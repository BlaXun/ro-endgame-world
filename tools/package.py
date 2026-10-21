#!/usr/bin/env python3
"""Package this repository's mods as release assets for Ragnarok Offline.

    python3 tools/package.py                    check every mod; write dist/
    python3 tools/package.py --tag v1.2.0       the same, and refuse unless every mod is 1.2.0
    python3 tools/package.py --set-version 1.2.0
                                                raise every mod.json to 1.2.0 and stop

Each mod under mods/ becomes dist/<mod>-<version>.zip with the mod's folder at
the top, which is what the app's registry entry (`"asset": "<mod>-*.zip"`)
installs. The mods of one repository are released together under one tag, so
they always carry the same version. dist/notes.md is that version's section of
CHANGELOG.md, used as the release notes players read on the Updates tab.

The app refuses an archive over 50 MB, one that unpacks to more than 96 MB or
2000 files, and links; so does this, before anything is published.
Python 3, no packages.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS = ROOT / "mods"
DIST = ROOT / "dist"
SKIP = {"__pycache__", ".DS_Store"}
LIMIT_ZIP, LIMIT_UNPACKED, LIMIT_FILES = 50 << 20, 96 << 20, 2000
VERSION = re.compile(r'("version"\s*:\s*")([^"]*)(")')


def fail(msg):
    sys.exit(f"package.py: {msg}")


def mods():
    found = sorted(d for d in MODS.iterdir() if d.is_dir())
    if not found:
        fail("no mods under mods/")
    out = []
    for d in found:
        try:
            manifest = json.loads((d / "mod.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            fail(f"{d.name}/mod.json: {e}")
        if manifest.get("name") != d.name:
            fail(f"{d.name}/mod.json: name is {manifest.get('name')!r}, not the folder's")
        out.append((d, manifest))
    return out


def notes(version):
    """The CHANGELOG.md section headed `## <version>`."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(version)}[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m or not m[1].strip():
        fail(f"CHANGELOG.md has no section for {version}")
    return m[1].strip() + "\n"


def files_of(mod_dir):
    out = []
    for p in sorted(mod_dir.rglob("*")):
        if SKIP & set(p.relative_to(mod_dir).parts):
            continue
        if p.is_symlink():
            fail(f"{p.relative_to(ROOT)} is a link; the app refuses links")
        if p.is_file():
            out.append(p)
    return out


def package(mod_dir, version):
    files = files_of(mod_dir)
    unpacked = sum(p.stat().st_size for p in files)
    if len(files) > LIMIT_FILES or unpacked > LIMIT_UNPACKED:
        fail(f"{mod_dir.name}: {len(files)} files, {unpacked >> 20} MB unpacked; the app takes {LIMIT_FILES} and {LIMIT_UNPACKED >> 20} MB")
    zpath = DIST / f"{mod_dir.name}-{version}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            # a fixed date, so the same files always make the same archive
            info = zipfile.ZipInfo(f"{mod_dir.name}/{p.relative_to(mod_dir).as_posix()}", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    if zpath.stat().st_size > LIMIT_ZIP:
        fail(f"{zpath.name} is {zpath.stat().st_size >> 20} MB; the app takes {LIMIT_ZIP >> 20} MB")
    return zpath, len(files)


def main():
    ap = argparse.ArgumentParser(description="Package the mods as release assets.")
    ap.add_argument("--tag", help="the release tag, e.g. v1.2.0; every mod must carry its version")
    ap.add_argument("--set-version", metavar="X.Y.Z", help="write this version into every mod.json and stop")
    args = ap.parse_args()
    found = mods()

    if args.set_version:
        if not re.fullmatch(r"\d+(\.\d+)*", args.set_version):
            fail(f"not a version: {args.set_version}")
        for d, _ in found:
            p = d / "mod.json"
            text, n = VERSION.subn(lambda m: m[1] + args.set_version + m[3], p.read_text(encoding="utf-8"), count=1)
            if n != 1:
                fail(f"{d.name}/mod.json has no version")
            p.write_text(text, encoding="utf-8")
        print(f"every mod is now {args.set_version}; add a `## {args.set_version}` section to CHANGELOG.md")
        return

    versions = {m.get("version") for _, m in found}
    if len(versions) != 1 or None in versions:
        fail("the mods carry different versions: " + ", ".join(f"{d.name} {m.get('version')}" for d, m in found)
             + " (tools/package.py --set-version X.Y.Z)")
    version = versions.pop()
    if args.tag is not None and args.tag.lstrip("v") != version:
        fail(f"tag {args.tag} but the mods are {version}")

    names = {d.name for d, _ in found}
    for d, m in found:
        for dep in m.get("requires", {}).get("mods", []):
            if dep not in names:
                print(f"note: {d.name} needs {dep}, which is not in this repository")

    DIST.mkdir(exist_ok=True)
    for old in DIST.glob("*.zip"):
        old.unlink()
    (DIST / "notes.md").write_text(notes(version), encoding="utf-8")
    for d, _ in found:
        zpath, n = package(d, version)
        print(f"{zpath.relative_to(ROOT)}: {n} files, {zpath.stat().st_size >> 10} KB")


if __name__ == "__main__":
    main()
