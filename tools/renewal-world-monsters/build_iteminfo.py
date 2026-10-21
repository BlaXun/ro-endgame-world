#!/usr/bin/env python3
"""The client's names and descriptions for the items the renewal-world mods add (System/itemInfo.lua).

Pre-renewal's client item table has no entry for many renewal items and renewal's numbers in the
rest, while the converted gear and cards now do something else. A mod's System/itemInfo.lua is
added to the client's table (stack/src/assets/client_tables.rs), so each mod (renewal-world-monsters,
-gear, -cards) ships an entry for every item in its db/item_db.yml:

- converted gear and cards: renewal's names and art, with a description written from the
  converted item (itemdesc.py: its script at every refine level), the sets it belongs to here
  (build_combos.py), and its type, weight and requirements;
- loot copied from renewal as it is: renewal's entry unchanged.

build_monsters.py calls build() once a mod; the translation is ROenglishRE's Renewal itemInfo.lua from the
pinned vendor/ROenglishRE.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
# the ragnarokoffline.app checkout, for vendor/ROenglishRE: RO_APP, or the one beside this repository
APP = os.environ.get("RO_APP") or os.path.normpath(os.path.join(HERE, "../../../ragnarokoffline.app"))
TRANSLATION = "Translation/Renewal/SystemEN/LuaFiles514/itemInfo.lua"
RULE = "_______________________"

WEAPON_TYPES = {"Dagger": "Dagger", "1hSword": "One-Handed Sword", "2hSword": "Two-Handed Sword", "1hSpear": "One-Handed Spear",
                "2hSpear": "Two-Handed Spear", "1hAxe": "One-Handed Axe", "2hAxe": "Two-Handed Axe", "Mace": "Mace",
                "2hMace": "Two-Handed Mace", "Staff": "Staff", "2hStaff": "Two-Handed Staff", "Bow": "Bow", "Knuckle": "Knuckle",
                "Musical": "Musical Instrument", "Whip": "Whip", "Book": "Book", "Katar": "Katar", "Revolver": "Revolver",
                "Rifle": "Rifle", "Gatling": "Gatling Gun", "Shotgun": "Shotgun", "Grenade": "Grenade Launcher",
                "Huuma": "Huuma Shuriken"}
SLOTS = [("Right_Hand", "Weapon"), ("Left_Hand", "Shield"), ("Armor", "Armor"), ("Garment", "Garment"), ("Shoes", "Footgear"),
         ("Both_Accessory", "Accessory"), ("Right_Accessory", "Accessory"), ("Left_Accessory", "Accessory"),
         ("Head_Top", "Headgear"), ("Head_Mid", "Headgear"), ("Head_Low", "Headgear")]
# A job flag on an item and the classes that wear it here (the third class after the transcendent one).
THIRD = {"Knight": "Rune Knight", "Crusader": "Royal Guard", "Wizard": "Warlock", "Sage": "Sorcerer", "Hunter": "Ranger",
         "BardDancer": "Minstrel, Wanderer", "Priest": "Arch Bishop", "Monk": "Sura", "Blacksmith": "Mechanic",
         "Alchemist": "Genetic", "Assassin": "Guillotine Cross", "Rogue": "Shadow Chaser", "StarGladiator": "Star Emperor",
         "SoulLinker": "Soul Reaper", "Gunslinger": "Gunslinger, Rebellion", "Ninja": "Ninja, Kagerou, Oboro",
         "KagerouOboro": "Kagerou, Oboro", "Rebellion": "Rebellion", "SuperNovice": "Super Novice", "Novice": "Novice"}


def translation_path():
    p = os.path.join(APP, "vendor/ROenglishRE", TRANSLATION)
    if os.path.exists(p):
        return p
    raise SystemExit("build_iteminfo: no vendor/ROenglishRE (scripts/vendor-fetch.sh ROenglishRE)")


def entries(path):
    """{id: entry text} of the translation's table. It is cp949 with a few stray bytes."""
    text = open(path, "rb").read().decode("cp949", errors="replace").replace("\r\n", "\n")
    out = {}
    for m in re.finditer(r"^\t\[(\d+)\] = \{", text, re.M):
        i, depth, in_str = m.end(), 1, False
        while depth:
            c = text[i]
            if in_str:
                if c == "\\":
                    i += 1
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c in "{}":
                depth += 1 if c == "{" else -1
            i += 1
        out[int(m[1])] = text[m.start():i]
    return out


def field(block, k):
    m = re.search(rf"^    {k}: (.+)$", block, re.M)
    return m[1].strip() if m else None


def flags(block, k):
    m = re.search(rf"^    {k}:\n((?:      .*\n?)+)", block, re.M)
    return re.findall(r"(\w+): true", m[1]) if m else []


def script(block):
    m = re.search(r"^    Script: \|\n((?:      .*\n?|\s*\n)+)", block, re.M)
    return m[1] if m else ""


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def effect_lines(itemdesc, text):
    out, last = [], None
    for ctx, line in itemdesc.describe(text or ""):
        if ctx != last and ctx:
            out.append(f"^777777{ctx}:^000000")
        last = ctx
        out.append(("   " if ctx else "") + line)
    return out


def describe(block, renewal_entry, itemdesc, sets, names):
    """The description lines of a converted item or card."""
    lines = []
    old = re.search(r"\bidentifiedDescriptionName = \{(.*?)\n\t\t\}", renewal_entry or "", re.S)
    old = re.findall(r'"((?:[^"\\]|\\.)*)"', old[1]) if old else []
    flavour = old[:old.index(RULE)] if RULE in old else []
    if flavour and not any(re.search(r"[+-]\d|\d+ ?%|\^", l) for l in flavour):
        lines += flavour + [RULE]
    lines += effect_lines(itemdesc, script(block)) or ["No effect of its own."]
    for items, combo_script in sets:
        others = [names.get(i, i) for i in items if i != field(block, "AegisName")]
        lines += [RULE, "When equipped with " + ", ".join(f"^990099{n}^000000" for n in others) + ":"]
        lines += effect_lines(itemdesc, combo_script) or ["(no effect)"]
    lines.append(RULE)
    t, sub, loc = field(block, "Type"), field(block, "SubType"), flags(block, "Locations")
    if t == "Card":
        where = next((w for k, w in SLOTS if k in loc), "Equipment")
        lines += ["^0000CCType:^000000 Card", f"^0000CCCompound on:^000000 {where}"]
    elif t == "Weapon":
        lines.append(f"^0000CCType:^000000 {WEAPON_TYPES.get(sub, sub)}")
        if field(block, "Attack"):
            lines.append(f"^0000CCAttack:^000000 {field(block, 'Attack')}")
    else:
        where = " / ".join(dict.fromkeys(w for k, w in SLOTS if k in loc)) or "Armor"
        lines.append(f"^0000CCType:^000000 {where}")
        if field(block, "Defense"):
            lines.append(f"^0000CCDefense:^000000 {field(block, 'Defense')}")
    lines.append(f"^0000CCWeight:^000000 {int(field(block, 'Weight') or 0) // 10}")
    if field(block, "WeaponLevel"):
        lines.append(f"^0000CCWeapon Level:^000000 {field(block, 'WeaponLevel')}")
    if t != "Card":
        jobs = flags(block, "Jobs")
        third = any(c.startswith("Third") or c == "All_Third" for c in flags(block, "Classes"))
        who = "All jobs" if not jobs or "All" in jobs else ", ".join(
            THIRD.get(j, j) if third else re.sub(r"(?<=[a-z])(?=[A-Z])", " ", j) for j in jobs)
        lines += [RULE, "^0000CCRequirement:^000000"]
        if field(block, "EquipLevelMin"):
            lines.append(f"Base Level {field(block, 'EquipLevelMin')}")
        lines.append(who)
    return lines


def build(item_blocks, converted, combos, itemdesc):
    """System/itemInfo.lua for the mod's items. item_blocks: {aegis: yaml block}; converted: the
    aegis names written here from the converted item; combos: build_combos' compare list."""
    tr = entries(translation_path())
    names = {}
    for a, b in item_blocks.items():
        names[a] = field(b, "Name") or a
    sets = {}
    for c in combos:
        for alt in c["items"]:
            for i in alt:
                sets.setdefault(i, []).append((alt, c["after"]))
    out = ["-- Generated by tools/renewal-world-monsters/build_monsters.py (build_iteminfo.py) -- do not hand-edit.",
           "-- Names and art from ROenglishRE's renewal table; the converted gear and cards described as they are here.",
           "tbl = {"]
    missing = []
    for a, b in sorted(item_blocks.items(), key=lambda kv: int(re.match(r"  - Id: (\d+)", kv[1])[1])):
        iid = int(re.match(r"  - Id: (\d+)", b)[1])
        e = tr.get(iid)
        if e is None:
            missing.append(a)
            continue
        if a not in converted:
            out.append(e + ",")
            continue
        desc = describe(b, e, itemdesc, sets.get(a, []), names)
        body = "\n".join(f"\t\t\t{q(l)}," for l in desc).rstrip(",")
        e = re.sub(r"\bidentifiedDescriptionName = \{.*?\n\t\t\}", lambda _: "identifiedDescriptionName = {\n" + body + "\n\t\t}", e, count=1, flags=re.S)
        e = re.sub(r"(slotCount = )\d+", lambda m: m[1] + str(field(b, "Slots") or 0), e, count=1)
        out.append(e + ",")
    out[-1] = out[-1].rstrip(",")
    out.append("}")
    return "\n".join(out) + "\n", missing
