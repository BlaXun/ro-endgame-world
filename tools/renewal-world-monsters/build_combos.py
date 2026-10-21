#!/usr/bin/env python3
"""Renewal's set bonuses for the converted gear and cards (the owner, 2026-10-18: "let all come
over and scale down like the single-skill bonuses"). build_monsters.py imports convert() and writes
db/item_combos.yml of renewal-world-gear (the sets of gear and pre-renewal items) and of
renewal-world-cards (the sets of cards and pre-renewal items); run on its own, this prints each set and writes combos_compare.json
beside it for the status page:

  build_combos.py --rathena ../../../rathena-level175

A renewal set comes over when it holds at least one converted item or card and every piece of it
exists in this game (pre-renewal's tables or the renewal-world mods'); a set pre-renewal already has stays its
own. Its script goes through the gear's conversion (build_equipment.convert_script: renewal-only
bonuses translated or dropped, single-skill bonuses at a third), and then every other bonus is
scaled to a third as well, rounded toward zero but never to nothing. The card abuse check
(build_cards.ABUSE) flags what it would flag on a card.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_equipment as be

SCALE = 3
# Where the number that scales sits among a bonus's arguments (after its name); the last one otherwise.
VALUE_AT = {"bAutoSpell": 2, "bAutoSpellWhenHit": 2, "bAutoSpellOnSkill": 3, "bAddEff": 1, "bAddEff2": 1,
            "bAddEffWhenHit": 1, "bHPRegenRate": 0, "bSPRegenRate": 0, "bHPDrainRate": 1, "bSPDrainRate": 1}
NO_VALUE = {"bAtkEle", "bDefEle", "bNoCastCancel", "bNoGemStone", "bIntravision", "bNoKnockback",
            "bNoSizeFix", "bUnbreakableWeapon", "bUnbreakableArmor", "bNoWalkDelay"}


def combos(path):
    """[(alternatives: [[item, ...], ...], script)] of a combo table, comments left out."""
    text = re.sub(r"#[^\n]*", "", open(path, encoding="utf-8").read())
    out = []
    for blk in re.split(r"\n  - Combos:", text)[1:]:
        head, _, script = blk.partition("    Script: |\n")
        alts = [re.findall(r"^\s+- (\S+)\s*$", c, re.M) for c in re.split(r"- Combo:", head)[1:]]
        script = "\n".join(l[6:] if l.startswith("      ") else l for l in script.split("\n") if l.strip())
        out.append(([a for a in alts if a], script))
    return out


def scale_line(m, log):
    kind, name, args = m[1], m[2], m[3] or ""
    if name.startswith("bSkill") or name in NO_VALUE or not args:
        return m[0]   # skill bonuses are scaled already; flags have no number
    a = [x.strip() for x in args.lstrip(",").split(",")]
    i = min(VALUE_AT.get(name, len(a) - 1), len(a) - 1)
    v = a[i]
    if re.fullmatch(r"-?\d+", v):
        n = int(v)
        new = int(n / SCALE) or (1 if n > 0 else -1 if n < 0 else 0)
        a[i] = str(new)
    else:
        a[i] = f"({v})/{SCALE}"
    out = f"{kind} {name},{','.join(a)};"
    if out != " ".join(m[0].split()):
        log.append(f"a third: {' '.join(m[0].split())} -> {out}")
    return out


def scale_script(script, log):
    return re.sub(r"\b(bonus\d?)\s+(\w+)((?:,[^;\"]*)?);", lambda m: scale_line(m, log), script)


def convert(rathena, available, converted):
    """{"yaml": the mod's table, "compare": [...]} for the renewal sets this game can complete."""
    import build_cards   # its import widens be.KEEP to the bonuses pre-renewal's cards have
    be.KEEP.add("bIgnoreMdefRaceRate")
    if not be.SKILLS:
        be.SKILLS.update(be.load_skills(rathena))
    if not be.PRE_SKILLS:
        be.PRE_SKILLS.update(re.findall(r"^    Name: (\S+)", open(f"{rathena}/db/pre-re/skill_db.yml", encoding="utf-8").read(), re.M))
    pre_sets = {tuple(sorted(a)) for alts, _ in combos(f"{rathena}/db/pre-re/item_combos.yml") for a in alts}
    body, compare = [], []
    for alts, script in combos(f"{rathena}/db/re/item_combos.yml"):
        alts = [a for a in alts if set(a) & converted and all(i in available for i in a) and tuple(sorted(a)) not in pre_sets]
        if not alts:
            continue
        log = []
        # A flat MATK becomes a MATK rate of a tenth, as on the cards (build_cards.py).
        src = re.sub(r"bonus bMatk,(\d+);", lambda m: f"bonus bMatkRate,{max(1, round(int(m[1]) / 10))};", script)
        if src != script:
            log.append("flat MATK made a MATK rate of a tenth")
        after = scale_script(be.convert_script(src, log, standins=False), log)
        flags = []
        for pat, what, too_much, how, cap in build_cards.ABUSE:
            for m in re.finditer(pat, after):
                val = int(m[1]) if m.lastindex and m[1] else None
                if too_much and val is not None and too_much(val):
                    after = after.replace(m[0], m[0][: m.start(1) - m.start(0)] + str(cap) + m[0][m.end(1) - m.start(0):])
                    flags.append(f"{what}: {val} -> {cap} ({how})")
                elif not too_much:
                    flags.append(f"{what}: {how}")
        entry = ["  - Combos:"]
        for a in alts:
            entry.append("      - Combo:")
            entry += [f"          - {i}" for i in a]
        if after.strip():
            entry.append("    Script: |")
            entry += ["      " + l if l.strip() else "" for l in after.split("\n")]
        body.append(entry)
        compare.append({"items": alts, "renewal": script, "after": after, "log": log, "flags": sorted(set(flags))})
    return {"yaml": table(body), "compare": compare, "entries": body}


def table(entries):
    """A combo table of these entries (each a list of lines, as convert() returns them)."""
    return "\n".join(["Header:", "  Type: COMBO_DB", "  Version: 1", "", "Body:"] + [l for e in entries for l in e]) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rathena", required=True)
    a = ap.parse_args()
    import build_monsters
    build_monsters.build(a.rathena)
    res = build_monsters.COMBOS
    for c in res["compare"]:
        print(" | ".join(" + ".join(x) for x in c["items"]))
        for l in c["log"] + [f"FLAG: {f}" for f in c["flags"]]:
            print("   ", l)
    json.dump(res["compare"], open(os.path.join(HERE, "combos_compare.json"), "w"), indent=1)
    print(f"{len(res['compare'])} sets; wrote combos_compare.json")


if __name__ == "__main__":
    main()
