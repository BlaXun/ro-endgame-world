#!/usr/bin/env python3
"""bosscards.py <rathena> <mob id or AegisName> [<mod's mob_db.yml>]: the two weapon cards a player would put in a
two-slot weapon against that monster, from ordinary monster cards only (no MVP or boss cards):
the race card, the element card, the size card, two of them from different kinds, since in
pre-renewal cards of one kind add up and different kinds multiply (DAMAGE_MECHANICS.md, cards).
Prints "card1:card2" for GEAR_CARDS, and the reasoning on stderr."""
import os, re, sys

rathena, want = sys.argv[1], sys.argv[2]
db = os.path.join(rathena, "db", "pre-re")
mobs = open(os.path.join(db, "mob_db.yml")).read()
if len(sys.argv) > 3:   # a mod's monsters (renewal-world's converted bosses) come first
    mobs = open(sys.argv[3]).read() + "\n" + mobs
blk = next(b for b in re.split(r"\n  - Id: ", mobs)
           if b.split("\n")[0] == want or re.search(r"AegisName: " + re.escape(want) + r"\n", b))
get = lambda k: (re.search(r"\n    " + k + r": ([^\n]+)", blk) or [0, ""])[1]
race, ele, size = get("Race"), get("Element") or "Neutral", get("Size") or "Small"

# common cards (+20 % race, +20 % element, +15 % size): the ones a level-80 player can buy
RACE = {"Insect": 4063, "Demon": 4111, "Plant": 4068, "Fish": 4080, "Formless": 4007,
        "Dragon": 4118, "Brute": 4060, "Demihuman": 4035, "DemiHuman": 4035}
ELE = {"Wind": 4030, "Fire": 4049, "Poison": 4062, "Earth": 4065, "Water": 4069,
       "Holy": 4085, "Ghost": 4202, "Dark": 4005}
SIZE = {"Small": 4082, "Medium": 4092, "Large": 4126}
picks = [(20, "race " + race, RACE.get(race)), (20, "element " + ele, ELE.get(ele)),
         (15, "size " + size, SIZE.get(size))]
picks = [p for p in picks if p[2]]
picks.sort(key=lambda p: -p[0])
two = (picks + picks)[:2] if len(picks) == 1 else picks[:2]
print(f"{want}: {race}, {ele} {get('ElementLevel')}, {size} -> " +
      ", ".join(f"{p[1]} +{p[0]}% ({p[2]})" for p in two), file=sys.stderr)
print(":".join(str(p[2]) for p in two))
