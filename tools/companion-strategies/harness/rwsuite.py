#!/usr/bin/env python3
"""rwsuite.py: one region's party test on several test servers at once.

    rwsuite.py --tag dewata --level 48 --party 7:Kn:tank:m,8:Pri:support:f,... \\
               --plans tuned|baseline --load 2151:1 2151:3 ... [--no-load]

Each server (--rigs, default the three in the scratchpad) runs the whole list once,
so three servers give three runs of every pack. With --load (the default) it first
merges the plans (companion-roles, then every *.yml in companion-strategies/ in
PLAN_ORDER) and restarts each server with renewal-world, the plans and the test NPC.
Results go to <out>/<tag>_<rig>.jsonl; a summary per pack is printed: median time a
pack took, how many runs cleared it, how many wiped, and the lowest HP anyone reached.
"""
import argparse, collections, json, os, statistics, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "../../.."))
# the ragnarokoffline.app checkout and ro-endgame-classes, beside this repository unless set
APP = os.environ.get("RO_APP") or os.path.join(os.path.dirname(ROOT), "ragnarokoffline.app")
CLASSES = os.environ.get("RO_CLASSES") or os.path.join(os.path.dirname(ROOT), "ro-endgame-classes")
# The monster mods, in dependency order (build_monsters.py writes all four).
# The class mods, in dependency order: what lets the test parties level past 99.
CLASS_MODS = ("level175-core", "transcendent-third-classes", "expanded-classes")
RW_MODS = ["renewal-world-monsters", "renewal-world-minibosses", "renewal-world-mvps", "renewal-world-gear", "renewal-world-cards"]
PLAN_ORDER = ["everyday-party.yml", "bifrost-fields.party.yml", "eclage.party.yml", "dewata.party.yml", "rockridge.party.yml"]


def merge_plans(out_dir, which, roles=None, extra=()):
    os.makedirs(os.path.join(out_dir, "db"), exist_ok=True)
    roles = roles or os.path.join(APP, "examples/mods/companion-roles/db/population_strategy.yml")
    parts = [open(roles).read().rstrip("\n")]
    for f in extra:   # another mod's plans, as if installed after companion-roles
        parts.append(open(f).read().split("\nBody:\n", 1)[1].rstrip("\n"))
    if which == "tuned":
        sdir = os.path.join(ROOT, "tools/companion-strategies")
        files = PLAN_ORDER + sorted(f for f in os.listdir(sdir) if f.endswith(".yml") and f not in PLAN_ORDER)
        for f in files:
            parts.append(open(os.path.join(sdir, f)).read().split("\nBody:\n", 1)[1].rstrip("\n"))
    open(os.path.join(out_dir, "db/population_strategy.yml"), "w").write("\n\n".join(parts) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--level", type=int, default=99)
    ap.add_argument("--party", required=True)
    ap.add_argument("--plans", default="tuned", choices=["tuned", "baseline"])
    ap.add_argument("--rigs", default=os.environ.get("RIGS", ""))
    ap.add_argument("--out", default=os.environ.get("SUITE_OUT", "."))
    ap.add_argument("--limit", type=int, default=180)
    ap.add_argument("--no-load", action="store_true")
    ap.add_argument("--extra", default=os.environ.get("EXTRA_PLANS", ""),
                    help="comma list of other mods' population_strategy.yml to load after companion-roles")
    ap.add_argument("--roles", default=os.environ.get("ROLES"),
                    help="companion-roles' population_strategy.yml to use (another branch's engine)")
    ap.add_argument("--mod", default=",".join(os.path.join(ROOT, "mods", m) for m in RW_MODS),
                    help="comma list of the renewal-world monster mods to load, in dependency order (default: "
                         "the four; a copy with bosses on, for BOSSES.md)")
    ap.add_argument("--mods", default=os.environ.get("MODS", ",".join(os.path.join(CLASSES, "mods", m) for m in CLASS_MODS)),
                    help="comma list of mods loaded before --mod (default: the class mods; '' for none)")
    ap.add_argument("--rejoin", type=int, default=0,
                    help="seconds a boss that teleported away stays lost before it is set back beside the party")
    ap.add_argument("--attrition", type=int, default=0,
                    help="seconds: fallen members get back up and a wipe does not end the fight (bosses)")
    ap.add_argument("--env", default="", help="extra env for rwparty, e.g. SKILLS_OFF=Ash:MO_CHAINCOMBO")
    ap.add_argument("packs", nargs="+")
    a = ap.parse_args()
    rigs = [r for r in a.rigs.split(",") if r]
    if not a.no_load:
        plans = os.path.join(a.out, f"plans_{a.plans}")
        merge_plans(plans, a.plans, a.roles, [f for f in a.extra.split(",") if f])
        for r in rigs:
            p = subprocess.run([os.path.join(r, "up.sh")] + [m for m in a.mods.split(",") if m] + [m for m in a.mod.split(",") if m] + [plans,
                                os.path.join(r, "rwtest")], capture_output=True, text=True)
            bad = [l for l in p.stdout.splitlines() if ("Error" in l or "Warning" in l) and "Recruiter" not in l
                   and "disablenpc" not in l and "s1/p1" not in l and "inter-server" not in l and "mesitem" not in l]
            if p.returncode or bad:
                print(f"{r}: up.sh: {p.returncode} {bad[:5]}", file=sys.stderr)
    env = dict(os.environ, LEVEL=str(a.level), LIMIT=str(a.limit), ATTRITION=str(a.attrition), REJOIN=str(a.rejoin))
    for kv in [x for x in a.env.split(";") if x]:
        k, v = kv.split("=", 1); env[k] = v
    procs = []
    for r in rigs:
        out = open(os.path.join(a.out, f"{a.tag}_{os.path.basename(r)}.jsonl"), "w")
        procs.append(subprocess.Popen(["python3", "rwparty.py", a.party] + a.packs, cwd=r, env=env,
                                      stdout=out, stderr=subprocess.DEVNULL))
    for p in procs:
        p.wait()
    d = collections.defaultdict(list)
    if a.attrition:   # a boss: its HP the party takes off a minute, and how often a member falls
        for r in rigs:
            for l in open(os.path.join(a.out, f"{a.tag}_{os.path.basename(r)}.jsonl")):
                x = json.loads(l)
                if x["seconds"] is None:   # no status came back: the test NPC did not load
                    print(f"{x['mob']}: no status from the test NPC", file=sys.stderr)
                    continue
                mins = max(x["seconds"], 1) / 60
                start = int(os.environ.get("START_HP") or 100)   # a later phase started below 100 %
                taken = start if x["cleared"] else start - (x["pack_hp_left_pct"] or 0)
                d[x["mob"]].append((taken / mins, x["deaths"] / mins, x["seconds"] if x["cleared"] else None))
        for mob, v in d.items():
            kills = [k for *_, k in v if k]
            print(f"{mob}: HP {statistics.median(h for h, _, _ in v):.1f} %/min ({' '.join(f'{h:.1f}' for h, _, _ in v)})  "
                  f"falls {statistics.median(f for _, f, _ in v):.2f}/min ({' '.join(f'{f:.2f}' for _, f, _ in v)})"
                  + (f"  killed in {' '.join(map(str, kills))} s" if kills else ""))
        return
    for r in rigs:
        for l in open(os.path.join(a.out, f"{a.tag}_{os.path.basename(r)}.jsonl")):
            x = json.loads(l)
            low = min(v[0] for k, v in x["min_hp_sp_pct"].items() if not k.startswith("Rig"))
            d[(x["mob"], x["count"])].append((x["seconds"], x["cleared"], x["left"] == x["count"] and x["seconds"] < a.limit - 8, low))
    for (mob, n), v in d.items():
        cleared = [s for s, c, w, l in v if c]
        print(f"{mob} x{n}: cleared {len(cleared)}/{len(v)}  wiped {sum(1 for _, _, w, _ in v if w)}  "
              f"median {statistics.median(cleared) if cleared else '-'}s  lowest HP {min(l for *_, l in v)}%  "
              f"runs {' '.join(str(s) + ('' if c else ('W' if w else 'x')) for s, c, w, _ in v)}")


if __name__ == "__main__":
    main()
