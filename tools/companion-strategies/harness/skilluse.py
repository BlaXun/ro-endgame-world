#!/usr/bin/env python3
"""skilluse.py <rig dir> [user]: what each party member cast in the rig's last client session, by skill name."""
import collections, json, os, re, sys
rig = sys.argv[1]; user = sys.argv[2] if len(sys.argv) > 2 else "gmtest"
names = {}
for rel in ("rathena/db/pre-re/skill_db.yml", "rathena/db/import/skill_db.yml"):
    try:
        for m in re.finditer(r"- Id: (\d+)\s*\n\s+Name: (\S+)", open(os.path.join(rig, rel), encoding="utf-8", errors="replace").read()):
            names[int(m.group(1))] = m.group(2)
    except OSError:
        pass
lines = open(os.path.join(rig, "logs/client-%s.jsonl" % user), encoding="utf-8", errors="replace").read().splitlines()
start = max((i for i, l in enumerate(lines) if '"ev": "login_ok"' in l or '"map_entered"' in l), default=0)
who, use, dmg = {}, collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
for l in lines[start:]:
    try:
        e = json.loads(l)
    except ValueError:
        continue
    if e.get("ev") == "spawn" and e.get("name"):   # a member shows under a drawn name: tell it by its job
        who[e["id"]] = ("job %s %s" % (e.get("class"), e["name"])) if e.get("objtype") == 0 else e["name"]
    if e.get("ev") in ("skill_damage", "skill_nodamage", "skill_ground"):
        use[e.get("src")][e.get("skill")] += 1
        if e.get("ev") == "skill_damage":
            dmg[e.get("src")][e.get("skill")] += max(0, e.get("damage", 0))
    if e.get("ev") == "damage" and e.get("damage", 0) > 0:
        use[e.get("src")]["attack"] += 1
        dmg[e.get("src")]["attack"] += e["damage"]
for src in sorted(use, key=lambda s: str(who.get(s, s))):
    if src not in who:
        continue
    print("%-22s %s" % (who[src], ", ".join("%s x%d%s" % (names.get(k, k), n, (" (%d dmg)" % dmg[src][k]) if dmg[src][k] else "")
                                            for k, n in use[src].most_common(14))))
