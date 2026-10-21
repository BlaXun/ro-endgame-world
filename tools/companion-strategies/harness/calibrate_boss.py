#!/usr/bin/env python3
"""calibrate_boss.py: a converted boss's HP, attack and experience from attrition fights.

    calibrate_boss.py --rathena DIR --mod DIR --boss 2156 --refs 1159,1046,1087 \\
                      [--pay 1.25] [--note "..."] results.jsonl...

The results are rwsuite.py --attrition runs (BOSSES.md): the same party fights the
boss and pre-renewal reference bosses of its kind and level, fallen members get back
up, and each fight gives two numbers: the boss's HP the party takes off a minute
(wear) and how often a member falls a minute (falls).

  Attack  first. A party that is down cannot wear anything, so while the boss's falls
          are above 1.5 x the references' median + 0.5 a minute, attack x (median /
          falls) ^ 0.7, bounded to 0.5-2, HP stays, and a retest.
  Hp      then. Wear scales with 1/HP, so HP x (the boss's wear / the references'
          median) puts it at the references' median.
  BaseExp what the references pay per minute of fight (their base experience over
          their time to kill, 100 / wear), median, x pay, x the boss's time to kill
          at the calibrated HP (the references' median).
  JobExp  BaseExp x the references' median job/base. MvpExp follows in the
          converter (half the base, as every pre-renewal MVP).

Prints a summary, then a CSV row for monsters.csv (AegisName,Hp,Attack,BaseExp,JobExp,note).
"""
import argparse, collections, csv, json, re, statistics as st, sys


def mobs(path):
    out, cur = {}, None
    for l in open(path, encoding="utf-8"):
        m = re.match(r"^  - Id: (\d+)", l)
        if m:
            cur = int(m[1]); out[cur] = {}
        m = re.match(r"^    (AegisName|Hp|Attack|BaseExp|JobExp): (\S+)", l)
        if m and cur:
            out[cur][m[1]] = m[2] if m[1] == "AegisName" else int(m[2])
    return out


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--rathena", required=True)
ap.add_argument("--mod", required=True)
ap.add_argument("--boss", type=int, required=True)
ap.add_argument("--refs", required=True)
ap.add_argument("--pay", type=float, default=1.0)
ap.add_argument("--note", default="")
ap.add_argument("files", nargs="+")
a = ap.parse_args()
pre = mobs(a.rathena + "/db/pre-re/mob_db.yml")
new = mobs(a.mod + "/db/mob_db.yml")
runs = collections.defaultdict(list)
for f in a.files:
    for l in open(f):
        r = json.loads(l)
        mins = max(r["seconds"], 1) / 60
        wear = 100 / mins if r["cleared"] else (100 - (r["pack_hp_left_pct"] or 0)) / mins
        runs[r["mob"]].append((wear, r["deaths"] / mins))
refs = [int(x) for x in a.refs.split(",")]
missing = [m for m in refs + [a.boss] if not runs[m]]
if missing:
    sys.exit(f"no results for {missing}")
wear = {m: st.median(w for w, _ in runs[m]) for m in refs + [a.boss]}
falls = {m: st.median(f for _, f in runs[m]) for m in refs + [a.boss]}
for m in refs + [a.boss]:
    name = (new.get(m) or pre[m])["AegisName"]
    print(f"# {m} {name:20s} wear {wear[m]:6.1f} %/min  falls {falls[m]:5.2f}/min  runs {len(runs[m])}", file=sys.stderr)
w_ref, f_ref = st.median(wear[m] for m in refs), st.median(falls[m] for m in refs)
f_lo, f_hi = min(falls[m] for m in refs), max(falls[m] for m in refs)
b = new[a.boss]
if wear[a.boss] <= 0:
    sys.exit(f"{b['AegisName']}: the party took nothing off it; a plan first (BOSSES.md)")
hp = round(b["Hp"] * wear[a.boss] / w_ref, -2)
atk = b["Attack"]
if falls[a.boss] > 1.5 * f_ref + 0.5:
    atk = round(atk * min(2, max(0.5, ((f_ref + 0.05) / (falls[a.boss] + 0.05)) ** 0.7)))
    hp = b["Hp"]
t_kill = 6000 / w_ref   # seconds, at the calibrated HP
rate = st.median(pre[m]["BaseExp"] / (6000 / wear[m]) for m in refs)
be = round(a.pay * rate * t_kill, -1)
je = round(be * st.median(pre[m]["JobExp"] / pre[m]["BaseExp"] for m in refs), -1)
names = ", ".join(pre[m]["AegisName"].replace("_", " ").title() for m in refs)
state = "within the references' falls" if atk == b["Attack"] else f"attack {b['Attack']} -> {atk}, retest"
print(f"# {b['AegisName']}: HP {b['Hp']} -> {int(hp)}; {state}; {t_kill:.0f} s to kill; "
      f"references wear {w_ref:.1f} %/min, falls {f_ref:.2f}/min ({f_lo:.2f}-{f_hi:.2f})", file=sys.stderr)
note = (f"boss calibrated ({a.note}): wear {wear[a.boss]:.1f} %/min at HP {b['Hp']}, falls {falls[a.boss]:.2f}/min; "
        f"references {names}: wear {w_ref:.1f}, falls {f_ref:.2f} ({f_lo:.2f}-{f_hi:.2f}); "
        f"{a.pay}x their {rate:.0f} exp/s over {t_kill:.0f} s")
csv.writer(sys.stdout, lineterminator="\n").writerow([b["AegisName"], int(hp), atk, int(be), int(je), note])
