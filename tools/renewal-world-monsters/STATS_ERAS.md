# Monster stats in pre-renewal and renewal, side by side

What each monster stat does in each era, so that a renewal monster or MVP can be
given pre-renewal stats that do the same job. It complements BALANCING.md
(how the converter works) and BOSSES.md (how bosses are weighed).

**Ground truth.** The rAthena source at `development/rathena`, branch
`ragnarokoffline`, commit `c8b69e407`. Every formula carries a `file:line` from
that checkout; paths are relative to `src/map/` unless they start with `db/`,
`conf/` or `src/config/`. The line numbers drift as the fork moves, but the
function names stay put. The irowiki pages explain the official game; where they
disagree with the source, this document follows the source.

**Era switch.** `src/config/renewal.hpp:24` defines `RENEWAL`, and with it
`RENEWAL_CAST` (:37), `RENEWAL_DROP` (:45), `RENEWAL_EXP` (:52),
`RENEWAL_LVDMG` (:58), `RENEWAL_ASPD` (:68) and `RENEWAL_STAT` (:74). A
pre-renewal build (`PRERE`, `./configure --enable-prere`) defines none of them.

**Units.** Hit rates are in %, crit in 0.1 %, status-change rates in 0.01 %
(10000 = 100 %).

**Marks.** *(unverified)* means read from the source but not measured in game.
*(inferred)* means a consequence I worked out that no single line states.

---

## 0. The mob database fields, era by era

| YAML field | pre-renewal meaning | renewal meaning | source |
|---|---|---|---|
| `Attack` | low end of the physical damage range | the middle of it: 80–120 % of Attack | mob.cpp:5143-5150; status.cpp:2522-2549 |
| `Attack2` | **high end of the physical range** | **magic attack** (`rhw.matk`) | mob.cpp:5152-5163 (`#ifdef RENEWAL rhw.matk = atk #else rhw.atk2 = atk`) |
| `Defense` | stored in `defType` = `signed char`: **capped at 127** with a warning | `int16`, up to 32767 | mob.cpp:5165-5177; src/config/const.hpp:46-56 |
| `MagicDefense` | same, capped at 127 | `int16` | mob.cpp:5179-5191 |
| `Resistance`, `MagicResistance` | read, then **never used** | % reduction (4th-job era) | mob.cpp:5193-5210; battle.cpp:5583-5610, 6046-6069 |
| `Str` | **nothing** for a monster (no base ATK, see §8) | adds to base ATK | status.cpp:2424-2492; conf/battle/battle.conf:13-14 |
| `AttackDelay`, `AttackMotion` | same in both eras (§9) | same | mob.cpp:5417-5434 |

The player-side cap `max_def: 99` (conf/battle/player.conf:132, applied in
status.cpp:4587-4606) is for players only. A pre-renewal monster can have DEF or
MDEF up to 127.

---

## 1. Hard DEF and physical damage reduction

### Formulas

Both live in `battle_calc_defense_reduction` (battle.cpp:4721).

| | formula | source |
|---|---|---|
| pre-renewal | `damage = damage × (100 − DEF) / 100 − softDEF`; DEF is first capped at 100 | battle.cpp:4873-4883 |
| renewal | `damage = damage × (4000 + DEF) / (4000 + 10 × DEF) − softDEF` | battle.cpp:4868-4870 |
| renewal, skills flagged `SimpleDefense` | `damage −= DEF + softDEF` (flat) | battle.cpp:4848-4853 |
| renewal only, before DEF | `Res` cuts `Res / (Res + 400) × 80 %` | battle.cpp:5581-5611 |
| both | after DEF the damage is raised to at least 1 | battle.cpp:3579-3589, 4913, 4932 |

Pre-renewal DEF 100 (or anything up to 127) therefore lets through **nothing but
the minimum of 1** (a player's mastery and refine bonuses are added after the
reduction, battle.cpp:4900-4915, so a geared player still does a little). Renewal's
reduction tends toward 90 % and never gets there.

Inverse: the pre-renewal DEF with the same reduction as renewal DEF *D* is
**`DEF_pre = 900·D / (4000 + 10·D)`**, rounded.

### Table

| renewal DEF | renewal reduction | pre-renewal DEF for the same % |
|---:|---:|---:|
| 0 | 0 % | 0 |
| 50 | 10.0 % | 10 |
| 100 | 18.0 % | 18 |
| 200 | 30.0 % | 30 |
| 280 (renewal MVP median) | 37.1 % | 37 |
| 300 | 38.6 % | 39 |
| 500 | 50.0 % | 50 |
| 1000 | 64.3 % | 64 |
| 2000 | 75.0 % | 75 |
| ∞ | → 90 % | 90 |

**Worked example.** Renewal Baphomet has DEF 379 (43.8 %); rAthena's own
pre-renewal Baphomet has DEF 35. The same attack of 1,000 before DEF:
renewal 1000 × 4379 / 7790 = 562 (before soft DEF); pre-renewal with DEF 44:
560; with the stock DEF 35: 650. The official pairs come out close to "same
%", not exact: Dark Lord 330 → 40.7 % vs stock 30, Drake 279 → 37.0 % vs 20,
Lord of Death 336 → 41.1 % vs 77 (db/re/mob_db.yml vs db/pre-re/mob_db.yml).

### What ignores DEF

| | pre-renewal | renewal |
|---|---|---|
| **Critical hits** | **ignore hard AND soft DEF** (`attack_ignores_def` returns true on a crit, battle.cpp:3336-3340) | do **not**; they deal ×1.4 instead (battle.cpp:5646-5658; for monsters also battle.cpp:2631-2632) |
| Skills with `IgnoreDefense` in skill_db | ignore both (battle.cpp:3384) — 20 skills, among them Asura Strike, Acid Terror, Spiral Pierce, Auto Counter, Sacrifice, NPC_CRITICALSLASH, NPC_PIERCINGATT, NPC_EARTHQUAKE | same flag, 43 skills; Asura, Acid Terror, Spiral Pierce, Auto Counter **lose** it; Acid Terror ignores only soft DEF (battle.cpp:4801-4804) |
| "Ice Pick" class: `bDefRatioAtk*` cards/weapons, Investigate, Mass Spiral | damage × (DEF + softDEF)/100 (Investigate ×2): **more DEF = more damage** (battle.cpp:3166-3209, 4874-4877) | damage + DEF × skillratio/200, and the DEF formula is skipped (battle.cpp:4863-4870) |
| `bIgnoreDefRace/Class` (Samurai Spector, etc.) | ignore entirely (battle.cpp:3364-3382) | same |
| `bIgnoreDefRaceRate` (% of DEF) | reduces DEF and soft DEF by % (battle.cpp:4736-4742) | same |

Counts: `IgnoreDefense: true` in db/pre-re/skill_db.yml vs db/re/skill_db.yml.

### Porting

- Convert DEF by the table, never by ratio or by copying the number.
- A converted DEF lands at most at 89, so a renewal monster never becomes
  physically immune in pre-renewal. The reverse trap is a hand-set DEF ≥ 100:
  that is immunity to everything but crits, Ice Pick and DEF-ignoring skills.
- **Crits are the big difference.** In pre-renewal an Assassin Cross with Katar
  crits walks through any DEF; in renewal a high-DEF boss is a wall to crits.
  A boss whose identity is "hard to hurt physically" leaks to crit builds in
  pre-renewal however its DEF is set. Only LUK (§7) stands against that.
- Ice Pick is the mirror: in pre-renewal high DEF *feeds* it.
- `Res` has no pre-renewal counterpart. 110 renewal monsters carry it (98–5000,
  median 1000 = 57 % physical cut). To keep that job, fold it into DEF:
  total kept = (1 − r_res) × (1 − r_def); pre-renewal DEF = 100 × (1 − kept).
  Example: Res 1000 + DEF 300 → 0.429 × 0.614 = 0.263 kept → DEF 74. *(inferred)*

---

## 2. Soft DEF (VIT)

| | monster soft DEF | applied | source |
|---|---|---|---|
| pre-renewal | `def2 = VIT`; per hit `VIT + rnd(0, (VIT/20)² − 1)` (0 extra when VIT < 40) | subtracted after the % cut | status.cpp:2712-2715; battle.cpp:4826-4834, 4878-4883 |
| renewal | `def2 = (Level + VIT) / 2`, fixed | subtracted after the DEF formula | status.cpp:2650-2656; battle.cpp:4835-4837, 4868 |

For comparison, the player's soft DEF: pre-renewal
`⌊0.3·VIT⌋ + rnd(0, ⌊VIT²/150⌋ − ⌊0.3·VIT⌋ − 1) + ⌊VIT/2⌋` (battle.cpp:4809-4813);
renewal `(Level + VIT)/2 + AGI/5` (status.cpp:2654).

| monster | pre-renewal per hit | renewal |
|---|---|---|
| VIT 30 | 30 | Lv 100: 65 |
| VIT 60 | 60–68 | Lv 100: 80; Lv 150: 105 |
| VIT 100 | 100–124 | Lv 150: 125 |
| VIT 200 | 200–299 | Lv 150: 175 |

**Porting.** Soft DEF is a flat amount, so what matters is its size against a
player's hit in that era. Renewal's figure is inflated by the monster's level
(Lv 150 gives 75 on its own). A pre-renewal VIT of
`(Lv_re + VIT_re)/2 × (typical pre-renewal hit / typical renewal hit)` keeps the
proportion *(inferred)*. But VIT does three more jobs in pre-renewal: half of
it is soft MDEF (§4), and it resists Stun, Poison, Silence and Bleeding (§5).
Choose VIT for the resistances first; soft DEF is the least of its jobs.

---

## 3. Hard MDEF and magic damage reduction

Both in `battle_calc_magic_attack` (battle.cpp:5802).

| | formula | source |
|---|---|---|
| pre-renewal | `damage = damage × (100 − MDEF)/100 − softMDEF` (no cap: MDEF > 100 goes negative) | battle.cpp:6107-6116 |
| renewal | `damage = damage × (1000 + MDEF)/(1000 + 10·MDEF) − softMDEF`; negative MDEF counts as 0 | battle.cpp:6097-6106 |
| renewal only, before MDEF | `MRes` cuts `MRes/(MRes + 400) × 80 %` | battle.cpp:6046-6069 |
| both | at least 1 per hit | battle.cpp:6210-6211 |

So pre-renewal MDEF ≥ 100 means **1 damage per hit from every spell**. It also
means immunity to Freeze and Stone (§5). Among 1004 pre-renewal monsters only
E_HYDRA has MDEF ≥ 100; 392 of 2698 renewal monsters do.

Inverse: **`MDEF_pre = 900·M / (1000 + 10·M)`**, rounded.

| renewal MDEF | renewal reduction | pre-renewal MDEF for the same % |
|---:|---:|---:|
| 0 | 0 % | 0 |
| 25 | 18.0 % | 18 |
| 50 | 30.0 % | 30 |
| 100 | 45.0 % | 45 |
| 134 (renewal MVP median) | 51.5 % | 52 |
| 200 | 60.0 % | 60 |
| 300 | 67.5 % | 68 |
| 800 | 80.0 % | 80 |

**Worked example.** Renewal Osiris: MDEF 164 → 55.9 %; stock pre-renewal
Osiris MDEF 25. A 3,000-damage Storm Gust hit: renewal 3000 × 1164/2640 =
1,322; pre-renewal at MDEF 56: 1,320; at the stock 25: 2,250.

**Surprise:** for many old MVPs renewal kept the *number* and so changed the
effect: Baphomet 45/45, Thanatos 35/35, Lord of Death 73/73, Bloody Knight
50/50 (pre-re/re). Renewal MDEF 45 is a 27.9 % cut; pre-renewal MDEF 45 is
45 %. So copying the renewal MDEF of an *old* monster over-protects it in
pre-renewal, and the table above applies to the shared monsters too.

**Porting.** Convert with the table; fold MRes in as for Res in §1. Never let
hard MDEF reach 100 unless magic immunity is the point.

---

## 4. Soft MDEF (INT, and VIT/2 in pre-renewal)

| | monster soft MDEF | source |
|---|---|---|
| pre-renewal | `mdef2 = INT + VIT/2` (players use the same) | status.cpp:2716-2719 |
| renewal | `mdef2 = (INT + Level) / 4` | status.cpp:2658-2664 |
| renewal player | `INT + Level/4 + (DEX + VIT)/5` | status.cpp:2662 |

Subtracted flat from every spell hit after the % cut (battle.cpp:6106, 6115).

| monster | pre-renewal | renewal |
|---|---|---|
| Lv 150, INT 80, VIT 60 | 110 | 57 |
| Lv 150, INT 131, VIT 123 (renewal MVP medians) | 192 | 70 |
| Lv 98, INT 225, VIT 200 (Beelzebub, pre-re) | 325 | — |

**Porting.** This is where conversions break. Pre-renewal soft MDEF is about
four times renewal's for the same INT, and against pre-renewal spell hits
(a few hundred to two thousand) it is a large share: the converter's own note
records a level-10 Jupitel Thunder doing 12 damage per hit. For the same job,
`INT_pre + VIT_pre/2 ≈ (INT_re + Lv_re)/4 × (typical pre-renewal spell hit /
typical renewal spell hit)` *(inferred)*. But in pre-renewal INT is also the
monster's whole magic attack (§8) and its Sleep resistance (§5). The three
cannot be set independently; §14 says what to give up.

---

## 5. Status resistance

`status_get_sc_def` (status.cpp:9620). Monster values are capped at
`mob_max_status_def` = 100 % (battle.cpp:8618; status.cpp:9886-9891), so a
resistance of 10000 is full immunity.

**Mechanics.**

- pre-renewal: `rate −= rate × sc_def / 10000`, then `rate −= sc_def2`
  (status.cpp:9930-9931). `sc_def2` is usually
  `LUK×10 + Lv_target×10 − Lv_source×10`, a flat cut of 0.1 % per LUK and per
  level of advantage; it may go negative and then *raises* the rate (pre-renewal
  caps it only from above, status.cpp:9887-9888).
- renewal: `sc_def = stat × 100 − levelAdv`, with
  `levelAdv = ⌊max(0, Lv_source − Lv_target)² / 5⌋ × 100` (status.cpp:9658),
  clamped to 0..10000 (status.cpp:9890-9891). No flat part; a source that is
  not higher than the target does not weaken resistance at all.
- Both: monsters with `MD_STATUSIMMUNE` (every `Class: Boss`, and Guardians,
  mob.cpp:5585-5595) cannot get any status whose status.yml entry has
  `BossResist` (status.cpp:10193-10194). Stone, Freeze, Stun, Sleep, Poison,
  Curse, Silence, Confusion, Blind, Bleeding and Decrease AGI have it in **both**
  db/pre-re/status.yml and db/re/status.yml; Quagmire and Hallucination do not.
- Both: Freeze and Stone fail on Undead-element monsters (status.cpp:10238-10248,
  with `undead_detect_type: 0`, conf/battle/battle.conf:72).
- Both: Curse fails on a target with LUK 0 (status.cpp:9743-9744).

### The table

| status | pre-renewal: resisted by | full immunity at | renewal: resisted by | full immunity at | source |
|---|---|---|---|---|---|
| Poison | VIT | VIT 100 | VIT | VIT 100 + levelAdv | status.cpp:9662-9679 |
| Stun | VIT | VIT 100 | VIT | VIT 100 + levelAdv | :9681-9689 |
| **Silence** | **VIT** | VIT 100 | **INT** | INT 100 + levelAdv | :9691-9699 |
| Bleeding | VIT | VIT 100 | AGI | AGI 100 + levelAdv | :9701-9709 |
| **Sleep** | **INT** | INT 100 | AGI | AGI 100 + levelAdv | :9711-9719 |
| Stone (StoneWait) | hard MDEF | MDEF 100 | hard MDEF | MDEF 100 + levelAdv | :9721-9729 |
| Freeze | hard MDEF | MDEF 100 | hard MDEF | MDEF 100 + levelAdv | :9731-9739 |
| Curse | LUK (flat part: LUK×10 − Lv_source×10, no target level) | LUK 100 | LUK | LUK 100 + levelAdv | :9741-9753 |
| Blind | (VIT + INT)/2 | VIT + INT = 200 | INT | INT 100 + levelAdv | :9755-9763 |
| Confusion | (STR + INT)/2; flat part reversed (LUK and level *help* the source) | STR + INT = 200 | LUK | LUK 100 + levelAdv | :9765-9773 |
| Decrease AGI | flat part = hard MDEF × 100 (so MDEF 100 = immune) | MDEF 100 | same | MDEF 100 | :9775-9779 |

`levelAdv`, in stat points: 0 when the source is not above the target; 5 at
+5 levels, 20 at +10, 45 at +15, 80 at +20.

**The belief "INT gives silence immunity" is right for renewal and wrong for
pre-renewal.** In pre-renewal Silence is resisted by **VIT** (status.cpp:9692-9695);
INT resists Sleep and half of Blind and Confusion.

### Worked example

A player of level 99 lands a 50 % Stun (rate 5000) on a monster with VIT 60,
LUK 30.

- pre-renewal, monster level 90: `5000 − 5000×6000/10000 = 2000`; flat part
  `300 + 900 − 990 = 210`; final **17.9 %**.
- renewal, monster level 150, player 175: levelAdv = ⌊25²/5⌋×100 = 12500, so
  sc_def = 6000 − 12500 → 0; final **50 %**. The same VIT protects nothing
  against a stronger caster.

### Porting

Map each resistance the renewal monster has onto the stat that holds it in
pre-renewal:

| renewal stat | resists in renewal | to keep it in pre-renewal, set |
|---|---|---|
| VIT | Stun, Poison | VIT (also resists Silence and Bleeding there) |
| INT | Silence, Blind | VIT for Silence; VIT + INT for Blind |
| AGI | Sleep, Bleeding | INT for Sleep; VIT for Bleeding |
| LUK | Curse, Confusion | LUK for Curse; STR + INT for Confusion |
| MDEF | Freeze, Stone | MDEF (and §3 limits it to < 100 unless magic immunity is wanted) |

Bosses need none of this: `Class: Boss` gives the same blanket immunity in both
eras.

---

## 6. HIT, FLEE and perfect dodge

| | pre-renewal | renewal | source |
|---|---|---|---|
| monster HIT | Lv + DEX | Lv + DEX **+ 150** | status.cpp:2704-2707; 2639-2643 |
| monster FLEE | Lv + AGI | Lv + AGI **+ 100** | status.cpp:2708-2711; 2644-2648 |
| player HIT | Lv + DEX (+ gear) | Lv + DEX + LUK/3 **+ 175** (+ gear, + Vulture's Eye) | same lines; battle.cpp:3288-3290 |
| player FLEE | Lv + AGI (+ gear) | Lv + AGI + LUK/5 **+ 100** (+ gear) | same lines |
| hit chance | **80** + HIT − FLEE | **0** + HIT − FLEE | battle.cpp:3259-3263, 3279 |
| clamp | 5..100 % | 5..100 % | battle.cpp:3313; conf/battle/battle.conf:78-79 |
| perfect dodge | players only: (LUK + 10)/10 %, normal attacks only | same | status.cpp:2735-2740; battle.cpp:5425; battle.conf:17 |
| mobbing penalty on player FLEE | −10 % per attacker beyond 2 | same | battle.cpp:3264-3276; battle.conf:85-95 |

So, in plain stats:

| direction | pre-renewal hit % | renewal hit % |
|---|---|---|
| player hits monster | 80 + (Lv_p + DEX_p) − (Lv_m + AGI_m) | **75** + (Lv_p + DEX_p + LUK_p/3) − (Lv_m + AGI_m) |
| monster hits player | 80 + (Lv_m + DEX_m) − (Lv_p + AGI_p) | **50** + (Lv_m + DEX_m) − (Lv_p + AGI_p + LUK_p/5) |

Monsters have no perfect dodge in either era (`enable_perfect_flee: 1` = players).

**Worked example.** Renewal monster Lv 150, AGI 140, DEX 200. A renewal Lv 175
player with DEX 120, LUK 60, AGI 100 (gear ignored): player hits 75 + 315 − 290
= 100 %; monster hits 50 + 350 − 287 = 100 %. Ported as pre-renewal FLEE 290 /
HIT 350 against a Lv 99 player (DEX 120, AGI 100): player hits 80 + 219 − 290 =
9 %; monster hits 100 %. The numbers survive the port; the players do not.

**Porting.** Hit/flee are a contest against the player population of the era,
so carry over the *chance*, not the number:

- `FLEE_pre = 80 + HIT_ref − p`, where HIT_ref is the HIT of a reference
  pre-renewal attacker (e.g. a Lv 99 Sniper or Lord Knight) and p the hit
  chance the renewal monster gave its era's equivalent;
- `HIT_pre = FLEE_ref − 80 + q` for the monster's own accuracy q against a
  reference pre-renewal tank or evader.

Then AGI = FLEE − Lv and DEX = HIT − Lv (the converter's approach, BALANCING.md
§1). Note the asymmetric constants: for the same stats, renewal is 30 points
*worse* for the monster's own hit and about 5 points worse for the player's.

---

## 7. Crit and crit resistance

| | pre-renewal | renewal | source |
|---|---|---|---|
| who can crit | players and mercenaries (`enable_critical: 17`) | same | conf/battle/battle.conf:21; status.cpp:2722-2733 |
| monster crit | none, except always-crit skills (NPC_CRITICALSLASH) | same | battle.cpp:3023-3024 |
| player crit (0.1 %) | 10 + LUK×10/3 | 10 + LUK×3 + Lv/10 | status.cpp:2725-2730 |
| target's LUK cuts crit by | LUK × 2 (×3 when a monster attacks a player) | same | battle.cpp:3060-3062 |
| a crit… | always hits, **ignores DEF and soft DEF**, max damage | always hits, ×1.4 damage (+ CRATE), **DEF applies** | battle.cpp:3241, 3336-3340, 5646-5658 |

**Worked example.** A pre-renewal Assassin Cross with 60 % crit vs a monster with
LUK 85: 600 − 170 = 430 → 43 % of hits crit and pass every point of DEF.

**Porting.** Crit resistance per LUK is the same in both eras, so LUK can be
copied for that job. But copying it is less protection than it looks: the same
crit that renewal multiplied by 1.4 *after* DEF goes straight through DEF in
pre-renewal. To keep a high-DEF boss from melting to crit builds, raise LUK
(each 5 LUK = −1 % crit). LUK also resists Curse and, in pre-renewal, takes
0.1 % per point off every status rate (§5). LUK 0 means Curse immunity.

---

## 8. Monster ATK and MATK

### Physical

| | damage before skill ratio and DEF | source |
|---|---|---|
| pre-renewal | `rnd(Attack, Attack2 − 1)`; if Attack > Attack2, always Attack2; **no STR, no level** (`enable_baseatk: 0x9` = player + homunculus) | battle.cpp:2527-2540, 2568-2572, 2623-2625; battle.conf:13 |
| renewal | `rnd(0.8·Attack, 1.2·Attack − 1) + STR + Level` (`enable_baseatk_renewal: 0x29F` includes monsters) | status.cpp:2483-2487, 2522-2549, 2692-2695, 2742; battle.cpp:2623-2625; battle.conf:14 |
| renewal crit | × 1.4 in base damage, then × 1.4 again in the final step for a non-player *(unverified: looks like 1.96 for NPC_CRITICALSLASH)* | battle.cpp:2631-2632, 5652-5653 |
| size penalty | none for monsters in either era (size_fix is applied to players only) | battle.cpp:2580-2583 |

### Magic

| | MATK range | source |
|---|---|---|
| pre-renewal | `INT + (INT/7)²` .. `INT + (INT/5)²` — **INT only**; Attack2 plays no part | status.cpp:2510-2516, 2701-2703 |
| renewal | `INT + Lv + 0.7·Attack2` .. `INT + Lv + 1.3·Attack2` | status.cpp:2557-2592 |

Pre-renewal MATK by INT: 50 → 99–150; 80 → 201–336; 100 → 296–500;
120 → 409–696; 150 → 591–1050; 200 → 984–1800; 250 → 1475–2750.

**Worked example.** Renewal monster Lv 150, ATK 2000, STR 100, INT 80, Attack2
1500. Physical: 1600..2399 + 250 = 1850..2649 (avg 2250). Magic: 1280..2180
(avg 1730). Pre-renewal, same raw output: `Attack 1850, Attack2 2650` for the
blows, and **INT ≈ 225** for the spells (225 → 1249..2250). That INT gives
soft MDEF 225 + VIT/2 (§4) and Sleep immunity (§5).

### Porting

- Physical: `Attack_pre ≈ 0.8·ATK + STR + Lv`, `Attack2_pre ≈ 1.2·ATK + STR + Lv`
  (then scale for the era's player toughness).
- Renewal's Attack2 is MATK. The converter treats it so and drops it, setting
  Attack2 = Attack × the anchors' spread (BALANCING.md). That is right for the
  physical range, **but it leaves the monster's spells with whatever INT the
  ranking gave**. In pre-renewal, spell power comes from INT alone, so a
  renewal caster with high Attack2 and modest INT loses most of its magic.
  A caster ported this way hits with spells far softer than its design; a
  boss ported with high INT gets strong spells *and* near-immunity to magic.
- Ways to decouple, none in place: give the monster's spells higher levels in
  mob_skill_db; use NPC skills whose damage comes from ATK (NPC_EARTHQUAKE,
  NPC_*BREATH and the NPC element attacks are weapon-based, §10); or a Lua
  `skill(..., { ratio = ... })` hook that checks `c.caster.mob_id`
  (skill_lua.cpp:275 exposes it) *(possible route, untested)*.

---

## 9. Attack speed, cast time

| | pre-renewal | renewal | source |
|---|---|---|---|
| `AttackDelay` | time between attacks, clamped 100..8000 ms | same | mob.cpp:5417-5424; status.hpp:43-56 |
| `AttackMotion` | animation, clamped 1..8000 | same | mob.cpp:5426-5434 |
| missing fields | AttackDelay 100, AttackMotion 100 (`MAX_ASPD_NOPC`) | same | mob.cpp:5005-5007; status.hpp:47-56 |
| after load | AttackDelay = max(AttackDelay, AttackMotion) | same | mob.cpp:5609 |
| buffs/debuffs | amotion × aspd_rate; adelay never raised by it, floored at amotion | same (the `RENEWAL_ASPD` branches are for players and homunculi only) | status.cpp:6418-6431 |
| **skill cast time** | the mob_skill_db CastTime, only status effects change it | CastTime split 80/20 into variable/fixed, and the variable part **shrinks with the monster's DEX and INT**: × (1 − √((2·DEX + INT)/530)) | unit.cpp:2467-2472; skill.cpp:10270-10395; conf/battle/skill.conf:54, 376 |

So a missing AttackDelay gives a monster 10 attacks a second. Always carry it.

**Surprise:** a renewal monster with DEX 200 and INT 130 casts with only
`1 − √(530/530) = 0` of its variable cast, i.e. its fixed 20 % alone. The same
mob_skill_db row in pre-renewal casts at full length, 5 × longer. Renewal casters
are effectively much faster than their CastTime column says *(unverified in game)*.
Where a monster's threat is how fast it casts, shorten its CastTime when porting.

---

## 10. Skill damage formulas monsters use

Most NPC skills have one ratio for both eras; the era difference is the base
they multiply (§8) and the defence that follows (§1, §3).

| skill | type | ratio (both eras unless stated) | base | source |
|---|---|---|---|---|
| NPC_HELLJUDGEMENT | weapon, splash | 100 % × level | physical (§8) | skills/npc/hellsjudgement.cpp:15-16 |
| NPC_PULSESTRIKE | weapon, splash | 100 % × level | physical | skills/npc/pulsestrike.cpp:9-10 |
| NPC_*ATTACK (element), NPC_*BREATH, NPC_RANDOMATTACK, NPC_BLOODDRAIN | weapon | 100 % × level | physical | e.g. skills/npc/fireattributeattack.cpp:10, firebreath.cpp:13 |
| NPC_PIERCINGATT | weapon, ignores DEF | 75 % | physical | skills/npc/piercingattack.cpp:10 |
| NPC_CRITICALSLASH | weapon, always crit, ignores DEF | 100 % | physical | battle.cpp:3023 |
| NPC_EARTHQUAKE | magic, ignores MDEF, split | (200 + 100·lv + 100·⌊lv/2⌋ + (lv > 4 ? 100 : 0)) % | **physical ATK**; pre-renewal also ATK% buffs | battle.cpp:5937-5964 |
| NPC_DARKBREATH | magic | target's HP × (lv ≤ 5 ? 1/(2·(6−lv)) : ½) | none | battle.cpp:5928-5930 |
| NPC_GRANDDARKNESS | magic | +40 %/lv; pre-re (ATK after DEF + MATK) × ratio; renewal ((ATK + MATK)/2) × ratio − (DEF + soft DEF + MDEF + soft MDEF) | both | battle.cpp:6172-6206 |
| NPC_ICEMINE, NPC_FLAMECROSS | magic | Attack × 20 × level | Attack | battle.cpp:5965-5967 |
| MG_FIREBALL | magic | pre-re **70 + 10·lv %**; renewal **140 + 20·lv %** | MATK | skills/mage/fireball.cpp:12-16 |
| WZ_JUPITEL | magic | 100 % per hit, 3..12 hits by level in both DBs | MATK | db/*/skill_db.yml |
| MG_FIREBOLT / COLDBOLT / LIGHTNINGBOLT | magic | 100 % per hit, hits = level | MATK | skills/mage/firebolt.cpp |
| WZ_STORMGUST | magic | pre-re 100 + 40·lv %; renewal 70 + 50·lv % | MATK | skills/mage/stormgust.cpp:20-26 |
| WZ_FROSTNOVA | magic | pre-re (100 + 10·lv)·⅔ %; renewal 100 + 10·lv % | MATK | skills/mage/frostnova.cpp:23-29 |
| NPC_JACKFROST | magic | renewal × Lv/100 or /150 above level 99 (`RE_LVL_DMOD`); no-op in pre-re | MATK | skills/npc/jackfrost2.cpp:19-27; src/config/const.hpp:94-108 |

**Worked example: Hell's Judgement lv 5** from the §8 monster. Renewal:
2250 × 5 = 11,250 before DEF; against a renewal tank with DEF 300, × 0.614 =
6,910 − soft DEF. Pre-renewal with Attack 1850–2650: 11,250 again before DEF;
against a pre-renewal tank with DEF 50, 5,625 − VIT DEF. That is more than a
pre-renewal party member's HP (BALANCING.md records 2,971 a hit killing a level-48
party); this is why the mid band scales skill levels.

**Skills missing in pre-renewal.** db/pre-re/skill_db.yml has no or an empty
entry (no `Type`) for several renewal monster skills: NPC_HELLJUDGEMENT2,
NPC_CANE_OF_EVIL_EYE, NPC_PULSESTRIKE2, NPC_DRAGONBREATH, NPC_PSYCHIC_WAVE,
NPC_RAYOFGENESIS. The converter drops skills pre-renewal lacks; a boss built
around them needs a replacement.

---

## 11. Level-difference effects

| effect | pre-renewal | renewal | source |
|---|---|---|---|
| EXP by (monster Lv − player Lv) | none | 40 % at ≥ +16, 140 % at +10, … 10 % at ≤ −31 | db/re/level_penalty.yml; mob.cpp:3212-3219; pc.cpp:13374-13404 |
| Drops by level difference | none | 50 % at ≥ +16 … | db/re/level_penalty.yml; mob.cpp:3260-3262 |
| MVP EXP / MVP drops | none | penalty tables | mob.cpp:3470-3475, 3500-3505 |
| Status resistance | flat 0.1 %/level of difference (§5) | `levelAdv` only when the source is higher (§5) | status.cpp:9658 |
| Skill damage by caster level | none | `RE_LVL_DMOD`: × Lv/100 (or /150…) for casters above 99, in ~300 mostly 3rd-job skills; NPC: Jack Frost | src/config/const.hpp:94-108 |
| Monster level in its own stats | HIT, FLEE, Heal | HIT, FLEE, base ATK, MATK, soft DEF, soft MDEF, Heal, cast time (none) | §2, §4, §6, §8 |
| Damage penalty by level difference | none | none (no such code in battle.cpp) | — |

**Porting.** Renewal's level feeds almost every derived stat; pre-renewal's
feeds only HIT and FLEE. A renewal level 150 is worth +75 soft DEF, +37 soft
MDEF, +150 ATK and +150 MATK; none of it exists in pre-renewal, so it must come
back through Attack, VIT and INT.

---

## 12. HP regeneration and healing

| | pre-renewal | renewal | source |
|---|---|---|---|
| natural regen | none: `BL_REGEN` is player, homunculus, mercenary and elemental | same | status.hpp:3354; status.cpp:5270-5271 |
| AL_HEAL level ≥ `max_heal_lv` (11) | **9999** flat | **9999** flat | skill.cpp:581-582; conf/battle/skill.conf:248-249 |
| AL_HEAL below that | `⌊(Lv + INT)/8⌋ × (4 + 8·skill_lv)` | `⌊(Lv + INT)/5⌋ × 30 × skill_lv/10` **+ MATK** (§8), + Attack2 again as "weapon MATK" *(the second Attack2 is read from the code, unverified in game)* | skill.cpp:580-592, 695-732 |
| Sanctuary / NPC_EVILLAND | 100/lv up to 777 / 666 | same | skill.cpp:542-547 |

Example: AL_HEAL lv 10 by a monster Lv 150, INT 80, Attack2 1500. Pre-renewal:
⌊230/8⌋ × 84 = 2,352. Renewal: 46 × 30 = 1,380 + MATK 1,280..2,180 + 1,500
≈ 4,200–5,000. Renewal's monster MVPs mostly cast AL_HEAL at level 11
(db/re/mob_skill_db.txt, e.g. Baphomet), which is 9999 in both eras.

A dynamic-mobs map removes its monsters when no player is on it, damaged or not
(`mob_remove_damaged: yes`, conf/battle/monster.conf:257); they come back at
full HP. Same in both eras.

**Porting.** Heal at level 11 needs nothing. Below 11 a renewal heal is roughly
twice a pre-renewal one; raise the skill level or accept the difference.

---

## 13. Elements and sizes

### size_fix

The base table (db/size_fix.yml) is shared; the era files override two rows:

| weapon | pre-renewal | renewal |
|---|---|---|
| Knuckle | S 100 / M 75 / L 50 | S 100 / M 100 / L 75 |
| Whip | S 75 / M 100 / L 50 | S 75 / M 100 / L 75 |

Only players' weapons are size-fixed (battle.cpp:2580-2583). A monster's size
matters to players' weapons alone, and almost identically in both eras.

### attr_fix

Rows are the attacking element, columns the defending element (db/pre-re/attr_fix.yml:24-27).
They differ widely. The pattern, `pre-renewal → renewal`:

| case | lv 1 | lv 2 | lv 3 | lv 4 |
|---|---|---|---|---|
| Neutral vs Ghost | 25 → 90 | **0 → 70** | **0 → 50** | 0 |
| Ghost vs Neutral | 25 → 90 | 0 → 70 | 0 → 50 | 0 |
| element vs itself (Water/Earth/Fire/Wind) | 25 (Earth 100 → 25) | 0 (Earth 50 → 0) | **−25 → 0** (Earth 0) | **−50 → 0** (Earth −25 → 0) |
| weak counter (Water vs Wind, Fire vs Water, …) | 50 → 90 | 25 → 80 | 0 → 70 | 0 → 60 |
| strong counter (Water vs Fire, …) | 150 | 175 | 200 | 200 (unchanged) |
| Water/Earth/Fire/Wind vs Poison | 100 → 150 | 100 → 150 | 100 → 125 | 75 → 125 |
| Water/Earth/Fire/Wind vs Holy | 75 → 100 | 50 → 100 | 25 → 100 | 0 → 100 |
| Water/Earth/Fire/Wind vs Dark | 100 | 75 → 100 | 50 → 100 | 25 → 100 |
| Holy vs Undead | 150 → 125 | 175 → 150 | 200 → 175 | 200 |
| Holy vs Holy / Dark vs Dark | 0 | −25 → 0 | −50 → 0 | −100 → 0 |
| Poison/Dark vs Undead | −25 → 75 / −25 → 0 | −50 → 50 / −50 → 0 | … | −100 → 0 |
| Undead vs Holy | 100 → 125 | 125 → 150 | 150 → 175 | 175 → 200 |
| Ghost vs Water/Earth/Fire/Wind | 100 | 75 → 100 | 50 → 100 | 25 → 100 |

(Full grid: `diff db/pre-re/attr_fix.yml db/re/attr_fix.yml`.)

**Porting.** Keep the element and its level, but check what they do:

- A renewal **Ghost 2–3** monster that players hit for 70 %/50 % with neutral
  weapons is **immune to neutral damage in pre-renewal**. Either lower it to
  Ghost 1 or accept that it needs elemental weapons.
- Pre-renewal punishes the wrong element much harder (same element at level 3–4
  *heals*; weak counters drop to 0). Element choice matters more for the
  players fighting a ported monster, and its own elemental attacks against
  a player's armour element are also harsher.
- Holy armour 2–4 takes 50/25/0 % from the four elements in pre-renewal, Dark
  armour 2–4 75/50/25 %; in renewal both take 100 %.

---

## 14. Porting checklist for a renewal boss

For a renewal monster with level L, DEF D, MDEF M, Res R, MRes MR and stats
STR/AGI/VIT/INT/DEX/LUK:

| target | compute | keeps | can't keep |
|---|---|---|---|
| **DEF** | `100 × (1 − (1 − R/(R+400)×0.8) × (4000+D)/(4000+10D))`, round | physical % cut, Res folded in | crits ignore it (§1); Ice Pick feeds on it |
| **MDEF** | same with MR and `(1000+M)/(1000+10M)` | magic % cut; Freeze/Stone resistance ≈ MDEF | MDEF ≥ 100 would be total immunity, so the formula's ≤ 89 is the ceiling |
| **VIT** | max of: Stun/Poison need (renewal VIT); Silence need (renewal INT); Bleeding need (renewal AGI) | the four VIT statuses | soft DEF and VIT/2 soft MDEF come with it; for a `Class: Boss` this row is moot |
| **INT** | from the spell power wanted: the INT whose §8 range averages the renewal MATK, **or** from Sleep need (renewal AGI), whichever matters | spell damage, Sleep | soft MDEF = INT + VIT/2, often far above renewal's (INT+L)/4 — magic users then barely scratch it |
| **AGI** | `FLEE_target − L_pre`, with FLEE_target from the hit chance a reference pre-renewal attacker should have (§6) | being hit | — |
| **DEX** | `HIT_target − L_pre`, from the hit chance against a reference pre-renewal defender | hitting | cast time no longer shrinks with DEX: shorten CastTime instead (§9) |
| **LUK** | copy, then raise it if the boss must not melt to crits | crit resistance (same formula) | LUK also cuts every status 0.1 %/pt in pre-renewal; LUK 0 = Curse-immune |
| **STR** | irrelevant in pre-renewal; fold STR + L into Attack/Attack2 | — | — |
| **Attack / Attack2** | `0.8·ATK + STR + L` / `1.2·ATK + STR + L`, then the band's scale | physical range | — |
| **AttackDelay/Motion** | copy; never leave empty (default 100 ms) | speed | — |
| **Element** | copy, then check Ghost ≥ 2 and same-element levels (§13) | — | Ghost 2+ becomes neutral-immune |

Where it cannot match:

1. **DEF/MDEF ≥ 100 is immunity** (to non-crit physical / to all magic, and to
   Freeze/Stone). Renewal never reaches it; don't create it by accident.
2. **INT is three things at once** in pre-renewal (spell power, soft MDEF,
   Sleep). A strong renewal caster cannot keep its spell power without becoming
   near magic-immune. Decide which matters and use skill levels or a Lua ratio
   hook for the rest.
3. **Crits ignore DEF** in pre-renewal: a renewal "armoured" boss has no
   physical wall against crit builds. LUK is the only lever.
4. **VIT carries Silence and Bleeding** in pre-renewal; INT and AGI
   resistances must be moved to VIT and INT.
5. **Level-derived bonuses vanish** (§11): put them back through Attack, VIT,
   INT, or they are simply lost.
6. **Cast speed** in renewal depends on DEX/INT; in pre-renewal only on the
   CastTime column.
7. **Res / MRes** have no pre-renewal equivalent except folding into DEF/MDEF.

### What the converter does today

`build_monsters.py` ranks DEF, MDEF, STR, VIT, INT and LUK among the renewal
peers and reads the value at that rank off the fair pre-renewal tier; AGI and
DEX go through HIT and FLEE sums the same way, and Attack2 becomes Attack × the
anchors' spread. For bosses it only *warns* when the ranking flips which of
physical and magic damage the boss resists more (build_monsters.py:586-598).

Consequences:

- **The reductions are pre-renewal's typical ones, not the monster's own.** A
  renewal boss built to resist magic far more than physical keeps that order only
  if its rank does; the warning catches flips, not size. The %-cut can drift
  far from the renewal design in either direction.
- **Resistances follow the wrong stats.** A rank-based INT says nothing about
  Silence (VIT in pre-renewal), and AGI's ranks feed FLEE, not Sleep/Bleeding.
  For ordinary monsters this only shifts how often crowd control lands; bosses
  are immune anyway.
- **Spell power is whatever the INT rank gives**, since Attack2 is no longer
  MATK. Casters may come out weaker than their renewal design, and high-INT
  ones near magic-immune through soft MDEF.
- **Res/MRes and level-derived soft defences are dropped silently.** Renewal
  monsters with Res (110 of them) lose that layer.
- **The upside:** rank-mapping keeps every value inside the range real
  pre-renewal monsters use, so nothing lands on an immunity threshold, and the
  fight tests in BALANCING.md and BOSSES.md already correct the outcome.

Matching reductions (§1, §3) instead of ranks would make the conversion
explain itself; the price is that the derived soft stats (§2, §4) and the INT
coupling (§8) then need a choice per monster.
