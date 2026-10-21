#!/usr/bin/env python3
"""Build the renewal-world monster mods from rAthena's renewal tables.

Renewal-only monsters have no pre-renewal stats: renewal tuned them for its
own damage formulas and for characters past level 99. This script gives them
pre-renewal numbers by comparing them with the monsters both eras share at the
top of pre-renewal's range, and writes their spawns.

    python3 build_monsters.py              show the conversion, write nothing
    python3 build_monsters.py --write      write the five mods' tables and spawns
    python3 build_monsters.py --check      fail if any of them is stale

One run writes five mods (mods/; their mod.json and README.md are kept by hand):

  renewal-world-monsters  the ordinary monsters: mob_db, mob_skill_db, spawns (the quest
                          areas' in npc/when/quest_areas/), and the etc and usable loot
                          copied from renewal (item_db, System/itemInfo.lua). Its Drops
                          hold everything but the converted equipment and cards.
  renewal-world-minibosses  the minibosses (kind() or is_boss() but not an MVP) a map
                          spawns, and what such a spawn summons or hatches into (the gold
                          Scaraba eggs and the gold Scarabas), with their spawn lines.
  renewal-world-mvps      the MVPs and the monsters only they summon, with their spawn
                          lines (a boss line: a boss, or boss_monster) and MvpDrops. It
                          requires the minibosses mod when an MVP summons a miniboss (the
                          Gold Queen Scaraba her gold Scarabas; the build checks).
  renewal-world-gear      the converted equipment (item_db), renewal's sets of it and
                          pre-renewal items (item_combos.yml), their client entries, and
                          npc/renewal_world_gear_drops.txt: on load it adds each drop
                          with addmonsterdrop, at mob_db's rate and steal protection,
                          to every monster of it that is loaded (bosses: with their mod on).
  renewal-world-cards     the same for the converted cards and the card sets.

The build fails when an MVP reward (MvpDrops) is a converted item or card (addmonsterdrop
adds only drops), when a set mixes converted equipment and cards, and when a monster's
drops would pass rAthena's MAX_MOB_DROP with the added ones.

monster_maps.csv  the maps that get monsters, and optionally the band (bands.csv)
                  all their monsters are converted in. Every renewal spawn on them is
                  copied, except champion monsters and bosses (minibosses and
                  MVPs, stock or renewal-only): those need a test of their own
                  and are not added yet. A monster pre-renewal already has
                  keeps its pre-renewal stats; one it lacks is converted here.
                  BALANCING.md has the rules this follows.
prere_unfair.csv  the pre-renewal monsters a level-99 Lord Knight in plain armour
                  cannot survive for 3 seconds (measured on the test server).
                  They are left out of the fair tier.
monsters.csv      optional per-monster overrides: AegisName, then any of the
                  columns Level, Hp, Attack, Attack2, Defense, MagicDefense,
                  Str, Agi, Vit, Int, Dex, Luk, BaseExp, JobExp, AttackDelay,
                  AttackMotion. An empty cell
                  keeps the computed value; a note column is for the reader.
                  The BaseExp and JobExp there come from party fight tests:
                  tools/companion-strategies/README.md says how.

The anchors are the monsters both eras have, at pre-renewal level 101 or more,
that give experience and are not bosses: the Splendide and Manuk monsters,
Rata and Duneyrr. Pre-renewal has nothing ordinary above them. For each anchor
the script knows the renewal stats and the pre-renewal stats, and so:

  - Hp, BaseExp, JobExp and Attack are amounts, and scale: the renewal value
    times the anchors' median of (pre-renewal / renewal). Attack2 is the top of
    the attack range in pre-renewal but magic attack in renewal, so it is
    Attack times the anchors' median of (pre-renewal Attack2 / Attack).
  - Level keeps the monster's rank among the anchors: a renewal level higher
    than 70% of the anchors' renewal levels gets the level at 70% of their
    pre-renewal levels, so it stays within their 101-114.
  - Defense, MagicDefense and the six stats keep the monster's rank among its
    renewal peers (ordinary renewal monsters within PEER_LEVELS of its level),
    and take the value at that rank among the fair tier: the
    ordinary pre-renewal monsters of level 70-99, less those in
    prere_unfair.csv. Read off the anchors instead, they gave MDEF 80 and high
    INT, and with pre-renewal's soft MDEF (INT + VIT/2) on top a level-10
    Jupitel Thunder did 12 damage to Miming.
    Agi and Dex are the exception: pre-renewal FLEE is level + AGI and HIT is
    level + DEX, and these monsters keep their higher level. So FLEE and HIT
    take their rank among the fair tier, and Agi and Dex are what is left
    after the level. Read off the fair tier as plain stats, Angra Mantis had
    FLEE 253 and a Lord Knight missed it every time. FLEE also stops at
    FLEE_CAP of the fair tier: at its very top, three Angra Mantises outlasted
    a party with Quagmire and Ankle Snare.
  - Everything else (size, race, element, speeds, AI, modes) is copied.

That alone lands a monster beside the Splendide ones, and those are not fair:
in the fight test a level-99 Lord Knight in plain armour dies to Naga, Cornus or
Luciola Vespa in under two seconds, too fast for a priest to heal. So two
factors scale the result down, toward Bloody Knight and Abysmal Knight, which
a party can take on:

  OFFENCE  multiplies Attack and Attack2. 0.2 puts one monster at about
           700-2,000 damage a second on that Lord Knight.
  TOUGHNESS multiplies Hp, and BaseExp and JobExp with it, so experience per HP
           stays what the anchors give: the reward follows the effort.

Change them, re-run --write, and fight-test again.

Drops and an MVP's rewards (MvpDrops): equipment and cards converted (build_equipment.py,
build_cards.py; in the gear and cards mods, added on load), the rest as renewal has it. Etc and
usable loot pre-renewal lacks is copied from renewal's item tables into renewal-world-monsters'
db/item_db.yml; a usable that casts a skill pre-renewal lacks fails the build, and one that opens
an item group pre-renewal lacks is left out.
Sets: renewal's set bonuses this game can complete, at a third (build_combos.py ->
db/item_combos.yml of the gear or cards mod). The client's names and descriptions of every item
a mod adds (build_iteminfo.py -> its System/itemInfo.lua, from the pinned vendor/ROenglishRE).
Skills: renewal's rows, except a skill pre-renewal does not have and a summon
that names no monster. A band in bands.csv may scale their levels with the
monster's level and cap their rates (the mid band does: renewal's are set for
renewal-sized HP).

--rathena (or RATHENA_DIR) points at the checkout; the default is the app's
vendor/rathena. Python 3, no packages. Nothing here runs in the game.
"""
import build_equipment
import build_cards
import argparse
import csv
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "../.."))
# the ragnarokoffline.app checkout: RO_APP, or the one beside this repository
APP = os.environ.get("RO_APP") or os.path.join(os.path.dirname(ROOT), "ragnarokoffline.app")
MODS_DIR = os.path.join(ROOT, "mods")
MAPS_TOOLS = os.path.join(APP, "registry/tools/renewal-world")   # maps.csv: the maps mod's
# The five mods this writes (folder names under mods/; mod.json and README.md are kept by hand):
MONSTERS = "renewal-world-monsters"   # the ordinary monsters, their spawns, and the etc/usable loot from renewal
MVPS = "renewal-world-mvps"           # the MVPs and the monsters only they summon
MINIS = "renewal-world-minibosses"    # the minibosses a map spawns (or hatches), and what they summon
GEAR = "renewal-world-gear"           # the converted equipment, its sets, and its drops (added on load)
CARDS = "renewal-world-cards"         # the converted cards, their sets, and their drops (added on load)
OUT_MOBS = "db/mob_db.yml"
OUT_SKILLS = "db/mob_skill_db.txt"
OUT_SPAWNS = {MONSTERS: "npc/renewal_world_monsters.txt", MVPS: "npc/renewal_world_mvps.txt",
              MINIS: "npc/renewal_world_minibosses.txt"}
# Spawns on the quest areas, loaded only while the mod's quest_areas setting is on
# (as build.py's gates and portals into them).
OUT_QUEST_SPAWNS = {MONSTERS: "npc/when/quest_areas/renewal_world_quest_monsters.txt",
                    MVPS: "npc/when/quest_areas/renewal_world_quest_mvps.txt",
                    MINIS: "npc/when/quest_areas/renewal_world_quest_minibosses.txt"}
OUT_ITEMS = "db/item_db.yml"
OUT_COMBOS = "db/item_combos.yml"   # renewal's sets for the converted gear or cards (build_combos.py)
OUT_ITEMINFO = "System/itemInfo.lua"   # the client's names and descriptions of the items above (build_iteminfo.py)
OUT_DROPS = {GEAR: "npc/renewal_world_gear_drops.txt", CARDS: "npc/renewal_world_card_drops.txt"}
# Every file the build may write into a mod: one it no longer writes is removed by --write (and is stale for --check).
OWNED = {MONSTERS: [OUT_MOBS, OUT_SKILLS, OUT_SPAWNS[MONSTERS], OUT_QUEST_SPAWNS[MONSTERS], OUT_ITEMS, OUT_COMBOS, OUT_ITEMINFO],
         MVPS: [OUT_MOBS, OUT_SKILLS, OUT_SPAWNS[MVPS], OUT_QUEST_SPAWNS[MVPS]],
         MINIS: [OUT_MOBS, OUT_SKILLS, OUT_SPAWNS[MINIS], OUT_QUEST_SPAWNS[MINIS]],
         GEAR: [OUT_ITEMS, OUT_COMBOS, OUT_ITEMINFO, OUT_DROPS[GEAR]],
         CARDS: [OUT_ITEMS, OUT_COMBOS, OUT_ITEMINFO, OUT_DROPS[CARDS]]}
# rAthena's MAX_MOB_DROP (src/map/mob.hpp): the drop slots of a monster, its mob_db Drops and the added ones together.
MAX_MOB_DROP = 10
# The monster skills whose mob_skill_db rows name monsters (cols 12-16): what a monster summons or turns into.
SUMMONS = ("NPC_SUMMONSLAVE", "NPC_CALLSLAVE", "NPC_SUMMONMONSTER", "NPC_METAMORPHOSIS", "NPC_TRANSFORMATION")
OUT_COMPARE = "@monster_compare.json"   # beside this script: renewal against converted, for the status page
OUT_CARDS = "@cards_left_out.csv"   # beside this script, not in the mod: cards pre-renewal lacks, for the later task
# Version: in rAthena's db/import-tmpl/item_db.yml.
ITEM_DB_VERSION = 3
# Version: in rAthena's db/import-tmpl/mob_db.yml.
MOB_DB_VERSION = 5

# The ladder: a monster of renewal level LADDER_MIN or more keeps its level (raised to
# LADDER_FLOOR, held at the cap), and stands on its step's reference within these bounds.
LADDER_MIN, LADDER_FLOOR, LEVEL_CAP = 40, 70, 175
CARD_NAMES, CARD_SOURCES = set(), {}   # phase 8: the cards converted by build_cards.py, and where each drops
EQUIPMENT_SOURCES = {}   # item -> ["MONSTER rate %", ...]
EQUIPMENT_NAMES = set()   # what the last build() converted, for build_equipment.py run on its own
COMBOS = {}   # the last build()'s sets, for build_combos.py run on its own
LADDER = []   # one row per monster on the ladder, written to ladder.csv beside this script
REL_HP, REL_ATTACK = (0.5, 1.75), (0.6, 1.4)
PEER_LEVELS = 10
# A boss's own heals, kept to when it is idle.
SELF_HEALS = ("AL_HEAL", "NPC_ALLHEAL", "NPC_HEALING")
# The fewest anchors a renewal-level window may hold before it widens.
MIN_ANCHORS = 30
# Stats pre-renewal adds the level to: FLEE = level + AGI, HIT = level + DEX.
LEVEL_BOUND = ("Agi", "Dex")
# FLEE stops at this share of the fair tier. At its top (Angra Mantis, 192) a party
# with Quagmire and Ankle Snare took one of three in three minutes.
FLEE_CAP = 0.75
SCALED = ("Hp", "BaseExp", "JobExp", "Attack")
FAIR_RANKED = ("Defense", "MagicDefense", "Str", "Agi", "Vit", "Int", "Dex", "Luk")
OVERRIDABLE = SCALED + ("Level", "Attack2", "AttackDelay", "AttackMotion") + FAIR_RANKED   # and HpScale, AttackScale
# Written in this order, as rAthena's own tables are.
FIELDS = ("AegisName", "Name", "JapaneseName", "Level", "Hp", "Sp", "BaseExp", "JobExp", "MvpExp",
          "Attack", "Attack2", "Defense", "MagicDefense", "Resistance", "MagicResistance",
          "Str", "Agi", "Vit", "Int", "Dex", "Luk", "AttackRange", "SkillRange", "ChaseRange",
          "Size", "Race", "RaceGroups", "Element", "ElementLevel", "WalkSpeed", "AttackDelay",
          "AttackMotion", "ClientAttackMotion", "DamageMotion", "DamageTaken", "GroupId",
          "Title", "Ai", "Class", "Modes")
# Renewal-only fields pre-renewal does not read, and DamageTaken: pre-renewal does read it
# (battle.cpp applies it in both modes), and six renewal bosses take 10 % of all damage with it
# (Dark Lord 1272, Nightmare Amon Ra, Spider Chariot, Bestia, Corrupted Dark Lord, the field
# Pitaya boss; RENEWAL_BOSS_TACTICS.md). A converted boss's HP comes from its step, so the field
# would make it ten times as tough on top: left out on purpose (phase 6 tunes the HP itself).
SKILL_SUBST = {"NPC_WIDESTONE2": "NPC_WIDESTONE", "NPC_HELLJUDGEMENT2": "NPC_HELLJUDGEMENT"}
RENEWAL_ONLY = {"Resistance", "MagicResistance", "DamageTaken"}
DROP_TYPES = {"Weapon", "Armor", "Card", "Shadowgear", "Petarmor"}
SPAWN_SKIP = re.compile(r"championmobs\.txt$")
SPAWN = re.compile(r"^(\S+?),[^\t]*\t(monster|boss_monster)\t([^\t]+)\t(\d+),")


def load_mobs(path):
    """id -> {field: value} for a rAthena mob_db.yml; drops as a list of dicts."""
    mobs, cur, key = {}, None, None
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        m = re.match(r"^  - Id: (\d+)\s*$", line)
        if m:
            cur = {"Id": int(m[1]), "Drops": [], "MvpDrops": [], "Modes": {}}
            mobs[cur["Id"]] = cur
            key = None
            continue
        if cur is None:
            continue
        m = re.match(r"^    (\w+):\s*(.*?)\s*$", line)
        if m:
            key = m[1]
            if m[2]:
                cur[key] = m[2]
            continue
        m = re.match(r"^      - Item: (\S+)", line)
        if m and key in ("Drops", "MvpDrops"):
            cur[key].append({"Item": m[1]})
            continue
        m = re.match(r"^        (\w+): (.*?)\s*$", line)
        if m and key in ("Drops", "MvpDrops") and cur[key]:
            cur[key][-1][m[1]] = m[2]
            continue
        m = re.match(r"^      (\w+): (.*?)\s*$", line)
        if m and key in ("Modes", "RaceGroups"):
            cur.setdefault(key, {})[m[1]] = m[2]
    return mobs


def load_item_types(rathena, era):
    types = {}
    d = f"{rathena}/db/{era}"
    for f in sorted(os.listdir(d)):
        if not re.match(r"item_db.*\.yml$", f):
            continue
        name = None
        for line in open(os.path.join(d, f), encoding="utf-8"):
            m = re.match(r"^    AegisName: (\S+)", line)
            if m:
                name = m[1]
                types[name] = "Etc"
            m = re.match(r"^    Type: (\S+)", line)
            if m and name:
                types[name] = m[1]
    return types


def load_item_blocks(rathena, era):
    """AegisName -> the item's entry in rAthena's item tables, as written there."""
    blocks = {}
    d = f"{rathena}/db/{era}"
    for f in sorted(os.listdir(d)):
        if not re.match(r"item_db.*\.yml$", f):
            continue
        text = open(os.path.join(d, f), encoding="utf-8").read()
        for blk in re.split(r"\n(?=  - Id: )", text):
            m = re.search(r"^    AegisName: (\S+)", blk, re.M)
            if blk.startswith("  - Id: ") and m:
                blocks[m[1]] = blk.split("\n\n")[0].rstrip("\n")
    return blocks


def load_skill_aegis(rathena, era):
    names = set()
    for line in open(f"{rathena}/db/{era}/skill_db.yml", encoding="utf-8"):
        m = re.match(r"^    Name: (\S+)", line)
        if m:
            names.add(m[1])
    return names


def load_skill_names(rathena, era):
    names = set()
    for line in open(f"{rathena}/db/{era}/skill_db.yml", encoding="utf-8"):
        m = re.match(r"^  - Id: (\d+)", line)
        if m:
            names.add(int(m[1]))
    return names


def num(mob, key):
    try:
        return int(mob.get(key, 0))
    except ValueError:
        return 0


def is_mvp(mob):
    """An MVP as rAthena counts one: the Mvp mode (its MVP experience may be missing)."""
    return "MvpExp" in mob or (mob.get("Modes") or {}).get("Mvp") == "true"


def is_boss(mob):
    return mob.get("Class") in ("Boss", "Guardian", "Battlefield", "Event") or "MvpExp" in mob


def rank_map(x, re_vals, pre_vals):
    """x's rank among re_vals, read back off pre_vals."""
    below = sum(v < x for v in re_vals) + 0.5 * sum(v == x for v in re_vals)
    q = below / len(re_vals)
    pre = sorted(pre_vals)
    pos = q * (len(pre) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(pre) - 1)
    return round(pre[lo] + (pre[hi] - pre[lo]) * (pos - lo))


def rank_cap(values, share):
    """The value at that share of a sorted list."""
    return values[min(len(values) - 1, int(share * (len(values) - 1)))]


def map_spawns(rathena, era):
    """{map: {monster id}} from an era's spawn files."""
    out = {}
    for dirpath, _, files in os.walk(f"{rathena}/npc/{era}/mobs"):
        for f in sorted(files):
            path = os.path.join(dirpath, f)
            if SPAWN_SKIP.search(path):
                continue
            for line in open(path, encoding="utf-8"):
                m = SPAWN.match(line)
                if m:
                    out.setdefault(m[1], set()).add(int(m[4]))
    return out


def skill_line(c):
    """A mob_skill_db row in words: skill and level, when, how often, on whom, on what condition."""
    cond = c[10] + (" " + c[11] if len(c) > 11 and c[11] else "")
    return (f"{c[1].split('@')[-1]} lv{c[4]}, {c[2]}, {int(c[5]) / 100:g} %, cast {int(c[6]) / 1000:g} s, "
            f"delay {int(c[7]) / 1000:g} s, on {c[9]}, when {cond}")


def boss_peer_correction(rathena, re_mobs, pre_mobs, kind):
    """How far a boss stands above the ordinary monsters of its own level (within 8 levels),
    pre-renewal's median over renewal's, per kind, and the most pre-renewal's go (90th
    percentile): {kind: {Hp, Attack, BaseExp: factor, cap_Hp, cap_Attack}}. For bosses on the
    ladder, which takes a monster's standing against its level, not its map."""
    rel = {}
    for era, mobs in (("re", re_mobs), ("pre-re", pre_mobs)):
        spawned = {i for ids in map_spawns(rathena, era).values() for i in ids}
        ords = [m for i, m in mobs.items() if i in spawned and not is_boss(m) and num(m, "BaseExp") > 0 and num(m, "Hp") >= 100]
        for i, m in mobs.items():
            k_ = kind(m)
            if i not in spawned or not k_ or num(m, "BaseExp") <= 1:
                continue
            peers = [o for o in ords if abs(num(o, "Level") - num(m, "Level")) <= 8]
            if len(peers) < 5:
                continue
            for k in ("Hp", "Attack", "BaseExp"):
                rel.setdefault((era, k_, k), []).append(num(m, k) / statistics.median(num(o, k) for o in peers))
    out = {}
    for k_ in ("mvp", "miniboss"):
        out[k_] = {k: statistics.median(rel[("pre-re", k_, k)]) / statistics.median(rel[("re", k_, k)]) for k in ("Hp", "Attack", "BaseExp")}
        for k in ("Hp", "Attack"):
            v = sorted(rel[("pre-re", k_, k)])
            out[k_]["cap_" + k] = v[int(0.9 * (len(v) - 1))]
    return out


def boss_correction(rathena, re_mobs, pre_mobs, kind):
    """How much more a boss is than the ordinary monsters on its map, pre-renewal over
    renewal, per kind: {kind: {Hp, Attack, BaseExp, JobExp: factor, Level: levels}}.

    For every boss that spawns on a map with two or more ordinary monsters, in each
    era, its HP (and attack, experience) over the median of theirs, and its level
    less theirs; the correction is pre-renewal's median over renewal's (the level's,
    the difference). Renewal's MVPs pay about 300 times their map, pre-renewal's 54."""
    rel = {}
    for era, mobs in (("re", re_mobs), ("pre-re", pre_mobs)):
        for mp, ids in map_spawns(rathena, era).items():
            ords = [mobs[i] for i in ids if i in mobs and not is_boss(mobs[i]) and num(mobs[i], "BaseExp") > 0]
            if len(ords) < 2:
                continue
            med = {k: statistics.median(num(o, k) for o in ords) for k in SCALED + ("Level",)}
            for i in ids:
                k_ = kind(mobs[i]) if i in mobs else None
                if not k_:
                    continue
                for k in SCALED:
                    if med[k] > 0:
                        rel.setdefault((era, k_, k), []).append(num(mobs[i], k) / med[k])
                rel.setdefault((era, k_, "Level"), []).append(num(mobs[i], "Level") - med["Level"])
    out = {}
    for k_ in ("mvp", "miniboss"):
        out[k_] = {k: statistics.median(rel[("pre-re", k_, k)]) / statistics.median(rel[("re", k_, k)])
                   for k in SCALED}
        out[k_]["Level"] = statistics.median(rel[("pre-re", k_, "Level")]) - statistics.median(rel[("re", k_, "Level")])
        # The most a pre-renewal boss of the kind stands above its map (its 90th percentile):
        # the cap for a boss on the ladder.
        for k in ("Hp", "Attack"):
            v = sorted(rel[("pre-re", k_, k)])
            out[k_]["cap_" + k] = v[int(0.9 * (len(v) - 1))]
    return out


def load_bands():
    """bands.csv: a band per row, or an error message."""
    out = []
    for row in read_csv("bands.csv"):
        try:
            lo, hi = map(int, row["renewal_levels"].split("-"))
            ak, av = row["anchors"].split(":")
            fk, fv = row["fair_tier"].split(":")
            a = list(map(int, av.split("-"))) + [0]
            f = list(map(int, fv.split("-"))) + [0]
            out.append({"name": row["band"], "lo": lo, "hi": hi, "anchor_kind": ak, "anchor_lo": a[0],
                        "anchor_hi": a[1], "fair_kind": fk, "fair_lo": f[0], "fair_hi": f[1],
                        "offence": float(row["offence"]), "toughness": float(row["toughness"]),
                        "skill_levels": row.get("skill_levels") or "keep",
                        "skill_rate_cap": int(row.get("skill_rate_cap") or 0),
                        "attack_speed": (row.get("attack_speed") or "keep").strip(),
                        "cap": float(row.get("cap") or 0)})
        except (KeyError, ValueError):
            return f"bands.csv: cannot read the row for {row.get('band')}"
        if ak not in ("pre", "renewal") or fk not in ("level", "around"):
            return f"bands.csv: {row['band']}: anchors are pre:<levels> or renewal:<window>, fair_tier level:<levels> or around:<window>"
    return out


def read_csv(name):
    path = os.path.join(MAPS_TOOLS if name == "maps.csv" else HERE, name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if any(v.strip() for v in r.values() if v)]


def mob_yaml(mob):
    out = [f"  - Id: {mob['Id']}"]
    for k in FIELDS:
        if k in RENEWAL_ONLY or k not in mob:
            continue
        v = mob[k]
        if isinstance(v, dict):
            if v:
                out.append(f"    {k}:")
                out += [f"      {a}: {b}" for a, b in v.items()]
        else:
            out.append(f"    {k}: {v}")
    for key in ("MvpDrops", "Drops"):
        if mob.get(key):
            out.append(f"    {key}:")
            for d in mob[key]:
                out.append(f"      - Item: {d['Item']}")
                out += [f"        {a}: {b}" for a, b in d.items() if a not in ("Item", "Index", "RandomOptionGroup")]   # no random options in pre-renewal
    return out


def drop_script(mod, kind, drops, item_id, blocks, head):
    """The NPC script that adds a mod's drops on load: [(mob id, AegisName, drop)] -> its text.

    Each monster's drops are added only while the monster is loaded (renewal-world-mvps may be off),
    so a missing one is skipped without a line in the log. The script logs how many it added, and an
    error naming any it could not add (a full monster: rAthena keeps MAX_MOB_DROP)."""
    name = lambda a: re.search(r"^    Name: (.*?)\s*$", blocks[a], re.M)[1].strip('"')
    out = [f"// {head.format(c='//')}",
           f"// The converted {kind} drops of the renewal-world monsters, with the rates and steal protection",
           "// renewal gives them, added on load (addmonsterdrop). A monster that is not loaded is skipped.",
           "", f"-\tscript\t{'rw_gear_drops' if kind == 'equipment' else 'rw_card_drops'}\t-1,{{", "OnInit:"]
    by_mob = {}
    for mid, aegis, d in drops:
        by_mob.setdefault((mid, aegis), []).append(d)
    for (mid, aegis), ds in sorted(by_mob.items()):
        out.append(f"\tif (getmonsterinfo({mid}, MOB_ID) == {mid}) {{\t// {aegis}")
        out.append("\t\t.@mobs++;")
        for d in ds:
            steal = str(d.get("StealProtected", "false")).lower() == "true"
            out.append(f"\t\tif (addmonsterdrop({mid}, {item_id(d['Item'])}, {int(d['Rate'])}{', true' if steal else ''})) .@added++; "
                       f"else .@failed$ += \" {aegis}:{d['Item']}\";\t// {name(d['Item'])}, {int(d['Rate']) / 100:g} %"
                       + (", steal-protected" if steal else ""))
        out.append("\t}")
    out += ["\tif (.@failed$ != \"\")",
            f"\t\terrormes \"{mod}: drops not added (no free drop slot?):\" + .@failed$;",
            f"\tdebugmes \"{mod}: \" + .@added + \" {kind} drops added to \" + .@mobs + \" monsters\";",
            "\tend;", "}"]
    return "\n".join(out) + "\n"


def build(rathena):
    errors, notes = [], []
    re_mobs = load_mobs(f"{rathena}/db/re/mob_db.yml")
    pre_mobs = load_mobs(f"{rathena}/db/pre-re/mob_db.yml")
    item_types = load_item_types(rathena, "pre-re")
    re_item_types = load_item_types(rathena, "re")
    pre_skills = load_skill_names(rathena, "pre-re")
    re_item_blocks = load_item_blocks(rathena, "re")
    pre_skill_names = load_skill_aegis(rathena, "pre-re")
    pre_groups = {g.upper() for g in re.findall(r"^  - Group: (\S+)", open(f"{rathena}/db/pre-re/item_group_db.yml", encoding="utf-8").read(), re.M)}
    pre_skill_ids, pre_skill_max = {}, {}
    cur = None
    for line in open(f"{rathena}/db/pre-re/skill_db.yml", encoding="utf-8"):
        m = re.match(r"^  - Id: (\d+)", line)
        if m:
            cur = int(m[1])
        m = re.match(r"^    Name: (\S+)", line)
        if m and cur is not None:
            pre_skill_ids[m[1]] = cur; last = m[1]
        m = re.match(r"^    MaxLevel: (\d+)", line)
        if m and cur is not None:
            pre_skill_max[last] = int(m[1])
    new_items = {}

    # The fair tier: ordinary pre-renewal monsters that spawn somewhere, less the unfair ones.
    unfair = {r["AegisName"].strip() for r in read_csv("prere_unfair.csv")}
    for name in unfair - {m["AegisName"] for m in pre_mobs.values()}:
        errors.append(f"prere_unfair.csv: {name} is not in pre-renewal's mob_db")
    spawned = set()
    for dirpath, _, files in os.walk(f"{rathena}/npc/pre-re/mobs"):
        for f in files:
            for line in open(os.path.join(dirpath, f), encoding="utf-8"):
                m = SPAWN.match(line)
                if m:
                    spawned.add(int(m[4]))
    ordinary = [p for i, p in pre_mobs.items()
                if i in spawned and num(p, "BaseExp") > 0 and not is_boss(p) and p["AegisName"] not in unfair]
    # Pairs both eras share. A renewal-level window takes only monsters pre-renewal
    # spawns, leaving out the instance, event and slave copies that crowd the lower
    # levels; the high band takes every one (some of its anchors spawn only in scripts).
    pairs = [(re_mobs[i], p) for i, p in pre_mobs.items()
             if i in re_mobs and num(p, "BaseExp") > 0 and not is_boss(p)]
    # Bosses (MVPs and minibosses) are converted as ordinary monsters of their region,
    # then corrected for how differently the two eras weigh a boss against its map
    # (BOSSES.md). Their DEF, MDEF and stats rank among pre-renewal's bosses of
    # their kind.
    kind = lambda m: "mvp" if "MvpExp" in m else "miniboss" if m.get("Class") == "Boss" else None
    boss_ordinary = [p for i, p in pre_mobs.items() if i in spawned and kind(p) and num(p, "BaseExp") > 1
                     and p["AegisName"] not in unfair]
    boss_corr = boss_correction(rathena, re_mobs, pre_mobs, kind)
    boss_peer = boss_peer_correction(rathena, re_mobs, pre_mobs, kind)
    for k_, c in boss_corr.items():
        notes.append(f"boss correction {k_}: " + ", ".join(f"{k} {'+' if k == 'Level' else 'x'}{v:.2f}" for k, v in c.items()))
    bands = load_bands()
    if isinstance(bands, str):
        return {}, [bands], notes, ""
    cache = {}
    steps = {int(r["step"]): {"step": int(r["step"]), "hp": float(r.get("hp") or 0), "attack": float(r.get("attack") or 0),
                              "exp_per_hp": float(r.get("exp_per_hp") or 0.2)} for r in read_csv("steps.csv")}
    # Renewal's monsters of the open world: those on a map pre-renewal has monsters on,
    # or on an open map of renewal-world. The quest areas' and later episodes' monsters
    # have many times the HP of anything at their level and would move every median.
    open_maps = set(map_spawns(rathena, "pre-re")) | {r["map"].strip() for r in read_csv("maps.csv") if r["access"].strip() == "open"}
    re_spawned = {i for mp, ids_ in map_spawns(rathena, "re").items() if mp in open_maps for i in ids_}
    ladder_rows = []

    def ladder_step(r):
        """The level step of an ordinary monster, or None for an object (a plant, a
        crystal: a few HP) and for a monster below the regions' range."""
        lv = num(r, "Level")
        if lv < LADDER_MIN or num(r, "Hp") < 100 or not steps:
            return None
        lv = min(LEVEL_CAP, max(LADDER_FLOOR, lv))
        step = min(170, (lv + 5) // 10 * 10) if lv >= 100 else min(90, (lv + 5) // 10 * 10)
        return steps.get(step)

    def band_of(r):
        forced = map_band.get(int(r["Id"]))
        if forced:
            return next((bd for bd in bands if bd["name"] == forced), None)
        lv = num(r, "Level")
        for bd in bands:
            if bd["lo"] <= lv <= bd["hi"]:
                return bd
        return None

    def references(bd, r):
        """The anchors, their ratios and the fair tier for one monster of a band."""
        src, pool = pairs, ordinary
        if bd["anchor_kind"] == "pre":
            key = ("pre", bd["name"])
            anchors = [(a, p) for a, p in src if bd["anchor_lo"] <= num(p, "Level") <= bd["anchor_hi"]]
        else:
            # The window widens until it holds enough anchors: near renewal 139 six
            # levels held 17, a skewed few that put Rake Scaraba (139) seven levels
            # below Horn Scaraba (130).
            w = bd["anchor_lo"]
            key = ("renewal", bd["name"], num(r, "Level"))
            while True:
                anchors = [(a, p) for a, p in src if abs(num(a, "Level") - num(r, "Level")) <= w
                           and int(p["Id"]) in spawned]
                if len(anchors) >= MIN_ANCHORS or w >= 20:
                    break
                w += 2
        if key in cache:
            return cache[key]
        if len(anchors) < 5:
            cache[key] = None
            return None
        ratio = {k: statistics.median(num(p, k) / num(a, k) for a, p in anchors if num(a, k) > 0) for k in SCALED}
        spread = statistics.median(num(p, "Attack2") / num(p, "Attack") for a, p in anchors if num(p, "Attack") > 0)
        level = rank_map(num(r, "Level"), [num(a, "Level") for a, _ in anchors], [num(p, "Level") for _, p in anchors])
        if bd["fair_kind"] == "level":
            fair = [p for p in pool if bd["fair_lo"] <= num(p, "Level") <= bd["fair_hi"]]
        else:
            fair = [p for p in pool if abs(num(p, "Level") - level) <= bd["fair_lo"]]
        cache[key] = (anchors, ratio, spread, fair)
        notes.append(f"band {bd['name']} (L{num(r, 'Level')}): {len(anchors)} anchors, ratios "
                     + ", ".join(f"{k} x{v:.2f}" for k, v in ratio.items())
                     + f", Attack2 = Attack x{spread:.2f}; then Attack x{bd['offence']}, Hp and Exp x{bd['toughness']};"
                     + f" fair tier {len(fair)} monsters")
        return cache[key]

    # Spawns on the listed maps.
    map_rows = read_csv("monster_maps.csv")
    maps = [r["map"].strip() for r in map_rows]
    band_by_map = {r["map"].strip(): (r.get("band") or "").strip() for r in map_rows}
    boss_maps = {r["map"].strip() for r in map_rows if (r.get("bosses") or "").strip().lower() == "yes"}
    # A map may scale its monsters further (offence for attack, toughness for HP and
    # experience): renewal's quest areas are built for characters far past 99.
    map_scale = {r["map"].strip(): (float(r.get("offence") or 1), float(r.get("toughness") or 1)) for r in map_rows}
    access = {r["map"].strip(): r["access"].strip() for r in read_csv("maps.csv")}
    for mp in maps:
        if mp not in access:
            errors.append(f"monster_maps.csv: {mp} is not in maps.csv")
        elif access[mp] == "staged":
            errors.append(f"monster_maps.csv: {mp} is staged (nothing leads in): no monsters for it yet")
    spawns = {mp: [] for mp in maps}
    left_bosses = set()
    for dirpath, _, files in os.walk(f"{rathena}/npc/re/mobs"):
        for f in sorted(files):
            path = os.path.join(dirpath, f)
            if SPAWN_SKIP.search(path):
                continue
            for line in open(path, encoding="utf-8"):
                m = SPAWN.match(line)
                if m and m[1] in spawns:
                    mid = int(m[4])
                    mob = pre_mobs.get(mid) or re_mobs.get(mid)
                    if mob is not None and (is_boss(mob) or m[2] == "boss_monster") and m[1] not in boss_maps:
                        notes.append(f"{m[1]}: boss {mob['AegisName']} left out (bosses are not added yet)")
                        left_bosses.add(mid)
                        continue
                    spawns[m[1]].append((line.rstrip("\n"), mid))
    for mp in maps:
        if not spawns[mp]:
            errors.append(f"{mp}: renewal spawns no monsters there")

    wanted = {mid for lines in spawns.values() for _, mid in lines if mid not in pre_mobs}
    # Equipment the renewal monsters and bosses drop and pre-renewal lacks: converted by
    # build_equipment.py (PORTING_EQUIP.md). A boss's items are converted now and drop once
    # the boss is in (phase 6).
    equip_names = {d["Item"] for i in wanted | left_bosses if i in re_mobs for d in re_mobs[i]["Drops"] + re_mobs[i]["MvpDrops"]
                   if re_item_types.get(d["Item"]) in ("Weapon", "Armor", "Shadowgear") and d["Item"] not in item_types}
    EQUIPMENT_NAMES.clear(); EQUIPMENT_NAMES.update(equip_names)
    EQUIPMENT_SOURCES.clear()
    for i in wanted | left_bosses:
        for d in re_mobs.get(i, {}).get("Drops", []) + re_mobs.get(i, {}).get("MvpDrops", []):
            if d["Item"] in equip_names:
                EQUIPMENT_SOURCES.setdefault(d["Item"], []).append(
                    f"{re_mobs[i]['AegisName']}{' (boss, later)' if i in left_bosses else ''} {int(d.get('Rate', 0)) / 100:g} %")
    equipment = build_equipment.convert(rathena, equip_names)
    for name, (blk, _, _) in equipment.items():
        new_items[name] = blk
    # Cards pre-renewal lacks (phase 8): converted by build_cards.py and dropped; what it cannot
    # convert (not in the draft) stays left out and listed.
    card_names = {d["Item"] for i in wanted | left_bosses if i in re_mobs for d in re_mobs[i]["Drops"] + re_mobs[i]["MvpDrops"]
                  if re_item_types.get(d["Item"]) == "Card" and d["Item"] not in item_types}
    CARD_NAMES.clear(); CARD_NAMES.update(card_names); CARD_SOURCES.clear()
    for i in wanted | left_bosses:
        for d in re_mobs.get(i, {}).get("Drops", []) + re_mobs.get(i, {}).get("MvpDrops", []):
            if d["Item"] in card_names:
                CARD_SOURCES.setdefault(d["Item"], []).append(f"{re_mobs[i]['AegisName']} {int(d.get('Rate', 0)) / 100:g} %")
    cards = build_cards.convert(rathena, card_names)
    for name, c in cards.items():
        new_items[name] = c["block"]
    cards_left = []
    # Bosses are converted (into the monster table, so the fights can call them) before they
    # spawn: a map spawns its bosses only once its monster_maps.csv row says bosses: yes.
    wanted |= {b for b in left_bosses if b not in pre_mobs}
    for i in sorted(wanted | left_bosses):
        for key in ("Drops", "MvpDrops"):
            for d in re_mobs.get(i, {}).get(key, []):
                if re_item_types.get(d["Item"]) == "Card" and d["Item"] not in item_types and d["Item"] not in cards:
                    cards_left.append((re_mobs[i]["AegisName"], "boss" if i in left_bosses else "", d["Item"], d.get("Rate", ""),
                                       " ".join(re.sub(r"\s+", " ", re.search(r"Script: \|\n((?:      .*\n?)+)", re_item_blocks.get(d["Item"], "") + "\n")[1]).split())
                                       if "Script:" in re_item_blocks.get(d["Item"], "") else ""))
    # A boss's summoned slaves come too when pre-renewal lacks them (they spawn only
    # when it calls them).
    re_skill_rows = [l.rstrip("\n").split(",") for l in open(f"{rathena}/db/re/mob_skill_db.txt", encoding="utf-8")
                     if l[:1].isdigit()]
    for _ in range(3):
        for cols in re_skill_rows:
            if len(cols) > 16 and int(cols[0]) in wanted and cols[1].split("@")[-1] in ("NPC_SUMMONSLAVE", "NPC_CALLSLAVE"):
                for v in cols[12:17]:
                    if v.strip().isdigit() and int(v) not in pre_mobs and int(v) in re_mobs:
                        wanted.add(int(v))
    wanted = sorted(wanted)
    # A map may put all its monsters in one band (a region in one band, not split at a
    # band's edge); otherwise each monster's renewal level picks it.
    map_band = {}
    for mp, lines in spawns.items():
        for _, mid in lines:
            if band_by_map.get(mp) and mid not in map_band:
                map_band[mid] = band_by_map[mp]
    overrides = {r["AegisName"].strip(): r for r in read_csv("monsters.csv")}
    converted = []
    added_drops = {GEAR: [], CARDS: []}   # (mob id, AegisName, drop) of the converted equipment and cards
    skill_rule = {}
    for mid in wanted:
        r = re_mobs.get(mid)
        if r is None:
            errors.append(f"monster {mid} is in renewal's spawns but not its mob_db")
            continue
        bd = band_of(r)
        refs = references(bd, r) if bd else None
        if refs is None:
            errors.append(f"{r['AegisName']} (renewal level {num(r, 'Level')}): no band in bands.csv"
                          if bd is None else f"{r['AegisName']}: fewer than 5 anchors in band {bd['name']}")
            continue
        anchors, ratio, atk_spread, fair = refs
        skill_rule[mid] = bd
        scales = [map_scale.get(mp, (1, 1)) for mp, lines in spawns.items() if any(i == mid for _, i in lines)]
        off_x = min((o for o, _ in scales), default=1); tough_x = min((t for _, t in scales), default=1)
        mob = {k: v for k, v in r.items() if k not in ("Drops", "MvpDrops")}
        mob["Modes"] = dict(r.get("Modes", {}))
        # Renewal's data leaves the attack speed off a few monsters (G_BANASPATY, the copy
        # of Banaspaty that Leak summons; the three Lichterns), and rAthena then attacks
        # at its fastest: a hit every 0.1 s. Leak's summoned Banaspaty did 70-80 % of what
        # a party took until this was found. A summoned copy (G_X) takes its original's;
        # the rest are reported (the Lichterns were calibrated as they are).
        if not num(r, "AttackDelay"):
            twin = next((m for m in re_mobs.values() if r["AegisName"].startswith("G_")
                         and m["AegisName"] == r["AegisName"][2:] and num(m, "AttackDelay")), None)
            if twin:
                for k in ("AttackDelay", "AttackMotion", "DamageMotion"):
                    if k in twin and not num(r, k):
                        mob[k] = twin[k]
                notes.append(f"{r['AegisName']}: no attack speed in renewal's data, {twin['AegisName']}'s taken")
            else:
                notes.append(f"{r['AegisName']}: no attack speed in renewal's data: rAthena attacks at its fastest")
        for k in SCALED:
            mob[k] = max(1, round(num(r, k) * ratio[k] * (bd["offence"] if k == "Attack" else bd["toughness"])))
        mob["Level"] = rank_map(num(r, "Level"), [num(a, "Level") for a, _ in anchors],
                                [num(p, "Level") for _, p in anchors])
        peers = [m for m in re_mobs.values() if abs(num(m, "Level") - num(r, "Level")) <= PEER_LEVELS
                 and num(m, "BaseExp") > 0 and not is_boss(m)]
        # The monster's own kind: by the Mvp mode for an MVP whose table leaves the MVP experience
        # out (Spider Chariot), so it is converted, corrected and laddered as one. The peers and the
        # era's corrections still go by kind(), so no other monster's numbers move with it.
        bk = "mvp" if is_mvp(r) else kind(r)
        if bk:
            # A boss: the era's correction, then its kind's peers in each era (renewal's
            # around its renewal level, pre-renewal's around where it lands) for the
            # ranks and the cap. The window widens until each holds eight.
            for k in SCALED:
                mob[k] = max(1, round(mob[k] * boss_corr[bk][k]))
            mob["Level"] = min(99, round(mob["Level"] + boss_corr[bk]["Level"]))
            for w in range(PEER_LEVELS, 41, 2):
                peers = [m for m in re_mobs.values() if kind(m) == bk and abs(num(m, "Level") - num(r, "Level")) <= w
                         and num(m, "BaseExp") > 1 and m["Id"] != r["Id"]]
                if len(peers) >= 8:
                    break
            for w in range(PEER_LEVELS, 41, 2):
                fair = [p for p in boss_ordinary if kind(p) == bk and abs(num(p, "Level") - mob["Level"]) <= w]
                if len(fair) >= 8:
                    break
        # A cap, where the band sets one: HP and attack at most that many times the
        # strongest of the fair tier. Renewal's quest areas give monsters many times
        # the HP of anything at their level (a Bios Island Plasma came out at 1.15M).
        if bd.get("cap") and fair:
            for k in ("Hp", "Attack") + (("BaseExp", "JobExp") if bk else ()):
                top = max(num(p, k) for p in fair)
                if mob[k] > bd["cap"] * top:
                    notes.append(f"{r['AegisName']}: {k} {mob[k]} capped at {bd['cap']}x the fair tier's strongest ({top})")
                    if k == "Hp":
                        f = bd["cap"] * top / mob["Hp"]
                        mob["BaseExp"] = max(1, round(mob["BaseExp"] * f)); mob["JobExp"] = max(1, round(mob["JobExp"] * f))
                    mob[k] = round(bd["cap"] * top)
        for k in FAIR_RANKED:
            if k in LEVEL_BOUND:
                sum_of = lambda m: num(m, "Level") + num(m, k)
                target = rank_map(sum_of(r), [sum_of(m) for m in peers], [sum_of(p) for p in fair])
                if k == "Agi":
                    target = min(target, rank_cap(sorted(sum_of(p) for p in fair), FLEE_CAP))
                mob[k] = max(1, target - mob["Level"])
            else:
                mob[k] = rank_map(num(r, k), [num(m, k) for m in peers], [num(p, k) for p in fair])
        if off_x != 1 or tough_x != 1:
            mob["Attack"] = max(1, round(mob["Attack"] * off_x))
            for k in ("Hp", "BaseExp", "JobExp"):
                mob[k] = max(1, round(mob[k] * tough_x))
        mob["Attack2"] = round(mob["Attack"] * atk_spread)
        # The ladder (steps.csv): an ordinary monster keeps its renewal level, and its HP
        # and attack are its level step's reference times how it stands among renewal's
        # monsters of its level. The reference is what the fights tune, step by step
        # (BALANCING.md, "Above 99"). Bosses and objects keep the conversion above.
        st = ladder_step(r) if not bk else None
        if st:
            lv = min(LEVEL_CAP, max(LADDER_FLOOR, num(r, "Level")))
            mob["Level"] = lv
            for w in range(5, 31, 5):
                near = [m for m in re_mobs.values() if abs(num(m, "Level") - num(r, "Level")) <= w
                        and int(m["Id"]) in re_spawned and num(m, "BaseExp") > 0 and not is_boss(m) and num(m, "Hp") >= 100]
                if len(near) >= 8:
                    break
            lfair = [p for p in ordinary if (80 <= num(p, "Level") <= 99 if lv >= 100 else abs(num(p, "Level") - lv) <= 8)]
            ref_hp, ref_atk = st["hp"], st["attack"]
            if not ref_hp:    # below 100: a step above the fair pre-renewal monsters of its level
                ref_hp = statistics.median(num(p, "Hp") for p in lfair) * 1.25
                ref_atk = statistics.median(num(p, "Attack") for p in lfair)
            rel = lambda k, lo, hi: min(hi, max(lo, num(r, k) / statistics.median(num(m, k) for m in near)))
            rel_hp, rel_atk = rel("Hp", *REL_HP), rel("Attack", *REL_ATTACK)
            mob["Hp"] = max(1, round(ref_hp * rel_hp))
            mob["Attack"] = 1 if num(r, "Attack") <= 1 else max(1, round(ref_atk * rel_atk))
            spread = statistics.median(num(p, "Attack2") / num(p, "Attack") for p in lfair if num(p, "Attack") > 0)
            mob["Attack2"] = round(mob["Attack"] * spread)
            job_share = num(r, "JobExp") / max(1, num(r, "BaseExp"))
            mob["BaseExp"] = max(1, round(mob["Hp"] * st["exp_per_hp"]))
            mob["JobExp"] = max(1, round(mob["BaseExp"] * job_share))
            for k in FAIR_RANKED:
                mob[k] = rank_map(num(r, k), [num(m, k) for m in peers], [num(p, k) for p in lfair])
            mob["Agi"] = min(mob["Agi"], rank_cap(sorted(num(p, "Agi") for p in lfair), FLEE_CAP))
            ladder_rows.append((st["step"], lv, r["AegisName"], rel_hp, rel_atk))
            where = {mp: sum(int(ln.split("\t")[3].split(",")[1]) for ln, i in lines if i == mid) for mp, lines in spawns.items()}
            LADDER.append({"step": st["step"], "level": lv, "id": mid, "AegisName": r["AegisName"],
                           "rel_hp": round(rel_hp, 2), "rel_attack": round(rel_atk, 2), "hp": None, "attack": None,
                           "maps": " ".join(f"{mp}:{n}" for mp, n in where.items() if n)})
        # A boss on the ladder (level-175 run, phase 6): it keeps its renewal level as the
        # ordinary monsters do, and its HP and attack are its step's reference times how far it
        # stands above renewal's ordinary monsters of its level, corrected for how the two eras
        # weigh a boss against its map (boss_correction: an MVP x0.59 HP, x0.96 attack; a
        # miniboss x2.0, x1.65), at most what pre-renewal's bosses of the kind stand above their
        # map (90th percentile). Experience per HP is what pre-renewal's bosses pay against
        # their HP relative to an ordinary monster (the correction's EXP over its HP). Only a
        # starting point: the attrition fights decide (BOSSES.md).
        bst = None
        if bk and steps and num(r, "Level") >= LADDER_MIN:
            lv = min(LEVEL_CAP, max(LADDER_FLOOR, num(r, "Level")))
            bst = steps.get(min(170, (lv + 5) // 10 * 10) if lv >= 100 else min(90, (lv + 5) // 10 * 10))
        if bst:
            mob["Level"] = lv
            for w in range(5, 31, 5):
                near = [m for m in re_mobs.values() if abs(num(m, "Level") - num(r, "Level")) <= w
                        and int(m["Id"]) in re_spawned and num(m, "BaseExp") > 0 and not is_boss(m) and num(m, "Hp") >= 100]
                if len(near) >= 8:
                    break
            lfair = [p for p in ordinary if (80 <= num(p, "Level") <= 99 if lv >= 100 else abs(num(p, "Level") - lv) <= 8)]
            ref_hp, ref_atk = bst["hp"], bst["attack"]
            if not ref_hp:
                ref_hp = statistics.median(num(p, "Hp") for p in lfair) * 1.25
                ref_atk = statistics.median(num(p, "Attack") for p in lfair)
            ratio_of = lambda k: num(r, k) / statistics.median(num(m, k) for m in near)
            hp_x = min(ratio_of("Hp") * boss_peer[bk]["Hp"], boss_peer[bk]["cap_Hp"])
            atk_x = min(ratio_of("Attack") * boss_peer[bk]["Attack"], boss_peer[bk]["cap_Attack"])
            mob["Hp"] = max(1, round(ref_hp * hp_x))
            mob["Attack"] = max(1, round(ref_atk * atk_x))
            spread = statistics.median(num(p, "Attack2") / num(p, "Attack") for p in lfair if num(p, "Attack") > 0)
            mob["Attack2"] = round(mob["Attack"] * spread)
            # Its spells: pre-renewal takes a monster's magic attack from its INT (INT + (INT/7)^2 at
            # the least), renewal from its own MATK (Attack2 there). Ranked into pre-renewal's usual
            # INT a boss's spells lost most of their bite (Leak: INT 35, renewal MATK 1284). The INT is
            # set so its magic attack takes the same factor as its physical attack.
            re_matk = num(r, "Attack2")
            if re_matk > 0 and num(r, "Attack") > 0:
                # at most twice its physical attack: a boss with little attack and much magic in renewal
                # (the gold Scarabas: ATK 412, MATK 3211) would otherwise come out at MATK 9,000+
                want = min(re_matk * mob["Attack"] / num(r, "Attack"), 2 * mob["Attack"])
                i = 1
                while i < 999 and i + (i // 7) ** 2 < want:
                    i += 1
                if i > mob["Int"]:
                    notes.append(f"{r['AegisName']}: INT {mob['Int']} -> {i}, so its spells hit with MATK {int(want)} (renewal MATK {re_matk}, scaled as its attack)")
                    mob["Int"] = i
            job_share = num(r, "JobExp") / max(1, num(r, "BaseExp"))
            mob["BaseExp"] = max(1, round(mob["Hp"] * bst["exp_per_hp"] * boss_peer[bk]["BaseExp"] / boss_peer[bk]["Hp"]))
            mob["JobExp"] = max(1, round(mob["BaseExp"] * job_share))
            notes.append(f"{r['AegisName']}: boss on the ladder, level {lv}: HP x{hp_x:.1f} and attack x{atk_x:.2f} its step's "
                         f"reference (renewal: x{ratio_of('Hp'):.0f} and x{ratio_of('Attack'):.1f} its level's ordinary monsters; "
                         f"the era's {bk} correction against its level x{boss_peer[bk]['Hp']:.2f} / x{boss_peer[bk]['Attack']:.2f}, "
                         f"capped at pre-renewal's 90th percentile, x{boss_peer[bk]['cap_Hp']:.0f} / x{boss_peer[bk]['cap_Attack']:.1f})")
        # Attack speed keeps its rank, at pre-renewal's speeds, where the band says so:
        # copied, Comodo (0.5 s) and Dolomedes (0.36 s) hit like three of anything else.
        if bd.get("attack_speed") == "rank" and num(r, "AttackDelay"):
            delay = rank_map(num(r, "AttackDelay"), [num(m, "AttackDelay") for m in peers if num(m, "AttackDelay")],
                             [num(p, "AttackDelay") for p in fair if num(p, "AttackDelay")])
            scale = delay / num(r, "AttackDelay")
            mob["AttackDelay"] = delay
            for k in ("AttackMotion", "ClientAttackMotion"):
                if num(r, k):
                    mob[k] = max(1, round(num(r, k) * min(scale, 1.0) if scale < 1 else num(r, k) * scale))
        ov = overrides.pop(r["AegisName"], {})
        for k in OVERRIDABLE:
            if (ov.get(k) or "").strip():
                mob[k] = int(ov[k])
        for k, col in (("Hp", "HpScale"), ("Attack", "AttackScale")):   # a monster off its step's line
            if (ov.get(col) or "").strip():
                f = float(ov[col])
                mob[k] = max(1, round(mob[k] * f))
                if k == "Hp" and not (ov.get("BaseExp") or "").strip():
                    mob["BaseExp"] = max(1, round(mob["BaseExp"] * f)); mob["JobExp"] = max(1, round(mob["JobExp"] * f))
                if k == "Attack":
                    mob["Attack2"] = max(mob["Attack"], round(mob["Attack2"] * f))
        if (ov.get("Attack") or "").strip() and not (ov.get("Attack2") or "").strip():
            mob["Attack2"] = round(mob["Attack"] * atk_spread)   # the range moves with it
        if mob["Attack2"] < mob["Attack"]:
            mob["Attack2"] = mob["Attack"]
        # A boss keeps which of physical and magic damage it resists more, as its designers
        # chose. The eras turn DEF and MDEF into damage differently: compare the reductions
        # (renewal: (4000+DEF)/(4000+10 DEF) and (1000+MDEF)/(1000+10 MDEF); pre-renewal:
        # a percentage), not the numbers. Leak: renewal DEF 280 / MDEF 128 is 37 % / 50 %.
        if bk:
            re_phys = 1 - (4000 + num(r, "Defense")) / (4000 + 10 * num(r, "Defense"))
            re_mag = 1 - (1000 + num(r, "MagicDefense")) / (1000 + 10 * num(r, "MagicDefense"))
            pre_phys, pre_mag = min(mob["Defense"], 99) / 100, min(mob["MagicDefense"], 99) / 100
            if (re_phys - re_mag) * (pre_phys - pre_mag) < 0 and abs(re_phys - re_mag) > 0.05:
                notes.append(f"{r['AegisName']}: resists {'physical' if re_phys > re_mag else 'magic'} damage more in renewal "
                             f"({re_phys:.0%} / {re_mag:.0%}), the other converted (DEF {mob['Defense']} / MDEF "
                             f"{mob['MagicDefense']}): correct it in monsters.csv")
        # Pre-renewal gives every MVP half its base experience as MVP experience. An MVP is what
        # carries the Mvp mode (that is what rAthena goes by); renewal's table leaves the figure
        # out for some of them (Spider Chariot: "#   MvpExp:"), and rAthena then pays none.
        if is_mvp(r):
            mob["MvpExp"] = max(1, mob["BaseExp"] // 2)
        # The MVP rewards (the items handed to the killer) go through the same rules as the drops.
        for key in ("Drops", "MvpDrops"):
            mob[key] = []
            for d in r.get(key, []):
                t = item_types.get(d["Item"]) or re_item_types.get(d["Item"])
                if t in DROP_TYPES and d["Item"] in item_types and t != "Petarmor":
                    mob[key].append(d)          # equipment or a card pre-renewal has: its own item, unchanged
                elif t in DROP_TYPES and (d["Item"] in equipment or d["Item"] in cards):
                    # converted equipment or card: its own mod adds the drop on load (drop_script), so the
                    # monster mods work without it
                    if key == "MvpDrops":
                        errors.append(f"{r['AegisName']}: MVP reward {d['Item']} is converted "
                                      f"{'equipment' if d['Item'] in equipment else 'card'}; addmonsterdrop adds only "
                                      f"drops, not MVP rewards: decide which mod it goes in first")
                    else:
                        added_drops[GEAR if d["Item"] in equipment else CARDS].append((mid, r["AegisName"], d))
                elif t in DROP_TYPES:
                    notes.append(f"{r['AegisName']}: drop {d['Item']} left out ({t})")
                elif d["Item"] not in item_types:
                    # Etc and usable loot pre-renewal lacks comes from renewal's tables as it is.
                    blk = re_item_blocks.get(d["Item"])
                    skills = re.findall(r'itemskill\s*"?(\w+)', blk or "")
                    if blk is None:
                        errors.append(f"{r['AegisName']}: drop {d['Item']} is in neither era's item tables")
                    elif any(sk not in pre_skill_names for sk in skills):
                        errors.append(f"{r['AegisName']}: drop {d['Item']} casts a skill pre-renewal lacks ({', '.join(skills)})")
                    elif any(g not in pre_groups for g in re.findall(r"\bIG_(\w+)", blk)):
                        # a box of renewal-only things (Bs_Making_S: renewal's crafting materials)
                        notes.append(f"{r['AegisName']}: drop {d['Item']} left out (opens an item group pre-renewal lacks)")
                    else:
                        new_items[d["Item"]] = blk
                        mob[key].append(d)
                else:
                    mob[key].append(d)
        converted.append(mob)
        for row in LADDER:
            if row["id"] == mid:
                row.update(hp=mob["Hp"], attack=mob["Attack"], attack2=mob["Attack2"], base_exp=mob["BaseExp"])
    for name in overrides:
        errors.append(f"monsters.csv: {name} is not a monster this build converts")

    # Skills.
    skill_rows = []
    ids = {m["Id"] for m in converted}
    for line in open(f"{rathena}/db/re/mob_skill_db.txt", encoding="utf-8"):
        cols = line.rstrip("\n").split(",")
        if line.startswith("//") or len(cols) < 19 or not cols[0].isdigit() or int(cols[0]) not in ids:
            continue
        sid = int(cols[3])
        # Renewal's second versions of monster skills pre-renewal has in their first version: the
        # first version, so a boss keeps its mechanic (Spider Chariot's area stone curse and Hell
        # Judgement had been dropped; RENEWAL_BOSS_TACTICS.md calls them what decides its fight).
        sub = SKILL_SUBST.get(cols[1].split("@")[-1])
        if sub and sid not in pre_skills:
            cols[1] = cols[1].split("@")[0] + "@" + sub
            cols[3] = str(pre_skill_ids[sub])
            cols[4] = str(min(int(cols[4]), pre_skill_max[sub]))
            sid = int(cols[3])
            notes.append(f"skill row {cols[1]}: renewal's second version replaced by pre-renewal's {sub}")
        if sid not in pre_skills:
            notes.append(f"skill row left out, pre-renewal has no skill {sid}: {cols[1]}")
            continue
        if cols[1].endswith("@NPC_SUMMONSLAVE") and not any(c.strip() for c in cols[12:17]):
            notes.append(f"skill row left out, summons nothing: {cols[1]}")
            continue
        # A boss heals itself only when idle, as pre-renewal's bosses do: renewal's
        # heal in a fight too, and Leak healed through a party of eight.
        bd = skill_rule.get(int(cols[0]))
        if kind(re_mobs[int(cols[0])]) and cols[1].split("@")[-1] in SELF_HEALS \
                and cols[2] != "idle" and cols[9] == "self":
            notes.append(f"skill row left out, a boss heals only when idle: {cols[1]} ({cols[2]})")
            continue
        # A band may scale a skill's level with the monster's level and cap its rate:
        # renewal's levels and rates are set for renewal-sized HP.
        bd = skill_rule.get(int(cols[0]))
        mob = next(m for m in converted if m["Id"] == int(cols[0]))
        if bd and bd["skill_levels"] == "scale":
            scale = mob["Level"] / num(re_mobs[int(cols[0])], "Level")
            cols[4] = str(max(1, round(int(cols[4]) * scale)))
        if bd and bd["skill_rate_cap"]:
            cols[5] = str(min(int(cols[5]), bd["skill_rate_cap"]))
        skill_rows.append(",".join(cols))

    # The split into five mods. renewal-world-mvps: the bosses (what kind() or is_boss() calls one: MVPs and
    # minibosses, the gold Scarabas too), what only they summon, and what turns into or summons one (the gold
    # Scaraba eggs), with their spawn lines. renewal-world-monsters: the rest, with what they summon.
    summons = {}
    for row in skill_rows:
        c = row.split(",")
        if c[1].split("@")[-1] in SUMMONS:
            summons.setdefault(int(c[0]), set()).update(int(v) for v in c[12:17] if v.strip().isdigit() and int(v) in ids)
    bosses = {i for i in ids if kind(re_mobs[i]) or is_boss(re_mobs[i])}
    boss_bound = set(bosses)
    while True:
        more = {i for i, ss in summons.items() if ss & boss_bound} - boss_bound
        if not more:
            break
        boss_bound |= more
    boss_spawn = lambda mid, ln: (mid in boss_bound or is_boss(pre_mobs.get(mid) or re_mobs.get(mid) or {})
                                  or "\tboss_monster\t" in ln)
    in_monsters = {mid for lines in spawns.values() for ln, mid in lines if mid in ids and not boss_spawn(mid, ln)}
    todo = list(in_monsters)
    while todo:
        for s_ in summons.get(todo.pop(), ()):
            if s_ not in in_monsters:
                in_monsters.add(s_); todo.append(s_)
    in_mvps = ids - in_monsters
    reached = set(boss_bound)
    todo = list(boss_bound)
    while todo:
        for s_ in summons.get(todo.pop(), ()):
            if s_ not in reached:
                reached.add(s_); todo.append(s_)
    for i in sorted(in_mvps - reached):
        errors.append(f"{re_mobs[i]['AegisName']}: converted, but neither spawned, a boss nor summoned: which mod is it for?")
    # The bosses split again (owner, 2026-10-18): renewal-world-minibosses holds every boss a map
    # spawns that is not an MVP, and what such a spawn summons or hatches into (the gold Scaraba
    # eggs and the gold Scarabas); renewal-world-mvps the MVPs and the slaves only they summon.
    mvp_ids = {i for i in ids if is_mvp(re_mobs[i])}
    in_minis = {mid for lines in spawns.values() for _, mid in lines if mid in in_mvps and mid not in mvp_ids}
    todo = list(in_minis)
    while todo:
        for s_ in summons.get(todo.pop(), ()):
            if s_ in in_mvps and s_ not in mvp_ids and s_ not in in_minis:
                in_minis.add(s_); todo.append(s_)
    in_mvps -= in_minis
    # An MVP that summons a miniboss (the Gold Queen Scaraba her gold Scarabas) needs that mod on.
    needs_minis = sorted(re_mobs[i]["AegisName"] for i in in_mvps if summons.get(i, set()) & in_minis)
    if needs_minis:
        mj = os.path.join(MODS_DIR, MVPS, "mod.json")
        if not os.path.exists(mj) or f'"{MINIS}"' not in open(mj, encoding="utf-8").read():
            errors.append(f"{MVPS}: {', '.join(needs_minis)} summon minibosses, so its mod.json must require {MINIS}")
    mod_of = lambda mid: MVPS if mid in in_mvps else MINIS if mid in in_minis else MONSTERS

    def spawn_mod(mid, ln):
        """The mod a spawn line goes to; a pre-renewal boss on these maps by whether it is an MVP."""
        if not boss_spawn(mid, ln):
            return MONSTERS
        if mid in ids:
            return mod_of(mid)
        return MVPS if is_mvp(pre_mobs.get(mid) or re_mobs.get(mid) or {}) else MINIS

    head = ("Generated by tools/renewal-world-monsters/build_monsters.py from rAthena's renewal tables. "
            "Do not edit:\n{c} change the tables there (monster_maps.csv, monsters.csv, equipment.csv, cards.csv) and run it with --write.")
    files = {}
    put = lambda mod, path, text: files.__setitem__(f"{mod}/{path}", text)
    what = {MONSTERS: "the ordinary monsters", MVPS: "the MVPs and the monsters only they summon",
            MINIS: "the minibosses a map spawns or hatches, and what they summon"}
    for mod in (MONSTERS, MINIS, MVPS):
        mobs_out = [f"# {head.format(c='#')}", f"# {what[mod][0].upper() + what[mod][1:]}.", "",
                    "Header:", "  Type: MOB_DB", f"  Version: {MOB_DB_VERSION}", "", "Body:"]
        for mob in converted:
            if mod_of(mob["Id"]) == mod:
                mobs_out += mob_yaml(mob)
        put(mod, OUT_MOBS, "\n".join(mobs_out) + "\n")
        put(mod, OUT_SKILLS, "\n".join([f"// {head.format(c='//')}"] + [r_ for r_ in skill_rows if mod_of(int(r_.split(",")[0])) == mod]) + "\n")
        spawns_out = [f"// {head.format(c='//')}", f"// Spawns of {what[mod]}, copied from renewal."]
        quest_out = [f"// {head.format(c='//')}", f"// Spawns of {what[mod]} on the quest areas, copied from renewal; loaded while quest_areas is on."]
        for mp in maps:
            lines = [ln for ln, mid in spawns[mp] if spawn_mod(mid, ln) == mod]
            if lines:
                out = quest_out if access.get(mp) == "quest" else spawns_out
                out += [""] + lines
        put(mod, OUT_SPAWNS[mod], "\n".join(spawns_out) + "\n")
        if len(quest_out) > 2:
            put(mod, OUT_QUEST_SPAWNS[mod], "\n".join(quest_out) + "\n")
            mj = os.path.join(MODS_DIR, mod, "mod.json")
            if not os.path.exists(mj) or '"quest_areas"' not in open(mj, encoding="utf-8").read():
                errors.append(f"{mod}: spawns on the quest areas, but its mod.json declares no quest_areas setting")

    # Items: the converted equipment and cards in their own mods, the loot copied from renewal in the monsters'.
    item_mod = lambda name: GEAR if name in equipment else CARDS if name in cards else MONSTERS
    item_id = lambda name: int(re.match(r"  - Id: (\d+)", new_items[name])[1])
    item_what = {MONSTERS: "Loot pre-renewal lacks, copied from renewal's item tables.",
                 GEAR: "Renewal's equipment the renewal-world monsters drop, converted for pre-renewal (build_equipment.py).",
                 CARDS: "Renewal's cards the renewal-world monsters drop, converted for pre-renewal (build_cards.py)."}
    for mod in (MONSTERS, GEAR, CARDS):
        mine = sorted((k for k in new_items if item_mod(k) == mod), key=item_id)
        if mine:
            put(mod, OUT_ITEMS, "\n".join([f"# {head.format(c='#')}", f"# {item_what[mod]}", "", "Header:", "  Type: ITEM_DB",
                                           f"  Version: {ITEM_DB_VERSION}", "", "Body:"] + [new_items[k] for k in mine]) + "\n")
    notes.append("items copied or converted from renewal: " + ", ".join(sorted(new_items)))
    # Renewal's sets that this game can complete, scaled to a third (build_combos.py): a set of gear (and
    # pre-renewal items) in the gear mod, one of cards in the cards mod.
    import build_combos
    COMBOS.clear()
    COMBOS.update(build_combos.convert(rathena, set(item_types) | set(new_items), EQUIPMENT_NAMES | CARD_NAMES))
    set_mod = []
    for c in COMBOS["compare"]:
        pieces = {i for alt in c["items"] for i in alt}
        kinds = {item_mod(i) for i in pieces if i in equipment or i in cards}
        if len(kinds) != 1:
            errors.append(f"set {' + '.join(sorted(pieces))}: mixes converted equipment and cards; "
                          f"{GEAR} and {CARDS} each need only {MONSTERS}: decide which mod it goes in first")
        set_mod.append(min(kinds) if kinds else None)
    for mod in (GEAR, CARDS):
        entries = [e for e, m in zip(COMBOS["entries"], set_mod) if m == mod]
        if entries:
            put(mod, OUT_COMBOS, f"# {head.format(c='#')}\n# Renewal's sets for the converted "
                f"{'gear' if mod == GEAR else 'cards'}, every bonus at a third.\n\n" + build_combos.table(entries))
    notes.append(f"sets from renewal: {len(COMBOS['compare'])}")
    # The client's names and descriptions for every item a mod adds (build_iteminfo.py).
    import build_iteminfo, itemdesc
    itemdesc.RATHENA = rathena
    for mod in (MONSTERS, GEAR, CARDS):
        blocks = {k: v for k, v in new_items.items() if item_mod(k) == mod}
        if blocks:
            lua, no_entry = build_iteminfo.build(blocks, (EQUIPMENT_NAMES | CARD_NAMES) & set(blocks),
                                                 [c for c, m in zip(COMBOS["compare"], set_mod) if m == mod], itemdesc)
            put(mod, OUT_ITEMINFO, lua)
            if no_entry:
                notes.append(f"{mod}: no client entry in the translation for: " + ", ".join(no_entry))
    # The converted equipment's and cards' drops, added on load by their mod's script. rAthena keeps at most
    # MAX_MOB_DROP drops a monster, and addmonsterdrop fails on a full one: the mob_db's and the added together.
    for mob in converted:
        n = len(mob["Drops"]) + sum(1 for k in added_drops for i, _, _ in added_drops[k] if i == mob["Id"])
        if n > MAX_MOB_DROP:
            errors.append(f"{mob['AegisName']}: {n} drops with the converted equipment and cards, rAthena keeps {MAX_MOB_DROP}")
    for mod, kind_ in ((GEAR, "equipment"), (CARDS, "card")):
        put(mod, OUT_DROPS[mod], drop_script(mod, kind_, added_drops[mod], item_id, new_items, head))
        notes.append(f"{mod}: {len(added_drops[mod])} drops on {len({i for i, _, _ in added_drops[mod]})} monsters")
    files[OUT_CARDS] = "AegisName,boss,card,rate,renewal effect\n" + "".join(
        ",".join('"' + str(x).replace('"', '""') + '"' if "," in str(x) or '"' in str(x) else str(x) for x in row) + "\n" for row in cards_left)

    # Every converted monster, renewal's values against the converted ones, for the run's status page.
    COMPARE_KEYS = ("Level", "Hp", "Attack", "Attack2", "Defense", "MagicDefense", "Str", "Agi", "Vit", "Int", "Dex", "Luk",
                    "BaseExp", "JobExp", "MvpExp", "AttackDelay", "WalkSpeed", "Element", "ElementLevel", "Race", "Size")
    compare = [{"id": mob["Id"], "AegisName": mob["AegisName"], "name": re_mobs[mob["Id"]].get("Name", mob["AegisName"]),
                "boss": bool(kind(re_mobs[mob["Id"]])),
                "before": {k: re_mobs[mob["Id"]].get(k) for k in COMPARE_KEYS if re_mobs[mob["Id"]].get(k) is not None},
                "after": {k: mob.get(k) for k in COMPARE_KEYS if mob.get(k) is not None},
                "skills_before": [skill_line(c) for c in re_skill_rows if int(c[0]) == mob["Id"]],
                "skills_after": [skill_line(r_.split(",")) for r_ in skill_rows if int(r_.split(",")[0]) == mob["Id"]],
                "changes": [n for n in notes if n.startswith(mob["AegisName"] + ":")
                            or (re_mobs[mob["Id"]].get("Name", "\0") + "@") in n]} for mob in converted]
    files[OUT_COMPARE] = json.dumps(compare, indent=1, default=str) + "\n"
    table = ["", f"{'monster':16}{'renewal':>44}   pre-renewal"]
    for mob in converted:
        r = re_mobs[mob["Id"]]
        f = lambda m, a2: (f"L{num(m, 'Level'):>3} HP{num(m, 'Hp'):>7} ATK{num(m, 'Attack'):>5}"
                           f"{'-' + str(num(m, 'Attack2')) if a2 else '':<7} DEF{num(m, 'Defense'):>4}"
                           f" MDEF{num(m, 'MagicDefense'):>4} EXP{num(m, 'BaseExp'):>6}")
        table.append(f"{mob['AegisName']:16}{f(r, False)}   {f(mob, True)}")
    table.append("")
    for step in sorted({x[0] for x in ladder_rows}):
        table.append(f"step {step}: " + ", ".join(f"{n} L{lv} hp x{h:.2f} atk x{a_:.2f}" for s_, lv, n, h, a_ in sorted(ladder_rows) if s_ == step))
    kept = {mid for lines in spawns.values() for _, mid in lines} - ids
    summary = "\n".join([n for n in notes if n.startswith("band ")] + table + [
        "", f"{len(converted)} monsters converted, {len(kept)} kept with their pre-renewal stats, "
        f"{sum(len(v) for v in spawns.values())} spawns on {len(maps)} maps, {len(skill_rows)} skill rows"] + [
        f"{mod}: " + ", ".join(x for x in (
            f"{sum(1 for i in ids if mod_of(i) == mod)} monsters" + (f" ({len(bosses & {i for i in ids if mod_of(i) == mod})} bosses)" if mod in (MVPS, MINIS) else "") + ", "
            f"{sum(1 for v in spawns.values() for ln, mid in v if spawn_mod(mid, ln) == mod)} spawn lines, "
            f"{sum(1 for r_ in skill_rows if mod_of(int(r_.split(',')[0])) == mod)} skill rows" if mod in (MONSTERS, MVPS, MINIS) else "",
            f"{sum(1 for k in new_items if item_mod(k) == mod)} items" if mod not in (MVPS, MINIS) else "",
            f"{sum(1 for m in set_mod if m == mod)} sets, {len(added_drops[mod])} drops on "
            f"{len({i for i, _, _ in added_drops[mod]})} monsters" if mod in (GEAR, CARDS) else "") if x)
        for mod in (MONSTERS, MINIS, MVPS, GEAR, CARDS)])
    return files, errors, [n for n in notes if not n.startswith("band ")], summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rathena", default=os.environ.get("RATHENA_DIR", os.path.join(APP, "vendor/rathena")))
    ap.add_argument("--write", action="store_true", help="write the mod's tables and spawns")
    ap.add_argument("--check", action="store_true", help="fail if they are stale")
    ap.add_argument("-v", "--verbose", action="store_true", help="also list what was left out")
    a = ap.parse_args()
    if not os.path.isdir(f"{a.rathena}/db/re"):
        sys.exit(f"no rAthena checkout at {a.rathena} (use --rathena or RATHENA_DIR)")
    files, errors, notes, summary = build(a.rathena)
    print(summary)
    if a.verbose:
        for n in notes:
            print("  " + n)
    for e in errors:
        print("ERROR: " + e, file=sys.stderr)
    if errors:
        sys.exit(f"{len(errors)} error(s); nothing written")
    where = lambda p: os.path.join(HERE, p[1:]) if p.startswith("@") else os.path.join(MODS_DIR, p)
    stale = [p for p, text in files.items()
             if not os.path.exists(where(p)) or open(where(p), encoding="utf-8").read() != text]
    # A file the build owns and no longer writes (a mod that lost all its quest-area spawns, say).
    gone = [f"{mod}/{p}" for mod, ps in OWNED.items() for p in ps
            if f"{mod}/{p}" not in files and os.path.exists(os.path.join(MODS_DIR, mod, p))]
    stale += [p + " (no longer written)" for p in gone]
    if a.check:
        if stale:
            sys.exit("stale: " + ", ".join(stale) + " (run build_monsters.py --write)")
        print("up to date")
    elif a.write:
        for p, text in files.items():
            os.makedirs(os.path.dirname(where(p)), exist_ok=True)
            with open(where(p), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        for p in gone:
            os.remove(os.path.join(MODS_DIR, p))
            print("removed " + p)
        with open(os.path.join(HERE, "ladder.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, ["step", "level", "id", "AegisName", "rel_hp", "rel_attack", "hp", "attack", "attack2", "base_exp", "maps"])
            w.writeheader()
            w.writerows(sorted(LADDER, key=lambda x: (x["step"], x["level"], x["id"])))
        print("wrote " + ", ".join(files))
    else:
        print("would write " + ", ".join(files) + (" (changed: " + ", ".join(stale) + ")" if stale else " (unchanged)"))


if __name__ == "__main__":
    main()
