#!/usr/bin/env python3
"""whohurts.py <rig>/logs/client-<user>.jsonl [--by-fight]: who did the damage the party
took in the last session of a test client log, by monster and skill; with --by-fight,
for each fight (each pack the test NPC spawned) apart.

A ground spell's damage (Meteor Storm, Fire Pillar, Lord of Vermilion) comes from the
spell's unit, a small id, not from the monster: it is listed as "ground spell".
Negative amounts are heals and are left out."""
import collections, json, sys

L = open(sys.argv[1]).read().splitlines()
# a session starts where the client's clock goes back
starts = [0] + [i for i in range(1, len(L)) if json.loads(L[i]).get("t", 0) < json.loads(L[i - 1]).get("t", 0) - 100]
ev = [json.loads(l) for l in L[starts[-1]:]]
names = {e["id"]: e["name"] for e in ev if "name" in e and "id" in e}
fights = [[]]
for e in ev:
    if "--by-fight" in sys.argv and e.get("ev") == "text" and e.get("text", "").startswith("RwTest: pack "):
        fights.append([e])
    fights[-1].append(e)
fights = [f for f in fights if f] if "--by-fight" not in sys.argv else fights[1:]


def report(ev, title):
  dmg, hits = collections.Counter(), collections.Counter()
  for e in ev:
      src = e.get("src", 0)
      # party members have ids below 110000000, monsters above, ground-spell units far below
      if e.get("ev") in ("damage", "skill_damage") and 0 < e.get("target", 0) < 110000000 \
              and (src >= 110000000 or src < 1000000) and (e.get("damage") or 0) > 0:
          who = names.get(src, "?") if src >= 110000000 else "ground spell"
          k = (who, e.get("skill", 0))
          dmg[k] += e["damage"]; hits[k] += 1
  if title:
      print(f"== {title}")
  tot = sum(dmg.values()) or 1
  for (who, skill), v in dmg.most_common(12):
      print(f"{who:20s} skill {skill:4d}  {v:8d} ({100 * v / tot:.0f}%) in {hits[(who, skill)]} hits")


for f in fights:
    report(f, f[0].get("text", "") if "--by-fight" in sys.argv else "")
