#!/usr/bin/env python3
"""Renewal equipment the converted monsters drop, turned into pre-renewal items.

PORTING_EQUIP.md (development directory) is the spec; this is its pipeline for the
level-175 run. build_monsters.py imports convert() for the equipment its monsters drop
and writes the result into renewal-world-gear's db/item_db.yml, the drops into its
npc/renewal_world_gear_drops.txt (added on load); run on its own,
this script prints the per-item log and writes the review list:

  build_equipment.py --rathena ../../../rathena-level175 [--write]

  --write   writes equipment_log.csv and EQUIPMENT_REVIEW.md beside this script

The rules, all taken from the items both eras' tables share (calibration, 1,920 pieces):
- Weapon ATK, weapon level, slots and equip level: as in renewal (the shared items keep
  them, ratio 1.0 throughout).
- Weapon MATK, which pre-renewal does not have: a MATK rate, as pre-renewal's own staves
  carry it (staves and books: 15 % below renewal MATK 140, 20 % to 279, 25 % from 280;
  other weapons: 10 % from 50, else 5 %).
- Armour DEF: renewal's DEF is on another scale, by slot (a shield's 120 is pre-renewal's
  5). The pre-renewal value is the median of the shared items of the same slot whose
  renewal DEF is nearest (the six nearest).
- Script bonuses: kept (stats, element / race / size / class modifiers, HP and SP,
  recovery, FLEE, critical, ATK and ASPD rates, resistances, autobonus); translated
  (bVariableCastrate -> bCastrate, a flat bMatk -> a MATK rate of a twentieth,
  bSPRegenRate -> bSPrecovRate); a skill-specific bonus stays on its skill at a third of its
  value (scaled_skill(); the owner, 2026-10-18: "keep that effect, but scale it down": damage
  at most +15 % a line, a fixed cast becomes after-cast delay as the fixed-cast rule has it).
  Before 2026-10-18 it became a smaller, broader stand-in
  (stand_in(): a physical skill's damage -> a third of it as melee or ranged damage, a magic
  skill's -> half of it as magic damage of its element, a cooldown or cast -> delay or cast
  rate, an SP cost -> SP rate; each capped), and what has no stand-in is dropped and logged:
  (bSkillAtk, bSkillCooldown, bSkillUseSP(rate), bSkillVariableCast, bSkillFixedCast,
  bSkillDelay) and bFixedCast* (no fixed cast in pre-renewal). A dropped line becomes a
  no-op assignment, so a braceless `if` keeps its shape.
- Classes: a third-class flag means the transcended third classes here (Third_Upper);
  baby and fourth-class flags are dropped.
- Power budget: no item may beat the best pre-renewal item of its kind by more than a
  step for its level: weapons against the best pre-renewal weapon of the same type
  (ATK, its 95th percentile, equip level 99 or less) times 1.05 at level 100, +3 % for
  each 10 levels above it; armour against the best of its slot the same way. Over the
  budget, the value is cut to it, a weapon's ATK rounded down to a ten: a best attempt, on the
  review list.
- An item with nothing left after the drops but its base values is converted all the
  same; if it was carried by its skill bonuses (a weapon whose ATK is below the budget's
  base, an armour piece with no bonus left), it is a best attempt: the review list says
  so, and equipment.csv can give it a replacement effect.

equipment.csv (beside this script) overrides any field per item, with a note:
  AegisName,Attack,Defense,MatkRate,Script,note
Script there replaces the converted script whole.
"""
import argparse, csv, os, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))

KEEP = {"bStr", "bAgi", "bVit", "bInt", "bDex", "bLuk", "bAllStats", "bMaxHP", "bMaxSP", "bMaxHPrate",
        "bMaxSPrate", "bHPrecovRate", "bSPrecovRate", "bFlee", "bFlee2", "bCritical", "bCritAtkRate",
        "bAtkRate", "bAspdRate", "bAspd", "bDelayrate", "bMdef", "bDef", "bHit", "bBaseAtk", "bAtkEle",
        "bDefEle", "bSubEle", "bSubRace", "bSubSize", "bSubClass", "bAddEle", "bAddRace", "bAddSize",
        "bAddClass", "bMagicAddEle", "bMagicAddRace", "bMagicAtkEle", "bResEff", "bAddEff", "bLongAtkRate",
        "bShortAtkRate", "bWeaponDamageRate", "bUnbreakableWeapon", "bUnbreakableArmor", "bSplashRange",
        "bUseSPrate", "bCastrate", "bMatkRate", "bHPDrainRate", "bSPDrainRate", "bIgnoreDefRace",
        "bIgnoreMdefRace", "bNoSizeFix", "bPerfectHide", "bNoKnockback", "bSpeedRate", "bSpeedAddRate",
        "bHealPower", "bHealPower2", "bAddItemHealRate", "bLongAtkDef", "bNearAtkDef", "bMagicDamageReturn",
        "bShortWeaponDamageReturn", "bLongWeaponDamageReturn", "bAutoSpell", "bAutoSpellWhenHit",
        "bCriticalLong", "bAtk", "bMatk2"}
DROP = {"bSkillAtk", "bSkillCooldown", "bSkillUseSP", "bSkillUseSPrate", "bSkillVariableCast",
        "bSkillFixedCast", "bSkillDelay", "bFixedCastrate", "bFixedCast", "bSkillFixedCastrate"}
TRANSLATE = {"bVariableCastrate": "bCastrate", "bSPRegenRate": "bSPrecovRate", "bHPRegenRate": "bHPrecovRate"}
STAVES = {"Staff", "2hStaff", "Book"}


def blocks(rathena, era):
    out = {}
    d = f"{rathena}/db/{era}"
    for f in sorted(os.listdir(d)):
        if not re.match(r"item_db.*\.yml$", f):
            continue
        for blk in re.split(r"\n(?=  - Id: )", open(os.path.join(d, f), encoding="utf-8").read()):
            m = re.search(r"^    AegisName: (\S+)", blk, re.M)
            if blk.startswith("  - Id: ") and m:
                out[m[1]] = blk.split("\n\n")[0].rstrip("\n")
    return out


def field(b, k):
    m = re.search(rf"^    {k}: (.+?)\s*$", b, re.M)
    return m[1] if m else None


def sub(b, k):
    m = re.search(rf"^    {k}:\n((?:      .*\n?)+)", b, re.M)
    return re.findall(r"(\w+): true", m[1]) if m else []


def script(b):
    m = re.search(r"^    Script: \|\n((?:      .*\n?|\s*\n)+)", b, re.M)
    return m[1].rstrip() if m else ""


class Calibration:
    """What the items both eras share say: DEF by slot, and the budgets."""
    def __init__(self, re_b, pre_b):
        self.def_pairs = {}
        for a, b in re_b.items():
            p = pre_b.get(a)
            if p and field(b, "Type") == "Armor" and field(b, "Defense") and field(p, "Defense"):
                self.def_pairs.setdefault(",".join(sub(b, "Locations")), []).append((int(field(b, "Defense")), int(field(p, "Defense"))))
        self.best_atk, self.best_def = {}, {}
        atk, dfn = {}, {}
        for a, p in pre_b.items():
            lv = int(field(p, "EquipLevelMin") or 1)
            if lv > 99:
                continue
            if field(p, "Type") == "Weapon" and field(p, "Attack"):
                atk.setdefault(field(p, "SubType"), []).append(int(field(p, "Attack")))
            if field(p, "Type") == "Armor" and field(p, "Defense"):
                dfn.setdefault(",".join(sub(p, "Locations")), []).append(int(field(p, "Defense")))
        for k, v in atk.items():
            self.best_atk[k] = sorted(v)[int(0.95 * (len(v) - 1))]
        for k, v in dfn.items():
            self.best_def[k] = sorted(v)[int(0.95 * (len(v) - 1))]

    def defense(self, loc, d):
        pairs = self.def_pairs.get(loc) or [x for k, v in self.def_pairs.items() if set(k.split(",")) & set(loc.split(",")) for x in v]
        if not pairs or d <= 0:
            return d
        near = sorted(pairs, key=lambda x: abs(x[0] - d))[:6]
        return max(1, round(statistics.median(p for _, p in near)))


def budget(best, lv):
    return round(best * (1.05 + 0.03 * max(0, lv - 100) / 10))


def matk_rate(subtype, matk):
    if subtype in STAVES:
        return 25 if matk >= 280 else 20 if matk >= 140 else 15
    return 10 if matk >= 50 else 5


SKILLS = {}   # AegisName -> (Type, Range, Element), from renewal's skill table; filled by convert()


def load_skills(rathena):
    out, cur = {}, None
    for line in open(f"{rathena}/db/re/skill_db.yml", encoding="utf-8"):
        m = re.match(r"^    Name: (\S+)", line)
        if m:
            cur = m[1]; out[cur] = {"Type": "", "Range": 1, "Element": "Neutral"}
            continue
        m = re.match(r"^    (Type|Range|Element): (\S+)", line)
        if m and cur:
            out[cur][m[1]] = int(m[2]) if m[1] == "Range" and m[2].lstrip("-").isdigit() else m[2]
    return out


# The owner (2026-10-18): single-skill effects stay, scaled down so they add a benefit without
# reading like "+50 % for skill x". A third of renewal's value; skill damage at most +15 % a line.
SKILL_SCALE = 3
SKILL_ATK_CAP = 15
SCALED = {"bSkillAtk", "bSkillCooldown", "bSkillUseSP", "bSkillUseSPrate", "bSkillVariableCast",
          "bSkillFixedCast", "bSkillDelay"}
PRE_SKILLS = set()


def scaled_skill(kind, name, args):
    """A bonus to one skill, kept on that skill at a third of its value. None when the skill does
    not exist in pre-renewal or the bonus has no pre-renewal form."""
    a = [x.strip() for x in args.lstrip(",").split(",", 1)]
    if name not in SCALED or len(a) < 2 or (PRE_SKILLS and a[0].strip('"') not in PRE_SKILLS):
        return None
    if a[0].strip('"').startswith("SU_"):   # the Summoner's skills: no class here has them
        return None
    sk, val = a[0], a[1]
    lit = int(val) if re.fullmatch(r"-?\d+", val.strip()) else None
    if name == "bSkillAtk":
        if lit is not None:
            v = max(-SKILL_ATK_CAP, min(SKILL_ATK_CAP, int(lit / SKILL_SCALE)))
            return f"bonus2 bSkillAtk,{sk},{v};" if v else None
        return f"bonus2 bSkillAtk,{sk},min({SKILL_ATK_CAP},({val})/{SKILL_SCALE});"
    if name == "bSkillFixedCast":
        # the fixed-cast rule: a fixed cast is three quarters after-cast delay here
        name, div = "bSkillDelay", SKILL_SCALE * 4 / 3
    else:
        div = SKILL_SCALE
    if lit is not None:
        v = int(lit / div)
        if name in ("bSkillCooldown", "bSkillVariableCast", "bSkillDelay"):
            v = int(v / 100) * 100 or (100 if lit > 0 else -100)   # a tenth of a second
        return f"bonus2 {name},{sk},{v};" if v else None
    return f"bonus2 {name},{sk},({val})/{int(div) if div == int(div) else 4};"


def stand_in(kind, name, args):
    """A bonus to one skill becomes a smaller, broader one of the same kind (the owner,
    2026-10-17: no single-skill boosts, but no blank gear either). None: no stand-in.
    Each stand-in line is capped: damage +10 %, delay, cast and SP -5 %."""
    a = [x.strip() for x in args.lstrip(",").split(",", 1)]
    if len(a) < 2:
        return None
    sk, val = a[0].strip('"'), a[1]
    info = SKILLS.get(sk, {})
    # A constant is worked out here, so the item reads "bonus bDelayrate,-5;", not a formula.
    lit = int(val) if re.fullmatch(r"-?\d+", val.strip()) else None
    def f(expr, fn):
        return str(fn(lit)) if lit is not None else expr
    if name == "bSkillAtk":
        if info.get("Type") == "Magic":
            ele = info.get("Element", "Neutral")
            ele = "Neutral" if ele in ("Weapon", "Endowed", "Random") else ele
            return f"bonus2 bMagicAtkEle,Ele_{ele},{f(f'min(10,({val})/2)', lambda v: min(10, int(v / 2)))};"
        rng = info.get("Range", 1)
        rng = rng if isinstance(rng, int) else 1
        return f"bonus {'bLongAtkRate' if abs(rng) >= 5 else 'bShortAtkRate'},{f(f'min(10,({val})/3)', lambda v: min(10, int(v / 3)))};"
    if name == "bSkillCooldown":
        return f"bonus bDelayrate,{f(f'max(-5,({val})/250)', lambda v: max(-5, int(v / 250)))};"
    if name == "bSkillVariableCast":
        return f"bonus bCastrate,{f(f'max(-5,({val})/250)', lambda v: max(-5, int(v / 250)))};"
    if name == "bSkillUseSP":
        return f"bonus bUseSPrate,{f(f'max(-5,-({val})/8)', lambda v: max(-5, -int(v / 8)))};"
    if name == "bSkillUseSPrate":
        return f"bonus bUseSPrate,{f(f'max(-5,-({val})/3)', lambda v: max(-5, -int(v / 3)))};"
    return None


def convert_script(text, log, standins=True, scale_skills=True):
    out, last_key = [], [None]
    for line in text.split("\n"):
        m = re.match(r"^(\s*)(bonus\d?)\s+(\w+)\s*(,.*)?;\s*(.*)$", line.strip() and line or "")
        if not m:
            m2 = re.search(r"\b(bonus\d?)\s+(b\w+)", line)
            if m2 and m2[2] in SCALED and scale_skills:
                # a skill bonus inside another line (an autobonus's script): scaled where it stands
                def sc(mm):
                    r = scaled_skill(mm[1], mm[2], mm[3].replace('\\"', '"'))
                    return r.replace('"', '\\"') if r and '\\"' in mm[0] else (r or ".@_removed = 1;")
                new = re.sub(r'\b(bonus\d?)\s+(bSkill\w+)((?:,[^;]*)?);', sc, line)
                log.append(f"scaled: {line.strip()} -> {new.strip()}")
                out.append(new)
                continue
            if m2 and m2[2] in DROP:
                log.append(f"dropped: {line.strip()}")
                out.append(re.sub(r"\bbonus\d?\s+b\w+[^;]*;", ".@_removed = 1;", line))
                continue
            out.append(line)
            continue
        ind, kind, name, args, rest = m[1], m[2], m[3], m[4] or "", m[5]
        rep = scaled_skill(kind, name, args) if scale_skills and name in SCALED else None
        if rep:
            log.append(f"scaled: {line.strip()} -> {rep}")
            out.append(f"{ind}{rep}")
            continue
        if name in DROP:
            rep = stand_in(kind, name, args) if standins else None
            key = rep and re.match(r"bonus\d?\s+\w+(,Ele_\w+)?", rep)[0]
            if rep and out and key == last_key[0] and out[-1].startswith(ind + key):
                # two skills of one item, one after the other, map to the same stand-in: once
                log.append(f"replaced: {line.strip()} -> (same stand-in as the line before, not added twice)")
                out.append(f"{ind}.@_removed = 1;")
                continue
            last_key[0] = key
            if rep:
                log.append(f"replaced: {line.strip()} -> {rep}")
                out.append(f"{ind}{rep}")
            else:
                log.append(f"dropped: {line.strip()}")
                out.append(f"{ind}.@_removed = 1;")
        elif name in TRANSLATE:
            log.append(f"translated: {name} -> {TRANSLATE[name]}")
            out.append(f"{ind}{kind} {TRANSLATE[name]}{args};")
        elif name == "bMatk" and kind == "bonus":
            log.append(f"translated: flat bMatk{args} -> MATK rate of a twentieth")
            out.append(f"{ind}bonus bMatkRate,({args[1:]})/20;")
        elif name in KEEP:
            out.append(line)
        else:
            log.append(f"UNKNOWN bonus kept for review: {line.strip()}")
            out.append(line)
    return "\n".join(out)


def convert(rathena, names, overrides=None):
    """{AegisName: (yaml block, log lines, review reason or None)} for the renewal items named."""
    re_b, pre_b = blocks(rathena, "re"), blocks(rathena, "pre-re")
    cal = Calibration(re_b, pre_b)
    if not SKILLS:
        SKILLS.update(load_skills(rathena))
    if not PRE_SKILLS:
        PRE_SKILLS.update(re.findall(r"^    Name: (\S+)", open(f"{rathena}/db/pre-re/skill_db.yml", encoding="utf-8").read(), re.M))
    overrides = overrides if overrides is not None else read_overrides()
    out = {}
    for name in sorted(names):
        b = re_b.get(name)
        if not b or name in pre_b:
            continue
        log, review = [], []
        t, subtype = field(b, "Type"), field(b, "SubType")
        lv = int(field(b, "EquipLevelMin") or 1)
        loc = ",".join(sub(b, "Locations"))
        new = b
        sc = script(b)
        o = (overrides if overrides is not None else {}).get(name, {}) if isinstance(overrides, dict) else {}
        # equipment.csv `Effect` (phase 7): the item's own effect in place of the stand-ins, added to
        # what the conversion keeps of its script.
        conv = convert_script(sc, log, standins=not o.get("Effect")) if sc else ""
        if o.get("Effect"):
            ind = min((len(l) - len(l.lstrip()) for l in conv.split("\n") if l.strip()), default=0)
            conv = (conv + "\n" if conv.strip() else "") + "\n".join(" " * ind + l for l in o["Effect"].replace("\\n", "\n").split("\n"))
            log.append(f"phase 7 effect: {o['Effect']} ({o.get('note', '')})")
        rest = [l for l in conv.split("\n") if re.search(r"\bbonus\d?\s+b\w+|autobonus", l)]
        if t == "Weapon":
            atk = int(field(b, "Attack") or 0)
            best = cal.best_atk.get(subtype)
            # Rounded down to a ten (the owner, 2026-10-17: 190, not 194), so the cut stays inside the budget.
            cap = budget(best, lv) // 10 * 10 if best else None
            if cap and atk > cap:
                review.append(f"ATK {atk} over the budget {cap} (best pre-renewal {subtype} {best}, level {lv}): cut to {cap}")
                atk = cap
                new = re.sub(r"^    Attack: \d+", f"    Attack: {atk}", new, flags=re.M)
            matk = field(b, "MagicAttack")
            if matk:
                rate = matk_rate(subtype, int(matk))
                new = re.sub(r"^    MagicAttack: \d+\n", "", new, flags=re.M)
                ind = re.match(r"\s*", conv)[0] if conv else ""
                conv = (f"{ind}bonus bMatkRate,{rate};\n" + conv).strip("\n") if conv else f"bonus bMatkRate,{rate};"
                log.append(f"MATK {matk} -> bMatkRate {rate}")
            if not rest and best and atk < round(best * 1.05):
                review.append(f"carried by its skill bonuses: nothing but ATK {atk} left (pre-renewal's best {subtype} {best})")
        elif t == "Armor":
            d = int(field(b, "Defense") or 0)
            pd = cal.defense(loc, d)
            best = cal.best_def.get(loc)
            cap = budget(best, lv) if best else None
            if cap and pd > cap:
                review.append(f"DEF {pd} over the budget {cap}: cut")
                pd = cap
            if d:
                new = re.sub(r"^    Defense: \d+", f"    Defense: {pd}", new, flags=re.M)
                log.append(f"DEF {d} -> {pd} (slot {loc})")
            if not rest:
                review.append("carried by its skill bonuses: no bonus left, only DEF")
        # Doram gear: the Summoner does not exist in this game. Its armour goes to every job,
        # its staves to the Mage line (a best attempt, on the review list).
        jobs = sub(b, "Jobs")
        if jobs and set(jobs) <= {"Summoner", "Spirit_Handler"}:
            to = ["All"] if t == "Armor" else ["Mage", "Wizard", "Sage"]
            new = re.sub(r"^    Jobs:\n(?:      .*\n?)+", "    Jobs:\n" + "".join(f"      {j}: true\n" for j in to), new, flags=re.M)
            review.append(f"Doram-only ({', '.join(jobs)}), a class this game does not have: given to {', '.join(to)}")
        # classes: transcended third classes only above 99
        cls = sub(b, "Classes")
        if cls:
            keep = [c for c in cls if c not in ("Baby", "Third_Baby", "Fourth", "All_Baby", "All_Third_Baby")]
            if any(c in ("Third", "All_Third") for c in keep) and "Third_Upper" not in keep:
                keep.append("Third_Upper")
            keep = [c for c in keep if c not in ("Third", "All_Third")] or ["Third_Upper"]
            new = re.sub(r"^    Classes:\n(?:      .*\n?)+", "    Classes:\n" + "".join(f"      {c}: true\n" for c in keep), new, flags=re.M)
        if re.search(r"pow\(|getrefine\(\)\s*\*|\.@r\s*\*", conv) and re.search(r"bBaseAtk|bMatkRate,\(\(", conv):
            review.append("its ATK or MATK grows with the refine on renewal's curve (up to the square of the refine): kept, check it at +10")
        o = overrides.get(name, {})
        for k in ("Attack", "Defense"):
            if o.get(k):
                new = re.sub(rf"^    {k}: \d+", f"    {k}: {o[k]}", new, flags=re.M)
                log.append(f"override {k} {o[k]}: {o.get('note', '')}")
        if o.get("MatkRate"):
            conv = re.sub(r"bonus bMatkRate,\d+;", f"bonus bMatkRate,{o['MatkRate']};", conv, count=1)
        if o.get("Script"):
            conv = o["Script"].replace("\\n", "\n")
            log.append(f"override script: {o.get('note', '')}")
            review = [r for r in review if not r.startswith(("carried", "its ATK or MATK"))] + [f"replacement effect: {o.get('note', '')}"]
        if any(l.startswith("replaced:") for l in log):
            review.append("skill-specific effects turned into broader stand-ins (see the log): check the numbers")
        if o.get("Effect"):
            review = [r for r in review if not r.startswith("skill-specific")] + [f"phase 7 effect: {o.get('note', '')}"]
        if any("UNKNOWN" in l for l in log):
            review.append("a bonus of unknown kind was kept as it was")
        new = re.sub(r"^    Script: \|\n(?:      .*\n?|\s*\n)+", "", new, flags=re.M).rstrip("\n")
        if conv.strip():
            lines = [l for l in conv.split("\n")]
            base = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
            body = "\n".join("      " + l[base:] if l.strip() else "" for l in lines)
            new += "\n    Script: |\n" + body
        out[name] = (new, log, review)
    return out


def read_overrides():
    p = os.path.join(HERE, "equipment.csv")
    if not os.path.exists(p):
        return {}
    return {r["AegisName"]: r for r in csv.DictReader(open(p, encoding="utf-8"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rathena", required=True)
    ap.add_argument("--names", help="comma-separated AegisNames (default: the equipment the mod's monsters and bosses drop)")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if a.names:
        names = a.names.split(",")
    else:
        sys.path.insert(0, HERE)
        import build_monsters
        build_monsters.build(a.rathena)
        names = build_monsters.EQUIPMENT_NAMES
    res = convert(a.rathena, names)
    rows = []
    for n, (blk, log, review) in res.items():
        print(f"== {n}: {'BEST ATTEMPT' if review else 'by rule'}")
        for l in log + [f"REVIEW: {r}" for r in review]:
            print("   ", l)
        rows.append({"AegisName": n, "how": "best attempt" if review else "rule", "log": " | ".join(log), "review": " | ".join(review)})
    print(f"{len(res)} items: {sum(1 for r in rows if r['how'] == 'rule')} by rule, {sum(1 for r in rows if r['how'] != 'rule')} best attempts")
    if a.write:
        with open(os.path.join(HERE, "equipment_log.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, ["AegisName", "how", "log", "review"]); w.writeheader(); w.writerows(rows)
        write_review(a.rathena, res, os.path.join(HERE, "EQUIPMENT_REVIEW.md"))
        write_compare(a.rathena, res, os.path.join(HERE, "equipment_compare.json"))
        print("wrote equipment_log.csv, EQUIPMENT_REVIEW.md")


def write_compare(rathena, res, path):
    """Every converted item, renewal against pre-renewal, for the run's status page."""
    import json
    re_b = blocks(rathena, "re")
    def vals(b):
        return {k: field(b, k) for k in ("Name", "Type", "SubType", "Attack", "MagicAttack", "Defense", "Slots",
                                          "WeaponLevel", "EquipLevelMin") if field(b, k)} | {
            "Jobs": sub(b, "Jobs"), "Classes": sub(b, "Classes"), "Script": script(b)}
    drops = {}
    if "build_monsters" in sys.modules:
        drops = getattr(sys.modules["build_monsters"], "EQUIPMENT_SOURCES", {})
    out = []
    for n, (blk, log, review) in sorted(res.items()):
        out.append({"item": n, "before": vals(re_b[n]), "after": vals(blk), "how": "best attempt" if review else "rule",
                    "why": review, "log": log, "drops": drops.get(n, [])})
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1)


def write_review(rathena, res, path):
    """Every best attempt: the renewal item, what the rules alone gave, what was done and why."""
    re_b = blocks(rathena, "re")
    plain = convert(rathena, [n for n, v in res.items() if v[2]], overrides={})
    def shown(b):
        keep = [l for l in b.split("\n") if re.match(r"    (Attack|MagicAttack|Defense|Slots|WeaponLevel|EquipLevelMin|SubType):", l)]
        sc = script(b)
        return "\n".join(keep + (["    Script:"] + sc.split("\n") if sc else []))
    out = ["# Equipment review list", "",
           "Generated by `build_equipment.py --write`. Every renewal item the converted monsters and bosses",
           "drop that the rules alone could not settle: its renewal values, what the rules gave, what was",
           "done instead and why (PORTING_EQUIP.md; the rules are in the script's header). Overrides are in",
           "`equipment.csv`. Items converted by rule alone are in `equipment_log.csv`.", ""]
    for n, (blk, log, review) in sorted(res.items()):
        if not review:
            continue
        out += [f"## {n}", "", "Why: " + "; ".join(review), "", "Renewal:", "```", shown(re_b[n]), "```",
                "Rules alone:", "```", shown(plain[n][0]), "```", "Converted:", "```", shown(blk), "```", ""]
    open(path, "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    main()
