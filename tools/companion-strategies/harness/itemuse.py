#!/usr/bin/env python3
"""itemuse.py <rig> [--since 'YYYY-MM-DD HH:MM:SS'] [--minutes N]: what each companion used up,
from rAthena's own item log (picklog, type C = consumed; the rigs log everything). Potions,
gemstones, catalysts, arrows and traps, by companion; with Companion inventory on, that is what
the fight cost them.

A companion's char_id is 95000000 + its shell index (cp_companion_persistence). The time is the
database's clock (UTC on the rigs): take --since from `SELECT NOW()` before the fight, or use
--minutes."""
import argparse, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("rig")
ap.add_argument("--since")
ap.add_argument("--minutes", type=int, default=20)
a = ap.parse_args()

up = open(os.path.join(a.rig, "up.sh")).read()
db = re.search(r"--name (\S+-db)", up).group(1)


def sql(q):
    out = subprocess.run(["docker", "exec", "-i", db, "mariadb", "-uragnarok", "-pragnarok", "ragnarok",
                          "-N", "-B", "-e", q], capture_output=True, text=True)
    if out.returncode:
        sys.exit(out.stderr.strip())
    return [l.split("\t") for l in out.stdout.splitlines() if l]


since = f"'{a.since}'" if a.since else f"NOW() - INTERVAL {a.minutes} MINUTE"
names = {95000000 + int(i): n for i, n in sql("SELECT shell_index, name FROM cp_companion_persistence")}
rows = sql(f"SELECT char_id, nameid, -SUM(amount) FROM picklog WHERE type='C' AND time >= {since} "
           f"GROUP BY char_id, nameid ORDER BY char_id, 3 DESC")

# item names from the server's own tables, so the output says Blue_Gemstone, not 717
items = {}
rdir = os.path.join(a.rig, "rathena", "db", "pre-re")
for f in os.listdir(rdir):
    if f.startswith("item_db") and f.endswith(".yml"):
        for m in re.finditer(r"- Id: (\d+)\n\s+AegisName: (\S+)", open(os.path.join(rdir, f)).read()):
            items[int(m.group(1))] = m.group(2)

used = {}
for cid, nid, n in rows:
    used.setdefault(names.get(int(cid), cid), []).append(f"{items.get(int(nid), nid)} {n}")
for who, l in used.items():
    print(f"{who:6s} " + ", ".join(l))
