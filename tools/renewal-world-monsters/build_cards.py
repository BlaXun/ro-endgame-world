#!/usr/bin/env python3
"""Renewal cards the converted monsters and bosses drop, made pre-renewal cards (phase 8 of the
level-175 run). build_monsters.py imports convert() for the cards its monsters drop and writes them
into renewal-world-cards (db/item_db.yml, the drops added on load by npc/renewal_world_card_drops.txt); run on its own,
this prints the per-card log and writes cards_compare.json beside it for the status page:

  build_cards.py --rathena ../../../rathena-level175 [--write]

The owner's rules (2026-10-17, RenewalToPreRenewal175LevelPlan.txt, phase 8): weaker rather than
stronger; no single-skill effects; build enablers are fine; every card checked for abuse; before
and after for every card. The owner's draft (CARD_REBALANCE_DRAFT.yml beside this script)
is a starting idea. How a card is made:

1. Start from the draft's script for the card.
2. Weaker rather than stronger: a bonus the renewal card also has takes the weaker of the two
   values (the draft's "Buff" verdicts do not raise a card above renewal's own numbers).
3. Held to pre-renewal's own cards: a bonus a pre-renewal card of the same slot also gives is at
   most the most any of those gives (the same bonus with the same arguments; MVP cards against
   MVP cards' values, others against others).
4. Single-skill bonuses stay on their skill at a third of their value, as on the gear
   (build_equipment.scaled_skill; the owner, 2026-10-18). Before that they became broad stand-ins.
5. The abuse check (ABUSE below) flags each risk it finds; flagged effects are cut to a safe value
   where a rule says how (status immunity at most 50 %, reflect at most 10 %, drain at most 5 %
   chance), and every flag goes on the review list and the status page.

cards.csv (beside this script) overrides a card: AegisName,Script,note (Script replaces whole).
"""
import argparse, csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DRAFT = os.path.join(HERE, "CARD_REBALANCE_DRAFT.yml")
sys.path.insert(0, HERE)
import build_equipment as be
# Bonuses pre-renewal has as well (doc/item_bonus.txt), kept as they are on cards.
be.KEEP |= {"bMagicAddSize", "bIgnoreDefRaceRate", "bCriticalAddRace", "bAddEffWhenHit", "bSPDrainValue", "bHPDrainValue",
            "bHPGainValue", "bSPGainValue", "bBreakWeaponRate", "bBreakArmorRate", "bNoCastCancel", "bAutoSpellOnSkill",
            "bMagicAddEle", "bAddEff", "bCritAtkRate", "bMagicAddRace", "bSubSize", "bAddDamageClass"}
# Bonuses whose numbers the two eras count on different scales: no "weaker of draft and renewal" for them.
ERA_SCALED = ("bDef", "bMdef", "bDef2", "bMdef2")

# What may be abused, and how far it may go (owner, 2026-10-17: stacking, combinations, chains,
# uncapped scaling, immunities and reflects, endless sustain, bosses and the economy).
ABUSE = [
    (r"bResEff,\w+,(\d+)", "status resistance", lambda v: v > 5000, "at most 50 % per card (four would make a wearer immune)", 5000),
    (r"bSubEle,Ele_\w+,(\d+)", "element resistance", lambda v: v > 30, "at most 30 % per card", 30),
    (r"bSubRace,RC_\w+,(\d+)", "race resistance", lambda v: v > 30, "at most 30 % per card", 30),
    (r"b(?:Short|Long)WeaponDamageReturn,(\d+)", "damage reflect", lambda v: v > 10, "at most 10 %", 10),
    (r"bMagicDamageReturn,(\d+)", "magic reflect", lambda v: v > 10, "at most 10 %", 10),
    (r"b(?:HP|SP)DrainRate,(\d+),", "drain chance", lambda v: v > 50, "at most 5 % chance", 50),
    (r"bIgnore(?:Mdef|Def)(?:Race|Class|Ele)\w*,\w+,(\d+)|bIgnore(?:Mdef|Def)(?:Race|Class|Ele)\w*,\w+", "defence ignored", None, "kept, flagged", None),
    (r"bAddClass,Class_Boss,(\d+)", "damage against bosses", lambda v: v > 20, "at most 20 %", 20),
    (r"autobonus|bAutoSpell", "autocast or autobonus", None, "kept, flagged: chains with other cards", None),
    (r"getrefine|readparam|BaseLevel|JobLevel|getskilllv", "scales with refine, stats or level", None, "kept, flagged: uncapped scaling", None),
    (r"bNoCastCancel|bNoGemStone|bIntravision|bNoKnockback|bNoSizeFix|bNoWalkDelay", "special flag", None, "kept, flagged", None),
    (r"bDropAddRace|bDropAddClass|bAddMonsterDropItem|bGetZenyNum|bAddGetZenyNum|bExpAddRace|bExpAddClass", "drops, zeny or experience", None, "kept, flagged: economy", None),
]


def draft_entries():
    out = {}
    text = open(DRAFT, encoding="utf-8").read()
    for e in re.split(r"\n(?=  # \[)", text):
        m = re.search(r"^    AegisName: (\S+)", e, re.M)
        if not m:
            continue
        head = re.match(r"  # \[([^\]]+)\] ([^|]+)\|\s*([^|]+)\|\s*tier (\S+)", e)
        blk = e[e.index("  - Id:"):].rstrip("\n")
        out[m[1]] = {"verdict": head[1] if head else "", "slot": head[3].strip() if head else "", "tier": head[4] if head else "",
                     "block": blk, "script": be.script(blk)}
    return out


def key_val(line):
    """('bonus2 bAddRace,RC_Insect', 20) for a bonus line ending in a literal number, else None."""
    m = re.match(r"\s*(bonus\d?)\s+(\w+)((?:,[^,;]+)*?),(-?\d+)\s*;\s*$", line)
    return (f"{m[1]} {m[2]}{m[3]}", int(m[4])) if m else None


def effects(script):
    """What a card does, numbers aside: {bonus and its target: (sign, number or None)}. A condition on
    the wearer's class or weapon counts as an effect of its own, so a class card is not a copy."""
    out = {}
    for l in script.split("\n"):
        # an autobonus's own bonuses are temporary: they count as the autobonus, not as its bonuses
        m = re.search(r"\b(bonus\d?)\s+(\w+)\s*(?:,(.*?))?;", re.sub(r'"\{.*?\}"', '""', l))
        if m:
            args = [a.strip() for a in (m[3] or "").split(",") if a.strip()]
            key = m[2] + (" " + args[0].strip('"') if len(args) >= 2 else "")
            num = re.fullmatch(r"-?\d+", args[-1]) if args else None
            v = int(num[0]) if num else None
            if key in out and out[key][1] is not None:   # a second line of the same bonus adds to the first
                v = out[key][1] + (v or 0)
            out[key] = (1 if v is None or v >= 0 else -1, v)
        for k, pat in (("skill", r'\bskill\s+"?(\w+)'), ("autobonus", r"\b(autobonus\d?)\b")):
            for mm in re.finditer(pat, l):
                out[f"{k} {mm[1]}"] = (1, None)
        if re.search(r"BaseClass|\bClass\b|eaclass", l):
            out["condition: class " + " ".join(re.findall(r"\b(?:Job|EAJ)_\w+", l))] = (1, None)
        if re.search(r"getequipid|getiteminfo|\.@type\b", l) and re.search(r"\bW_\w+", l):
            out["condition: weapon " + " ".join(re.findall(r"\bW_\w+", l))] = (1, None)
        if re.search(r"readparam|BaseLevel", l):
            out["condition: stats or level"] = (1, None)
    return out


def too_similar(script, loc, pre_cards, mine=None):
    """The cards of the same slot this one copies (phase 9): the same effects with the same signs ("same
    effects as"), a part of one card's effects with no number above it ("a weaker copy of"), or all of a
    pre-renewal card's effects at its numbers or more plus at most as many again ("makes it obsolete")."""
    e = effects(script)
    if not e:
        return []
    found = []
    for other, (oloc, oe) in (mine or pre_cards).items():
        if oloc != loc or not oe:
            continue
        # all of a pre-renewal card and a little more: that card would never be slotted again
        if set(oe) < set(e) and 2 * len(oe) >= len(e) and all(e[k][0] == oe[k][0] for k in oe) and not mine \
                and all(e[k][1] is not None and oe[k][1] is not None and abs(e[k][1]) >= abs(oe[k][1]) for k in oe):
            found.append(f"all of {other} and more (makes it obsolete)")
            continue
        if not set(e) <= set(oe) or any(e[k][0] != oe[k][0] for k in e):
            continue
        if set(e) == set(oe):
            found.append(f"same effects as {other}")
        elif all(e[k][1] is not None and oe[k][1] is not None and abs(e[k][1]) <= abs(oe[k][1]) for k in e):
            found.append(f"a weaker copy of {other}")
    return found


def pre_cards_by_slot(pre_b):
    return {a: (",".join(be.sub(b, "Locations")), effects(be.script(b))) for a, b in pre_b.items()
            if be.field(b, "Type") == "Card" and be.sub(b, "Locations")}


def pre_card_caps(pre_b):
    """{(location, mvp?, key): the most a pre-renewal card gives}."""
    caps = {}
    for a, b in pre_b.items():
        if be.field(b, "Type") != "Card":
            continue
        loc = ",".join(be.sub(b, "Locations"))
        mvp = "MVP" in (be.field(b, "Name") or "") or bool(re.search(r"Class_Boss|bonus bAllStats", be.script(b)))
        for l in be.script(b).split("\n"):
            kv = key_val(l)
            if kv and kv[1] > 0:   # the most a pre-renewal card gives; drawbacks are not caps
                k = (loc, mvp, kv[0])
                caps[k] = max(caps.get(k, kv[1]), kv[1])
    return caps


def convert(rathena, names, overrides=None):
    re_b, pre_b = be.blocks(rathena, "re"), be.blocks(rathena, "pre-re")
    if not be.SKILLS:
        be.SKILLS.update(be.load_skills(rathena))
    if not be.PRE_SKILLS:
        be.PRE_SKILLS.update(re.findall(r"^    Name: (\S+)", open(f"{rathena}/db/pre-re/skill_db.yml", encoding="utf-8").read(), re.M))
    caps = pre_card_caps(pre_b)
    pre_cards = pre_cards_by_slot(pre_b)
    draft = draft_entries()
    overrides = overrides if overrides is not None else read_overrides()
    out = {}
    for name in sorted(names):
        d = draft.get(name)
        rb = re_b.get(name)
        if not d or not rb or name in pre_b:
            continue
        log, review, flags = [], [], []
        loc = ",".join(be.sub(d["block"], "Locations"))
        mvp = d["tier"] == "MVP"
        # A card whose renewal effect is a bonus to single skills keeps those bonuses (scaled, step 4;
        # the owner, 2026-10-18): the draft's own lines stay, its stand-ins for the skill bonuses
        # (bonuses renewal's card does not have) go, and renewal's skill lines are added with the
        # conditions around them.
        base, other = d["script"], be.script(rb)
        scalable = [m for m in re.finditer(r"\b(bonus\d?)\s+(bSkill\w+)((?:,[^;]*)?);", other) if be.scaled_skill(m[1], m[2], m[3])]
        if scalable and not overrides.get(name, {}).get("Script"):
            def bkey(l):   # the bonus and its target (a race, a skill), not its number
                m = re.search(r"\bbonus\d?\s+(\w+)\s*(?:,([^;]*))?;", l)
                args = (m[2] or "").split(",") if m else []
                return m and (m[1], args[0].strip() if len(args) >= 2 else "")
            have = {bkey(l) for l in other.split("\n") if bkey(l)}
            keep = []
            for l in base.split("\n"):
                k = bkey(l)
                if k and k not in have and k[0] != "bMatk":
                    log.append(f"draft stand-in dropped, renewal's skill bonus kept instead: {l.strip()}")
                    l = re.sub(r"\bbonus\d?\s+\w+[^;]*;", ".@_removed = 1;", l)
                keep.append(l)
            skill = [l if not bkey(l) or bkey(l)[0].startswith("bSkill") else re.sub(r"\bbonus\d?\s+\w+[^;]*;", ".@_removed = 1;", l)
                     for l in other.split("\n")]
            base = "\n".join(keep) + "\n" + "\n".join(skill)
        ren = {kv[0]: kv[1] for kv in (key_val(l) for l in other.split("\n")) if kv}
        lines = []
        # Flat MATK on a card becomes a MATK rate of a tenth (10 -> 1 %): pre-renewal's cards give
        # MATK as a rate, and the gear's twentieth would turn a card's 10 into nothing.
        draft_script = re.sub(r"bonus bMatk,(\d+);", lambda m: f"bonus bMatkRate,{max(1, round(int(m[1]) / 10))};", base)
        if draft_script != base and "bonus bMatk," in d["script"]:
            log.append("flat MATK made a MATK rate of a tenth")
        ren = {("bonus bMatkRate" if k == "bonus bMatk" else k): (max(1, round(v / 10)) if k == "bonus bMatk" else v) for k, v in ren.items()}
        if "// MANUAL" in draft_script:
            flags.append("the draft marks it for a redesign by hand: kept as the draft has it")
        # A bonus line with numbers anywhere (a status chance before its flags, two values): the
        # same line in renewal's card, numbers aside, gives the weaker number in each place.
        shape = lambda x: re.sub(r"-?\d+", "#", " ".join(x.split()))
        ren_lines = {shape(x): [int(n) for n in re.findall(r"-?\d+", x)] for x in other.split("\n")
                     if re.search(r"\bbonus\d?\s", x)}
        def weaker_everywhere(l):
            sh, nums = shape(l), [int(n) for n in re.findall(r"-?\d+", l)]
            r = ren_lines.get(sh)
            if not r or len(r) != len(nums) or any(b in l for b in ERA_SCALED) or key_val(l):
                return l
            new = [min(a, b) for a, b in zip(nums, r)]
            if new == nums:
                return l
            it = iter(new)
            out = re.sub(r"-?\d+", lambda m: str(next(it)), l)
            log.append(f"weaker of draft and renewal: {' '.join(l.split())} -> {' '.join(out.split())}")
            return out
        for l in draft_script.split("\n"):
            l = weaker_everywhere(l)
            kv = key_val(l)
            if kv:
                k, v = kv
                nv = v
                if k in ren and k.split()[1].split(",")[0] not in ERA_SCALED and ((v > 0 and ren[k] < v) or (v < 0 and ren[k] < v)):
                    nv = ren[k]
                    log.append(f"weaker of draft and renewal: {k},{v} -> {nv}")
                cap = caps.get((loc, mvp, k))
                if cap is not None and nv > 0 and nv > cap:
                    log.append(f"held to pre-renewal's cards of the slot: {k},{nv} -> {cap}")
                    nv = cap
                if nv != v:
                    l = re.sub(r"-?\d+(\s*;\s*)$", str(nv) + r"\1", l)
            lines.append(l)
        conv = be.convert_script("\n".join(lines), log)
        o = overrides.get(name, {})
        if o.get("Script"):
            conv = o["Script"].replace("\\n", "\n")
            log.append(f"override: {o.get('note', '')}")
        for pat, what, too_much, how, cap in ABUSE:
            for m in re.finditer(pat, conv):
                val = int(m[1]) if m.lastindex and m[1] else None
                if too_much and val is not None and too_much(val):
                    conv = conv.replace(m[0], m[0][: m.start(1) - m.start(0)] + str(cap) + m[0][m.end(1) - m.start(0):])
                    flags.append(f"{what}: {val} -> {cap} ({how})")
                elif not too_much:
                    flags.append(f"{what}: {how}")
        blk = re.sub(r"^    Script: \|\n(?:      .*\n?|\s*\n)+", "", d["block"], flags=re.M).rstrip("\n")
        if conv.strip():
            ls = conv.split("\n")
            base = min((len(x) - len(x.lstrip()) for x in ls if x.strip()), default=0)
            blk += "\n    Script: |\n" + "\n".join("      " + x[base:] if x.strip() else "" for x in ls)
        out[name] = {"block": blk, "log": log, "flags": sorted(set(flags)), "verdict": d["verdict"], "slot": d["slot"], "tier": d["tier"],
                     "renewal": be.script(rb), "draft": d["script"], "after": conv, "loc": loc,
                     "similar": too_similar(conv, loc, pre_cards)}
    # The converted cards against each other: two new cards of a slot doing the same thing.
    mine = {n: (c["loc"], effects(c["after"])) for n, c in out.items()}
    for n, c in out.items():
        c["similar"] += [f"{x} (converted)" for x in too_similar(c["after"], c["loc"], None, {k: v for k, v in mine.items() if k != n})]
    return out


def read_overrides():
    p = os.path.join(HERE, "cards.csv")
    return {r["AegisName"]: r for r in csv.DictReader(open(p, encoding="utf-8"))} if os.path.exists(p) else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rathena", required=True)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    import build_monsters
    build_monsters.build(a.rathena)
    res = convert(a.rathena, build_monsters.CARD_NAMES)
    for n, c in res.items():
        print(f"== {n} [{c['verdict']}] {c['slot']} {c['tier']}")
        for l in c["log"] + [f"FLAG: {x}" for x in c["flags"]] + [f"SIMILAR: {x}" for x in c["similar"]]:
            print("   ", l)
    print(f"{len(res)} cards, {sum(1 for c in res.values() if c['flags'])} with abuse flags, "
          f"{sum(1 for c in res.values() if c['similar'])} too similar to another card")
    if a.write:
        comp = [{"card": n, "verdict": c["verdict"], "slot": c["slot"], "tier": c["tier"], "renewal": c["renewal"], "draft": c["draft"],
                 "after": c["after"], "log": c["log"], "flags": c["flags"], "similar": c["similar"], "drops": build_monsters.CARD_SOURCES.get(n, [])} for n, c in res.items()]
        json.dump(comp, open(os.path.join(HERE, "cards_compare.json"), "w"), indent=1)
        print("wrote cards_compare.json")


if __name__ == "__main__":
    main()
