#!/usr/bin/env python3
"""calibrate.py: experience for converted monsters from party fight results.

    calibrate.py --rathena DIR --mod DIR --refs 1197,1196,1216 --pay 1.25 \\
                 --monsters 2197,2199 [--single 2153] --note "mid band, party at 54" results.jsonl...

time a kill: the median seconds per kill of the x1 runs and of the x3 runs (or the
largest pack run), averaged; --single monsters use x1 only (few on their map, or
they teleport away from a pack). rate: the mean over --refs of base experience over
their median seconds per kill in packs. risk: 1 + 0.25 x (1 - the median lowest HP in
the packs). Base EXP = pay x rate x time x risk; Job EXP keeps the conversion's ratio.
Prints CSV rows (AegisName,BaseExp,JobExp,note) for monsters.csv.
"""
import argparse, collections, json, re, statistics as st


def exps(path):
    out, cur = {}, None
    for l in open(path, encoding="utf-8"):
        m = re.match(r"^  - Id: (\d+)", l)
        if m:
            cur = int(m[1]); out[cur] = {}
        m = re.match(r"^    (AegisName|BaseExp|JobExp): (\S+)", l)
        if m and cur:
            out[cur][m[1]] = m[2]
    return out


ap = argparse.ArgumentParser()
ap.add_argument("--rathena", required=True)
ap.add_argument("--mod", required=True)
ap.add_argument("--refs", required=True)
ap.add_argument("--monsters", required=True)
ap.add_argument("--single", default="")
ap.add_argument("--pay", type=float, default=1.25)
ap.add_argument("--note", default="")
ap.add_argument("files", nargs="+")
a = ap.parse_args()
pre = exps(a.rathena + "/db/pre-re/mob_db.yml")
new = exps(a.mod + "/db/mob_db.yml")
runs = collections.defaultdict(list)
for f in a.files:
    for l in open(f):
        r = json.loads(l)
        k = r["count"] - r["left"]
        low = min(v[0] for kk, v in r["min_hp_sp_pct"].items() if not kk.startswith("Rig"))
        runs[(r["mob"], r["count"])].append((r["seconds"] / k if k else 360.0, low))
refs = [int(x) for x in a.refs.split(",")]
pack = lambda m: max((c for (mm, c) in runs if mm == m and c > 1), default=None)
rate = st.mean(int(pre[m]["BaseExp"]) / st.median(t for t, _ in runs[(m, pack(m))]) for m in refs)
names = ", ".join(pre[m]["AegisName"].replace("_", " ").title() for m in refs)
single = {int(x) for x in a.single.split(",") if x}
for m in (int(x) for x in a.monsters.split(",")):
    if not runs[(m, 1)]:   # packs only
        tp = st.median(t for t, _ in runs[(m, pack(m))])
        t, low, how = tp, st.median(l for _, l in runs[(m, pack(m))]), f"{tp:.1f} s a kill in packs of {pack(m)}"
        risk = 1 + 0.25 * (1 - low / 100)
        be = round(a.pay * rate * t * risk, -1)
        je = round(be * int(new[m]["JobExp"]) / int(new[m]["BaseExp"]), -1)
        print(f'{new[m]["AegisName"]},{int(be)},{int(je)},"calibrated ({a.note}): {how}, {a.pay}x the rate at {names} ({rate:.0f}/s), risk x{risk:.2f}"')
        continue
    t1 = st.median(t for t, _ in runs[(m, 1)])
    if m in single or pack(m) is None:
        t, low, how = t1, st.median(l for _, l in runs[(m, 1)]), f"{t1:.1f} s a kill alone"
    else:
        tp = st.median(t for t, _ in runs[(m, pack(m))])
        t, low = (t1 + tp) / 2, st.median(l for _, l in runs[(m, pack(m))])
        how = f"{t:.1f} s a kill (x1 {t1:.1f}, x{pack(m)} {tp:.1f})"
    risk = 1 + 0.25 * (1 - low / 100)
    be = round(a.pay * rate * t * risk, -1)
    je = round(be * int(new[m]["JobExp"]) / int(new[m]["BaseExp"]), -1)
    note = f"calibrated ({a.note}): {how}, {a.pay}x the rate at {names} ({rate:.0f}/s), risk x{risk:.2f}"
    print(f'{new[m]["AegisName"]},{int(be)},{int(je)},"{note}"')
