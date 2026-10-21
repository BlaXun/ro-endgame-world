# Porting a renewal monster to pre-renewal

A checklist, in order, for bringing a renewal-only monster or boss into
renewal-world. The reasons behind each step are in [BALANCING.md](BALANCING.md)
(ordinary monsters) and [BOSSES.md](BOSSES.md) (minibosses and MVPs); the fight
tests in [`../companion-strategies/FIGHT_TESTS.md`](../tools/companion-strategies/FIGHT_TESTS.md);
the tactics in [`../companion-strategies/TACTICS.md`](../tools/companion-strategies/TACTICS.md).

## 1. Choose

- [ ] The map is in `maps.csv` and open (something leads in), its monsters in
      `monster_maps.csv`. Renewal's spawn lines decide which monsters come.
- [ ] Bosses only on maps whose row says `bosses: yes`, and only once their own
      tests are done (step 6).
- [ ] The monster's band (`bands.csv`, by its renewal level or the map's): the
      anchors and the fair tier it is converted against.

## 2. Convert

`build_monsters.py --write --rathena <rathena>` (with `--check` first). It:

- scales HP, attack and experience by the band's anchors, then the band's and the
  map's scale-down factors, and caps HP and attack at 1.5 times the fair tier's
  strongest;
- ranks DEF, MDEF and the stats among renewal peers and reads them off the fair
  tier (FLEE and HIT as sums with the level, FLEE capped);
- ranks the level among the anchors; a boss gets the era's boss correction on
  top (MVP +19 levels over its map, HP ×0.59 …) and **keeps that level**, even
  when its fights are meant for a stronger party (the user, 2026-10-10);
- scales skill levels and caps skill rates by band; a boss's self-heals only when
  idle;
- converts a boss's summoned slaves pre-renewal lacks;
- leaves out equipment and card drops, copies etc and usable loot.

`monsters.csv` overrides any of it per monster, with a note saying why.

## 3. Check the data, before any fight

The formulas behind these checks, era against era, are in
[STATS_ERAS.md](STATS_ERAS.md).

The converter copies renewal's entries; renewal's data has holes, and a hole
decides a fight before any number does. Read the converted entry and its skill
rows for:

- [ ] **Attack speed.** `AttackDelay`, `AttackMotion`, `DamageMotion` present. A
      monster without `AttackDelay` attacks at rAthena's fastest, a hit every
      0.1 s. Renewal leaves it off `G_BANASPATY` (Leak's summoned Banaspaty) and
      the three Lichterns; the converter gives a summoned copy (`G_X`) its
      original's and reports the rest. It was found only after Leak's tests: its
      Banaspaty did 70-80 % of what a level-95 party took, and three plan
      versions were spent on them as a "swarm".
- [ ] **Summoned copies match their original** (`G_X` against `X`): same
      speed, element, race, size; only experience and drops differ.
- [ ] **Its defences do the same job** (STATS_ERAS.md): compare damage
      reductions, not numbers (pre-renewal DEF that matches renewal's:
      900·D/(4000+10·D); MDEF: 900·M/(1000+10·M)); crits ignore DEF in
      pre-renewal; Res/MRes are ignored there; status resistance follows other
      stats (Silence: VIT in pre-renewal, INT in renewal).
- [ ] **Skills pre-renewal has** (`skill_db.yml`, pre-re). A skill pre-renewal
      lacks does nothing or fails; the build stops on usable items that cast one.
- [ ] **Summons and calls name monsters that exist** in the mod or pre-renewal.
- [ ] **A boss's skill conditions**: does it change tactics at HP thresholds
      (`myhpltmaxrate`), or use everything from full HP? Pre-renewal MVPs
      escalate (Power Up, Agi Up, heals below 30 %); a boss that does not gives a
      party nothing to learn (Leak used every skill "always").
- [ ] **Its slaves' threshold** (`slavele`): how many fall before a new pack, and
      how fast. Killing slaves that respawn every 10 s feeds the boss.

A quick test that catches what the table hides: one monster against one
character (`rwtest.txt` `spawn#id`), and a look at `whohurts.py` — how often it
hits, and how hard, against what its stats say.

## 4. Test an ordinary monster

`FIGHT_TESTS.md` §5: a party of the band's level, without plans and with them,
packs of one and three, against fair pre-renewal references of the same level.
Fairness bars: no wipe, no fight over before a healer can act. Then the
experience from time and risk (`harness/calibrate.py`).

## 5. Test a boss: tactics first

1. **Read the boss** (`DAMAGE_MECHANICS.md` "how to read a boss"): element,
   race, size; what blocks its skills (Safety Wall within 3 cells, Pneuma beyond);
   what its slaves are and whether they are bosses (statuses work on them if
   not).
   **Ask what its kit says about the designers' intent** (`../companion-strategies/READING_BOSSES.md`). A boss's skills are
   chosen together: Leak casts Land Protector, which erases Pneuma and Safety
   Wall, beside Hell Judgement and Pulse Strike, which those two are the classic
   answer to. The designers meant its strikes to be stood through (HP, heals,
   damage reduction, a tank, moving it off its ground), not walled off. Plan for
   that fight first; a trick that undoes the design (laying our own Land
   Protector on its) may stay as a reward but must not be needed, and the
   balance is judged without it.
2. **Write its plan** before judging it (`mvp-<name>.party.yml`): the tactics in
   `TACTICS.md`, the cards from `harness/bosscards.py`, the right party
   (`CLASSES.md`; a transcendent party for endgame bosses).
3. **Fight it with fixed gear and stocked bags** (`GEAR=mid`, Companion
   inventory on, `rwparty.py` KITS) against reference bosses of its target tier,
   fought the same way. 15-minute attrition fights; `START_HP` starts a later
   phase on its own.
4. **Judge the trend**: its HP lost a minute and the party's falls a minute,
   phase by phase, against the references'. A kill inside the test is not the
   measure.
5. **Improve the tactics** while they can be improved: what does the damage
   (`whohurts.py`), what the plan does about it (trace with `TRACE=`), what the
   party lacks. A gap in the plan system goes to `NEEDS.md` and the
   strategy-needs session.
6. **Only then adjust the boss**: phases first (skill conditions), then its and
   its slaves' damage and HP (`calibrate_boss.py`: attack while falls are far
   above the references', then HP from the wear), experience from the
   references' pay. Write down which tactics were tried.

**Not too easy.** The aim is a boss that is killable, not an easy one:

- **Clearly harder than the easy reference of its tier.** For an endgame MVP
  and a level-95 party that is Turtle General (killed in 5-10 minutes, 3-4 falls
  a minute): the boss should take noticeably longer, about 15-25 minutes, and
  make the party fall more, above all in its later phases.
- **Every phase asks for its tactic.** An early phase may be calm; the later
  ones should be survivable only with the right tactic (Pneuma and Safety Wall,
  clearing its Land Protector, cures, Assumptio). Check it: the same fight
  without that tactic should go clearly worse.
- **Cut as little as needed.** HP comes down only until the trend points into
  that range, not to the easy reference's time. A phase that turns out too easy
  is made harder where it is (its skills, its slaves), not by leaving the early
  phases as they are and cutting HP everywhere.
- **The test party is average, not the best.** Level 95 rather than 99, +7
  weapons with two ordinary cards, casters without damage gear, and the time a
  companion loses walking and choosing. A well-equipped party of players kills
  faster. The references were fought by the same party, so the comparison holds;
  but aim the test party's kill time at the **upper end** of the range (about 25
  minutes for an endgame MVP), so that a well-geared party lands in its middle.
- **A fixed bug is not a difficulty.** A fix (Leak's slaves attacking every 0.1 s)
  makes the boss easier for the right reason; measure again before cutting.

## 6. Ship

- [ ] `monster_maps.csv`: `bosses: yes` for the map, when its bosses passed.
- [ ] `build_monsters.py --write`, `--check` up to date.
- [ ] The plan in `companion-strategies/`, its results in BOSSES.md.
- [ ] Test changes undone: anything changed only for a test (a phase, a halved
      attack, a fixed slave) is either in the converter, a `monsters.csv` row with
      a note, or gone.
