# Balancing renewal monsters for pre-renewal

How renewal-world brings a region's monsters into pre-renewal, and the rules
that came out of doing it for the Bifrost fields (2026-10-09). The steps are
in order; each one caught something the one before could not.

The aims:

- **Party content, never unfair.** A region beyond the old world is meant for
  a party with a healer and crowd control. A single character may struggle;
  no fight may end before a healer could react.
- **Never boring either.** A pack a party clears without a plan is too easy:
  the fights should reward tactics. Not every party has to beat every
  monster; one common party with a sensible plan is enough.
- **Worth the time.** Experience follows what a fight costs: time and risk.
- **A step above.** A new region is a little harder than ordinary pre-renewal
  monsters of its level, and pays a quarter more per minute: it is what
  players travel for.
- **Only ordinary monsters for now.** Bosses (minibosses and MVPs, stock or
  renewal-only) are left out of the spawns: they need a test of their own
  (see the end).
- **Loot:** etc and usable items. Equipment and cards are left out until new
  gear is balanced as a task of its own (since done: they ship in the mods
  renewal-world-gear and renewal-world-cards, DROPS.md). Etc and usable loot pre-renewal lacks
  is copied from renewal's item tables (Eclage: 9 items); a usable that casts a
  skill pre-renewal lacks stops the build.

## 0. Above 99: levels from renewal, strength from a ladder of fights

Sections 1 to 4 were written while the cap was 99 and every region had to fit under it.
With transcendent-third-classes the cap is 175, and the conversion of ordinary monsters
changed (2026-10-12). What still holds from below: the aims, the fair tier and how DEF,
MDEF and the stats are ranked into it, the party test and its order when a pack is lost,
the plans, and how experience is calibrated. What replaced the bands for ordinary monsters:

- **Level:** renewal's own, raised to 70 where it is lower (Malangdo's culvert) and held
  at 175. Objects (plants, crystals, a few HP) keep the old conversion; so do bosses,
  until their own phase.
- **Level steps:** 70, 80, 90 and 100, 110, ... 170. A monster belongs to the step nearest
  its level and is fought by a party of that step's level, whatever its region.
- **HP and attack** are the step's reference (`steps.csv`) times how the monster stands
  among renewal's open-world monsters of its level (its HP over their median, within
  0.5-2.0; its attack within 0.6-1.6). A monster keeps being the tough one or the weak
  one of its level, as its designers made it; how strong the level is as a whole is one
  pair of numbers per step. The quest areas' monsters are left out of the median: they
  have many times the HP of anything at their level, and land at the top of the bounds.
- **Below 100** the reference is not tuned by hand: 1.25 times the median HP, and the
  median attack, of the fair pre-renewal monsters within eight levels.
- **From 100** the references are set by fights, climbing: the anchor first (a 99/70
  party against Abysmal Knight, Acidus and Bloody Knight), then step 100 a little harder
  than the anchor for a level-100 party, and each step about 5 % harder for its own
  party than the one below was for its party, in time per kill and in pressure (the
  damage the party takes a second as a share of the tank's HP). At most three rounds a
  step. `steps.csv` has each step's numbers and how they were reached.
- **AGI and DEX** are ranked as plain stats now: the party is of the monster's level, so
  the level cancels in HIT and FLEE. AGI still stops at the fair tier's 75th percentile.
- **A monster off its step's line** gets `HpScale` or `AttackScale` in `monsters.csv`,
  with a note, after BALANCING's order (plans and parties first).
- **Experience** is the step's rate times the measured time per kill times the risk
  factor, as in section 4. The table for 99 to 175 asks for the same experience an hour
  at every level, so the rate is the anchor's.

`monsters-cap99.csv` keeps the calibration of the level-99 version for the record.

## 1. Convert

`build_monsters.py` does this; its docstring has the detail.

**Two reference groups, not one.** The monsters closest to a new one in
pre-renewal can themselves be unfair: Splendide's and Manuk's kill a geared
level-99 Lord Knight in under two seconds. Copying them faithfully copied
that. So:

- **the anchors**, monsters both eras share near the new one's level, say
  how renewal's numbers translate into pre-renewal's formulas;
- **the fair tier**, ordinary pre-renewal monsters of level 70-99 less those
  in `prere_unfair.csv`, says what the numbers may be.

**Each kind of stat its own way.**

| Stat | How | Why |
|---|---|---|
| HP, ATK, Base/Job EXP | renewal value × the anchors' median ratio, then the scale-down factors | amounts scale |
| ATK2 | ATK × the anchors' spread | renewal's ATK2 is magic attack |
| DEF, MDEF, STR, VIT, INT, LUK | rank among renewal peers (±10 levels), value at that rank in the fair tier | pre-renewal defence is a percentage (100 is immune); ratios gave MDEF 230 |
| AGI, DEX | FLEE (level + AGI) and HIT (level + DEX) ranked as sums, then minus the level | the level counts in both; ranked as plain stats, FLEE came out 253 |
| FLEE | capped at the fair tier's 75th percentile | at its very top (192) three Angra Mantises outlasted a party with Quagmire and Ankle Snare |
| Level | rank among the anchors | the anchors' pre-renewal levels bunch whatever their renewal level |

**INT is soft MDEF too.** INT + VIT/2 comes off every spell after MDEF. A
monster with a high rank in both was immune to magic in practice (a level-10
Jupitel Thunder did 12). Always test a caster.

**The scale-down factors** (`OFFENCE`, `TOUGHNESS`) take the result from the
anchors' level of danger to the fair tier's. Bifrost needed attack ×0.2 and HP
×0.5 because its anchors were Splendide's. They belong to the anchors, not to
the game: a band with fair anchors needs less.

**Check the region's stock monsters.** A renewal spawn list can include
pre-renewal monsters that are on the unfair list (Bifrost: Luciola Vespa ×56,
Cornus ×33; El Dicastes: Centipede ×98, Tatacho ×52). They keep their stock
stats. Decide per region; for Bifrost they stay for now.

**Level bands** (`bands.csv`). Renewal raised many old monsters' levels, so a
renewal level does not say where a monster sits in pre-renewal. Each band
names its anchors, its fair tier, its scale-down factors and what happens to
the monsters' skills:

- *high* (renewal 140-155, Bifrost, Eclage, Rockridge's mine): the anchors are
  the shared monsters at pre-renewal 101 and up (Splendide's, unfair), the fair
  tier pre-renewal 70-99, attack ×0.2 and HP ×0.5, renewal's skills as they
  are.
- *top* (renewal 156+, Verus and beyond): the same anchors, further from them.
  With the high band's factors, Verus's robots (renewal 155-171) wiped a
  level-99 party in packs of three; attack ×0.08 and HP ×0.25.
- *mid* (renewal 60-139; Dewata, Malangdo, Malaya, El Dicastes): the anchors
  are the shared monsters within six renewal levels (ordinary, fair ones), the
  fair tier the monsters within eight levels of where the new one lands. Renewal
  80-88 lands at pre-renewal 43-53, 100 at 56, 125 at 76. Skill levels scale
  with the level (pre-renewal / renewal): at renewal's, two Cendrawasihs killed a
  level-48 party in 20 s with Hell Judgement and Pulse Strike (up to 2,971 a
  hit, more than a Wizard's HP). Rates stop at 50 %: at 20 % the casters
  (Banaspaty) lost their bite. HP ×1.25 makes the band a step above its
  references (×1.0 left Dewata too easy; ×1.5 tipped its skill-heavy monsters
  over); Cendrawasih and Comodo keep ×1.0, their kits being their step above.

**A cap.** Renewal's quest areas give their monsters many times the HP of
anything at their level (a Bios Island Plasma came out at 1.15 million). In
every band, HP and attack stop at 1.5 times the strongest
monster of the fair tier, and experience shrinks with HP. Among the tested
regions it trimmed only a few: Ruin Grace Believer (Verus), Faithful Manager,
the third Elite Buffalo Bandit and the gold Scaraba eggs, by 3-18 %.

**A map can scale further** (`offence` and `toughness` in monster_maps.csv).
The quest areas, renewal's episode 17 built for characters far past 99, are at
×0.5 both on top of their band and the cap: with the cap alone a level-99
party lost nearly every pack there; halved, most areas pass, and the maps whose
monsters still beat every party (Wolfchev's laboratory, Bios Island's library
and research rooms, the nightmare clock tower and Glast Heim castle) have none
yet.

The edge between the bands sits at renewal 140, where Bifrost and Eclage
begin; OPEN_QUESTIONS.md 4 has the other layouts.

**Renewal's attack speeds come along**, and ranking them into the fair tier
moved them too little (Dolomedes 0.36 s to 0.50 s) while making others faster
(Manananggal 0.28 s to 0.17 s), so they stay renewal's; a monster whose speed
alone beats every party gets its own AttackDelay in monsters.csv (Dolomedes:
0.864 s, Pom Spider's). Comodo attacks every 0.5 s, Wraith of
the same level every 1.8 s: three of them hit a tank far harder than their
ATK says. It stays (a Crusader tank answers it), but it is the first thing to
check when a low-level monster with modest ATK wipes a party.

## 2. Solo test

A Lord Knight, base 99 / job 70, the same stats in three gear tiers (shop gear;
+5-7 with common cards; +7-10 with good cards), fights each new monster and
fair references from the same band (Bloody Knight, Abysmal Knight, Hell
Apocalypse, Acidus) without a healer. A High Wizard casts at a monster that
cannot fight back.

**The bar:** the tier-2 Lord Knight survives at least about 7 seconds against
one monster, as he does against the references. Magic does damage comparable
to what it does to the references, element aside.

**Measure a monster's damage with a character that cannot die** (`bighp`: ten
times the HP): the biggest single hit and the damage a second, skills
included. A character that starts at 1 HP after a death looks like a one-shot.

## 3. Party test

Four companions at the level the band is for (99 in the high band: Lord
Knight tank, High Priest, High Wizard, Sniper; 48 for Dewata: Knight, Priest,
Wizard, Hunter), packs of one and three, three runs per pack, one party per
server. A party far above the monsters' level proves nothing: at 55, three
level-43 Alnoldis fell in 7 seconds. A region whose monsters span a wide range is tested in
tiers, each at its own level: Malaya's first field at 65, its second (level
76 monsters) at 72; at 65 the second field's Engkanto wiped the party, at 72
it was a step above Skeleton Generals and Rybios.

**Monsters that teleport out of a pack** (Wakwak, Manananggal) are judged and
calibrated alone: a party that cannot finish a pack because two of it left is
not losing.
`tools/companion-strategies/README.md` has the party, the plans and
the harness.

1. **The everyday plans** (`everyday-party.yml`): the fairness test. An
   ordinary competent party.
2. **A small plan per monster**: who first, and the one counter that works
   (interrupt it, Quagmire it, stand still against it). Without it a party
   loses fights it should win, and the monster looks too hard when the plan
   is.

**The bars:**

- *Fair:* every pack is cleared without the party wiping, in about one to two
  times what three Abysmal Knights take, by **at least one common party with a
  plan**. Not every party: the standard one may lose to a monster another
  party is built for.
- *Not boring:* the same pack, met by a party with no plan of its own
  (companion-roles alone), should struggle or lose.
- *Pack size follows the spawn.* A monster with only a handful on its map is
  met alone: judge it at ×1. Faithful Manager (three on its floor) is a ×1
  monster; Antique Book (fifteen) a ×3 one.

**The order, when a pack is lost:**

1. a first run with no plan of its own: losing is expected;
2. a plan for the classes in it, then a plan for the monster, each refined a
   few times from traces;
3. other common parties, each with its plan: a Lord Knight, a High Priest and
   a High Wizard, with a Sniper, an Assassin Cross (Meteor Assault stuns a
   pack), a Clown (Bragi: faster casting for the healer and the caster), a
   Champion; or a Paladin tank (Devotion on the healer). Two healers is not a
   common party;
4. only when no party with a plan clears it, the monster's numbers change,
   in `monsters.csv` with a note.

Antique Book is the example: three of them hit a tank for about 5,000 a
second, more than a Priest heals. The standard party lost however its plan
was refined; with an Assassin Cross it cleared three runs of three, with a
Clown two. So its numbers stayed.

**Pneuma under whoever is shot from range.** Three ranged Elite Buffalo Bandits
out of the tank's reach wiped the party every time; with the Priest's Pneuma
under their target, never.

**Stand out of reach of what hits everyone around it.** Cendrawasih's Hell
Judgement and Pulse Strike are centred on itself, Comodo's Bowling Bash on the
tank: everyone but the tank keeps four to nine cells off, and the healer heals
from there.

**Casters cast first and move later.** A rule that keeps a caster at range
outranking its casts makes it walk off every cast against monsters that keep
moving: four of twenty Frost Divers went off against three Antique Books. Step
away only from a monster hitting the caster in melee.

**When a fight runs long, trace it before blaming the monster.** Every slow
pack in the Bifrost run was a plan doing the wrong thing: a Wizard that kept
stepping off Quagmire broke every Fire Bolt (its SP never fell), a Priest who
buffed the hidden owner 239 times, a regroup rule meant for bosses. Run each
pack three times: one run in Bifrost took 167 s where the other two took 30.

## 4. Experience

Converted experience follows HP, and in Bifrost it was already within a
quarter of the calibrated value: good enough for a first version. Then:

- **time a kill:** median seconds per kill of the ×1 runs and of the ×3 runs,
  averaged, for the party that clears it (the standard one where it can; for
  Antique Book, the one with an Assassin Cross);
- **rate:** the party's base experience per second at references of the
  band (high: Abysmal Knight and Acidus; mid: ordinary monsters of the same
  level, for Dewata Argiope, Wraith, Orc Archer, High Orc) × 1.25: a step
  above;
- **risk:** × (1 + 0.25 × (1 − the median lowest HP in the ×3 runs)).

Base EXP = rate × time a kill × risk. Job EXP keeps the conversion's ratio.

A monster that never fights back (El Dicastes' Scaraba eggs) pays half the
reference rate, not 1.25 times it: no risk and nothing to answer, so less a
minute than a real fight, or it becomes the best farm in the region. Its time is
its HP at the party's measured damage, since companions leave a monster that
does not attack them alone.
The values go into `monsters.csv` with a note of how they were reached.

## Not covered yet

- **Bosses.** Left out of the spawns until they pass their own test:
  [BOSSES.md](BOSSES.md) (converted through their region's band and an era
  correction, judged in attrition fights against pre-renewal bosses).
