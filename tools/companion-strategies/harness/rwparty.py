#!/usr/bin/env python3
"""rwparty.py <party> <mob:count> [<mob:count> ...]

The owner (a Lord Knight of gear tier 1-3, played by roclient) and drafted
companions fight packs on guild_vs1, one scenario at a time. Before each pack the
party is raised and healed. The owner auto-attacks the nearest monster; the
companions do what their plans say.

party: comma list of job_id:name:role[:sex[:STR/AGI/VIT/INT/DEX/LUK]],
  e.g. 4008:Tank:tank:m,4009:Hela:support:f,4016:Ash:attacker:m:99/1/30/60/70/1
Env: LIMIT (seconds per pack, default 180), STATUS (poll interval, default 2),
REJOIN (seconds a pack monster may stay out of sight before it is set back beside
the party: bosses teleport away), ATTRITION (seconds: a member who falls is back up that long after, and a wipe does
not end the fight; for bosses, BOSSES.md).
Prints one JSON line per scenario."""
import json, os, queue, re, subprocess, sys, threading, time

tier, party, scen = "-", sys.argv[1], sys.argv[2:]
LIMIT = float(os.environ.get("LIMIT", "180"))
POLL = float(os.environ.get("STATUS", "2"))
HERE = os.path.dirname(os.path.abspath(__file__))
USER = os.environ.get("RUSER", "gmtest")
p = subprocess.Popen(["python3", "roclient.py", "--user", USER, "--pass", USER + "123", "run", "-"], cwd=HERE,
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
q = queue.Queue()
threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()


def send(*lines):
    for l in lines:
        p.stdin.write(l + "\n")
    p.stdin.flush()


def drain(sec):
    out, end = [], time.time() + sec
    while time.time() < end:
        try:
            l = q.get(timeout=max(0.01, end - time.time()))
        except queue.Empty:
            break
        try:
            out.append(json.loads(l))
        except ValueError:
            pass
    return out


def texts(evs):
    return [e.get("text", "") for e in evs if e.get("ev") == "text"]


# The owner only watches: hidden, standing still. Old companions are removed, the party drafted
# fresh (a restart brings saved ones back under other names), roles set in party chat.
LEVEL = int(os.environ.get("LEVEL", "99"))   # the party's base level; companions are drafted at the owner's
# Above 99 the owner needs a job whose cap is 175 (a Novice stops at 99, and a draft comes at its owner's level).
OWNER_JOB = 4060 if LEVEL > 99 else 0
send("say @allskill", "wait 1", f"say @party rwparty{USER}", f"say @jobchange {OWNER_JOB}", "say @blvl -275", f"say @blvl {LEVEL - 1}", f"whisper npc:RwTest gospot#{os.environ.get('MAP', 'alb2trea')}", "wait 2",
     "say @companion list raw", "wait 1")
old = [t.split("|")[1] for t in texts(drain(5)) if t.startswith("@CP|")]
for nm in sorted(set(old)):
    send(f"say @companion remove {nm}", "wait 1")
# The engine drafts third classes and expanded advancements itself (NEEDS.md 19). DRAFT_VIA=jobchange is the
# older way round: draft the transcendent or base class and change its job by GM command (it keeps that
# class's skill choice, so the member plays none of its new skills).
DRAFT_PARENT = {4060: 4008, 4061: 4010, 4062: 4012, 4063: 4009, 4064: 4011, 4065: 4013, 4073: 4015, 4074: 4017,
                4075: 4020, 4076: 4021, 4077: 4016, 4078: 4019, 4079: 4018, 4211: 25, 4212: 25, 4215: 24,
                4239: 4047, 4240: 4049}
VIA = os.environ.get("DRAFT_VIA", "direct")
changed = []
for m in party.split(","):
    jid, name, role, *sex = m.split(":")
    parent = DRAFT_PARENT.get(int(jid)) if VIA == "jobchange" else None
    send(f"say @companion draft {parent or jid} {name} {sex[0] if sex else ''}".strip(), "wait 1")
    if parent:
        changed.append((name, jid))
send("wait 4")
for name, jid in changed:
    send(f"say #jobchange {name} {jid}", "wait 1")
# MEMBER_LEVELS=Name:99,...: that member's own base level (a 99/70 member in a party above 99).
# JOBLV=n: the job level of the third classes and advancements (they start again at 1 after the
# change; unset: the cap). Every other member is at its job's cap.
MEMBER_LEVELS = dict(x.split(":") for x in os.environ.get("MEMBER_LEVELS", "").split(",") if x)
JOBLV = int(os.environ.get("JOBLV") or 0)
NEW_JOBS = set(DRAFT_PARENT) | {4190}
for m in party.split(","):
    # exactly LEVEL: "#blvl 98" used to stop at the cap of 99, which the third classes no longer have
    send(f"whisper npc:RwTest setlevel#{m.split(':')[1]}#{MEMBER_LEVELS.get(m.split(':')[1], LEVEL)}")
    if JOBLV and int(m.split(':')[0]) in NEW_JOBS:
        send(f"say #joblvl {m.split(':')[1]} -99", f"say #joblvl {m.split(':')[1]} {JOBLV - 1}")
    else:
        send(f"say #joblvl {m.split(':')[1]} 69")   # to the job's cap
send("wait 2")
# SKILLS_OFF=Name:SKILL,Name:SKILL unticks those skills in the companions' selection
# (a build: a Champion without Chain Combo plays the Asura plan)
for pair in [x for x in os.environ.get("SKILLS_OFF", "").split(",") if x]:
    nm, sk = pair.split(":")
    send(f"say @companion skills {nm} toggle {sk}", "wait 1")
# job:name:role:sex:STR/AGI/VIT/INT/DEX/LUK sets that companion's build
for m in party.split(","):
    f = m.split(":")
    if len(f) > 4 and f[4]:
        send(f"whisper npc:RwTest setstats#{f[1]}#{f[4].replace('/', ',')}", "wait 1")
# ARMOR_ELE=Ele_Undead gives every member that armour element, as an Evil Druid card
# would (gear a plan cannot switch yet: NEEDS.md)
for m in party.split(","):
    if os.environ.get("ARMOR_ELE"):
        send(f"whisper npc:RwTest armorele#{m.split(':')[1]}#{os.environ['ARMOR_ELE']}", "wait 1")
for m in party.split(","):
    jid, name, role, *sex = m.split(":")
    send(f"party {name} {role}", "wait 1")
send("party attack", "say @hide", "wait 3")
for nm in [x for x in os.environ.get("TRACE", "").split(",") if x]:
    send(f"party {nm} trace", "wait 1")
    if any(f"[{nm}] strategy trace off" in t for t in texts(drain(2))):   # a toggle: it was on
        send(f"party {nm} trace", "wait 1")
hidden = False
for t in texts(drain(12 + 3 * len(party.split(",")) + len(old))):
    if not t.startswith("@CP"):
        print("#", t, file=sys.stderr)
    if t.startswith("Invisible:"):
        hidden = t.endswith("On")
if not hidden:   # @hide toggles: it was on from an earlier run
    send("say @hide", "wait 1")
    print("#", texts(drain(2)), file=sys.stderr)

names = ",".join(m.split(":")[1] for m in party.split(","))
ATTRITION = int(os.environ.get("ATTRITION", "0"))
send(f"whisper npc:RwTest attrition#{ATTRITION}", "wait 1")
REJOIN = int(os.environ.get("REJOIN", "0"))   # seconds before a boss that teleported away is found again
send(f"whisper npc:RwTest rejoin#{REJOIN}", "wait 1")
send(f"whisper npc:RwTest gearof#{names}", "wait 2")
for t in texts(drain(3)):
    if "gearof" in t: print("#", t, file=sys.stderr)
# STOCK=1 (the default): before each pack, top each companion's bag up to a kit a player of
# that job would carry. With Companion inventory on (the rigs' battle_conf), the bag is all a
# companion has: potions, gemstones, catalysts, arrows and traps run out. STOCK=0: no top-up.
# Sized for a 15-minute MVP fight: at 30 White Potions, 10 Blue and 40 Blue Gemstones, a level-80
# Knight and Priest ran dry within 9 minutes of Mistress (itemuse.py).
# Condensed White Potions heal as much as White ones and weigh 2, not 15: with White ones the
# casters started fights above 50 % weight (no natural SP regeneration) and a Hunter's top-up
# was refused (ITEMS.md).
KIT_ALL = "White_Slim_Potion:50,Blue_Potion:10,Green_Potion:20,Panacea:10"   # Blue Potions weigh 15
KITS = {   # by 2-1/2-2 job; a transcendent job takes its base job's kit
    8: "Blue_Gemstone:100,Holy_Water:30",   # Holy Water: Aspersio costs one (none, no Aspersio)                                     # Priest: Safety Wall, Magnus, Pneuma
    9: "Blue_Gemstone:20",                                     # Wizard: Safety Wall
    16: "Blue_Gemstone:30,Yellow_Gemstone:30,Yellow_Live:30,Boody_Red:30,Crystal_Blue:15,Wind_Of_Verdure:15",
    # Hunter: what fits (a Sniper with the engine's 500 of every arrow and trap carried 2,280 and
    # had every bow skill refused); the arrows the engine stocks and the kit does not, to 0
    11: "Arrow:1000,Silver_Arrow:500,Fire_Arrow:300,Stone_Arrow:300,Crystal_Arrow:300,Booby_Trap:60,"
        "Steel_Arrow:0,Arrow_Of_Wind:0,Immatrial_Arrow:0,Rusty_Arrow:0,Arrow_Of_Shadow:0,Oridecon_Arrow:0",
    19: "Arrow:2000", 20: "Arrow:2000",
    24: "Bullet:3000,Silver_Bullet:1000",   # Gunslinger; Silver (Holy) for Undead (with both, it shot plain ones at Mistress)
}
# A third class or an expanded advancement carries and wears what the class it comes from does.
BASE2 = {4060: 7, 4061: 9, 4062: 11, 4063: 8, 4064: 10, 4065: 12, 4073: 14, 4074: 16, 4075: 19, 4076: 20,
         4077: 15, 4078: 18, 4079: 17, 4211: 25, 4212: 25, 4215: 24, 4239: 4047, 4240: 4049, 4190: 23}
def base2(jid):
    jid = int(jid)
    return BASE2.get(jid, jid - 4001 if 4008 <= jid <= 4022 else jid)
def kit(jid):
    return ",".join(k for k in (KIT_ALL, KITS.get(base2(jid))) if k)
STOCK = os.environ.get("STOCK", "1") != "0"
# ARM=Name:item:refine:card1:card2[,...]: a weapon of the player's making for those companions,
# put on before the first pack (e.g. Gs:13105:7:4063:4030, a +7 The Garrison with Caramel and
# Mandragora). The engine's gear sets give some jobs poor weapons.
# GEAR=mid: the reference parties' fixed gear, so two runs measure the same party (the engine's
# gear sets give each server different weapons: a Hunter an ATK 29 or an ATK 90 bow). Physical
# damage dealers: a +7 slotted shop weapon with GEAR_CARDS (bosscards.py picks them for the
# boss); casters: a +4 Arc Wand; everyone: a +4 Muffler with a Raydric card (-20 % Neutral, which
# is what a monster's normal attack is). ARM entries below come after and win.
GEAR_W = {7: (1172, 7, True),     # Knight: Claymore [2]
          14: (1408, 7, True),    # Crusader: Pike [4] with a Shield [1] below (a two-handed sword took its shield away, and
                                  # with it Auto Guard and every spear and shield skill of a Paladin or Royal Guard)
          11: (1715, 7, True),    # Hunter: Arbalest [2]
          24: (13105, 7, True),   # Gunslinger: The Garrison [2]
          12: (1253, 7, True),    # Assassin: Katar [2]
          8: (1611, 4, False), 9: (1611, 4, False), 16: (1611, 4, False)}   # Arc Wand [2]
gear = []
if os.environ.get("GEAR") == "mid":
    c = (os.environ.get("GEAR_CARDS", "0:0") + ":0").split(":")[:2]
    for m in party.split(","):
        jid, name = int(m.split(":")[0]), m.split(":")[1]
        w = GEAR_W.get(base2(jid))
        if w:
            gear.append(f"{name}:{w[0]}:{w[1]}:" + (f"{c[0]}:{c[1]}" if w[2] else "0:0"))
        if base2(jid) == 14:
            gear.append(f"{name}:2106:4:0:0")
        gear.append(f"{name}:2504:4:4133:0")
for spec in gear + [x for x in os.environ.get("ARM", "").split(",") if x]:
    send(f"whisper npc:RwTest arm#{spec.replace(':', '#')}", "wait 2")
for t in texts(drain(2)):
    if "RwTest: arm" in t: print("#", t, file=sys.stderr)


LOG = os.path.join(HERE, "logs", f"client-{USER}.jsonl")
LOG_FROM = os.path.getsize(LOG) if os.path.exists(LOG) else 0
results = []
for sc in scen:
    mob, n = sc.split(":")
    if ATTRITION:   # a boss fight: a fresh spot, away from the last fight's ground spells (a Land Protector lasts 345 s)
        send(f"whisper npc:RwTest gospot#{os.environ.get('MAP', 'alb2trea')}", "wait 3")
    if STOCK:
        for m in party.split(","):
            # a whisper carries at most about 255 characters: a long kit goes in several
            parts, cur = [], []
            for item in kit(m.split(':')[0]).split(","):
                if cur and len(",".join(cur + [item])) > 150:
                    parts.append(",".join(cur)); cur = []
                cur.append(item)
            for part in parts + [",".join(cur)]:
                send(f"whisper npc:RwTest stock#{m.split(':')[1]}#{part}", "wait 1")
        for t in texts(drain(2)):
            if "RwTest: stock" in t: print("#", t, file=sys.stderr)
    send(f"whisper npc:RwTest restore#{names}", "wait 4", f"whisper npc:RwTest pack#{mob}#{n}" + (f"#{os.environ['START_HP']}" if os.environ.get("START_HP") else ""), "wait 1")
    # Wait for the test NPC's own "pack" line: the client works its commands off one after
    # another and runs seconds behind after the stocking, so status lines of the pack before
    # (left=0) are still arriving. Counted as this pack's, they ended it at once with the old
    # pack's time.
    synced, until = False, time.time() + 90
    while not synced and time.time() < until:
        synced = any(t.startswith(f"RwTest: pack {mob} x{n}") for t in texts(drain(1)))
    if not synced:
        print(f"# no pack line for {mob} x{n}", file=sys.stderr)
    t0 = time.time()
    last = None
    mins = {}
    down, falls, back = {}, 0, 0   # attrition: who is down since when, and how many times anyone fell
    taken = healed = dealt = 0     # damage the monsters did to the party, what Heal and Sanctuary gave back, damage to the pack
    maxhp = {}
    while time.time() - t0 < LIMIT:
        if os.environ.get("PROBE"):   # PROBE=lpcells: another test-NPC command each poll, its answer to stderr
            send(f"whisper npc:RwTest {os.environ['PROBE']}")
        send(f"whisper npc:RwTest status#{names}", f"wait {POLL}")
        evs = drain(POLL + 0.5)
        if os.environ.get("TRACE"):
            for e in evs:
                if e.get("ev") == "text" and e.get("kind") in ("party", "self", "whisper") and not e["text"].startswith(("RwTest", "@CP")):
                    print(f"  [{round(time.time() - t0)}s] {e['text']}", file=sys.stderr)
        for t in texts(evs):
            if os.environ.get("PROBE") and t.startswith("RwTest: " + os.environ["PROBE"].split("#")[0]):
                print(f"  [{round(time.time() - t0)}s] {t}", file=sys.stderr)
            if t.startswith("RwTest: status+") and last:   # the members past the first line's room
                last += t[len("RwTest: status+"):]
            elif t.startswith("RwTest: status"):
                last = t
            if t.startswith("RwTest: status"):
                for part in t.split(" | ")[1:]:
                    mm = re.match(r"(.+?) (-?\d+)/(\d+) sp (-?\d+)/(\d+)", part)
                    if mm:
                        nm, hp, mhp, sp, msp = mm[1], *map(int, mm.groups()[1:])
                        maxhp[nm] = mhp
                        lo = mins.setdefault(nm, [100, 100])
                        lo[0] = min(lo[0], round(100 * hp / max(mhp, 1)))
                        lo[1] = min(lo[1], round(100 * sp / max(msp, 1)))
                        if ATTRITION and not nm.startswith("Rig"):
                            if hp <= 0 and nm not in down:
                                down[nm] = time.time(); falls += 1
                            elif hp > 0 and nm in down:
                                down.pop(nm); back += 1
        for nm, since in list(down.items()):
            if time.time() - since >= ATTRITION:
                send(f"whisper npc:RwTest revive#{nm}")
                down[nm] = time.time()   # once more after another wait, if it did not take
        if last:
            left = int(re.search(r"left=(-?\d+)", last)[1])
            alive = [part for part in last.split(" | ")[2:] if not re.search(r" 0/\d+ sp", part)]   # [1] is the hidden owner
            if left <= 0 or (not alive and not ATTRITION):
                break
    m = re.search(r"left=(-?\d+) t=(\d+) deaths=(\d+)(?: rejoins=\d+)? who=(\S*)", last or "")
    res = {"tier": tier, "mob": int(mob) if mob.isdigit() else mob, "count": int(n), "left": int(m[1]) if m else None,
           "seconds": int(m[2]) if m else None, "deaths": falls if ATTRITION else int(m[3]) if m else None,
           "who": [w for w in (m[4] if m else "").split(",") if w], "min_hp_sp_pct": mins,
           "cleared": bool(m) and int(m[1]) <= 0, "rejoins": int(re.search(r"rejoins=(\d+)", last)[1]) if last and "rejoins=" in last else None, **({"back_up": back} if ATTRITION else {}),
           "pack_hp_left_pct": int(re.search(r"packhp=(-?\d+)", last)[1]) if last and "packhp=" in last else None,
           "taken": None, "healed": None, "dealt": None, "max_hp": maxhp}
    ms = re.search(r" ms=(\d+)", last or "")
    if ms and res["cleared"]:
        res["seconds"] = round(int(ms[1]) / 1000, 1)   # the last kill's own time, not the poll's
    results.append(res)
send(f"whisper npc:RwTest restore#{names}", "wait 2", "quit")
p.wait(timeout=30)
# Damage and healing come from the client's own log, which has every event but runs behind the
# fight: read after the session, a fight being everything from its "RwTest: pack" line to the next.
fights = []
if os.path.exists(LOG):
    with open(LOG) as fh:
        fh.seek(LOG_FROM)
        for l in fh:
            try:
                e = json.loads(l)
            except ValueError:
                continue
            if e.get("ev") == "text" and e.get("text", "").startswith("RwTest: pack "):
                fights.append({"taken": 0, "healed": 0, "dealt": 0})
            if not fights:
                continue
            f, src, tg = fights[-1], e.get("src", 0), e.get("target", 0)
            # party members have ids below 110000000, monsters above, ground-spell units far below
            if e.get("ev") in ("damage", "skill_damage") and (e.get("damage") or 0) > 0:
                if 0 < tg < 110000000 and (src >= 110000000 or src < 1000000):
                    f["taken"] += e["damage"] + (e.get("damage2") or 0)
                elif tg >= 110000000:
                    f["dealt"] += e["damage"] + (e.get("damage2") or 0)
            elif e.get("ev") == "skill_nodamage" and e.get("skill") in (28, 70, 2051, 2043) and 0 < tg < 110000000:
                f["healed"] += e.get("value") or 0   # Heal, Sanctuary, Highness Heal, Coluceo Heal
for i, res in enumerate(results):
    if len(fights) == len(results):
        res.update(fights[i])
    print(json.dumps(res), flush=True)
