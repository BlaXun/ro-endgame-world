# Balancing renewal bosses for pre-renewal

Bosses (minibosses, `Class: Boss`, and MVPs, `MvpExp`) are left out of
renewal-world's spawns until they are balanced: a map gets its bosses only when
its `monster_maps.csv` row says `bosses: yes`, and none does yet. This is the
method as it stands (2026-10-10), what the tests showed, and what is left.
BALANCING.md covers ordinary monsters; [`../companion-strategies/FIGHT_TESTS.md`](../companion-strategies/FIGHT_TESTS.md)
how the fights are run.

Since 2026-10-18 the bosses are written to two mods of their own, with their spawn lines:
`renewal-world-minibosses` (King Dramoh, Wild Rider, the gold Scarabas and the eggs they hatch
from) and `renewal-world-mvps` (the MVPs, Spider Chariot with them, and the monsters only they
summon; it requires the minibosses mod, as the Gold Queen Scaraba summons the gold Scarabas).
`renewal-world-monsters` keeps the ordinary ones.

Spider Chariot (2026-10-18) is converted as an MVP: it carries renewal's Mvp mode, but renewal's
table leaves its MVP experience out, and the conversion used to take a boss without one for a
miniboss. Now it gets the MVP correction, MVP peers and MVP experience (half its base experience),
and was fought again with eight at 158: HP x4.0, attack x0.84 against its MVP conversion, wear
about 14 %/min and 9.7 falls a minute (monsters.csv has the rounds).

## 1. Conversion: the region's band, then the era's boss correction

A boss is converted as an ordinary monster of its region (the band its map or its
renewal level gives, with that band's anchors, scale-down and fair tier), then
corrected for how differently the two eras weigh a boss against its map
(`boss_correction` in `build_monsters.py`). For every boss on a map with two or
more ordinary monsters, in each era, its HP, attack and experience over the
median of theirs, and its level less theirs; the correction is pre-renewal's
median over renewal's:

| | HP | Attack | Base EXP | Job EXP | Level |
|---|---|---|---|---|---|
| MVP | x0.59 | x0.96 | x0.18 | x0.16 | +19 |
| miniboss | x2.00 | x1.65 | x2.45 | x2.13 | +3 |

(Renewal's MVPs pay about 300 times their map's monsters, pre-renewal's 54.)
DEF, MDEF and the stats take their rank among pre-renewal's bosses of the same
kind around the level it lands at; HP, attack and experience stop at 1.5 times
the strongest of those; level stops at 99; MVP experience is half the base, as
for every pre-renewal MVP. A boss's self-heals are kept to when it is idle, as
pre-renewal's are. Summoned slaves pre-renewal lacks are converted with it.

**Tactics first** (the user, 2026-10-11): a boss that is too hard is met with
tactics, counters and preventions first (a plan, elements, cards and armour, party
composition, cures); its damage and HP (and its slaves') come down only where no tactic
helps, and the tactics tried are written down with the cut.

**Level stays the band's** (the user, 2026-10-10): a boss keeps the level its band
and the correction give, though its fights may be meant for a stronger party (Leak:
level 75, renewal 94, beatable by a level-95+ party). Fights adjust its HP and
damage only.

**Why this way.** Converting each stat from bosses both eras share is as
accurate on those bosses (leave-one-out, median error about x1.6 on HP for
either method), but the shared bosses above renewal 120 are ones renewal
reworked: by them Mechaspider came out at 1.04M HP and 31.9M base experience,
and the instance Scarabas at 435-576k HP, and Bestia and Pitaya had too few to
convert at all. Through its region a boss also takes the scale-down that region
was tested with. Either way the error is about x1.5-2, so **the conversion is
only a starting point; the fights decide** (section 3).

## 2. Test: attrition fights

A party rarely kills a pre-renewal MVP inside a test, so "did it clear" says
nothing (the first pilot: Amon Ra lost 2 % of its HP in ten minutes). Bosses are
fought in attrition: a member who falls is up again, full, 5 s later; a boss
that teleports away is set back beside the party after 10 s out of sight; five
minutes a fight, four or more fights. Two numbers come out: **wear**, its HP the
party takes off a minute, and **falls**, how often a member goes down a minute.
A converted boss is compared with pre-renewal bosses of its kind and level,
fought by the same party the same way.

### Pre-renewal MVPs, no boss plans (8 companions at 99)

Lord Knight and Paladin tanks, two High Priests, High Wizard, Sniper, Assassin
Cross, Professor; companion-roles and the region plans, nothing for a
particular boss:

| MVP | Level | Wear %/min | Falls/min | Killed in |
|---|---|---|---|---|
| Eddga | 65 | 310 | 1.4 | 18-21 s |
| Phreeoni | 69 | 101 | 0 | 52-69 s |
| Mistress | 74 | 87 | 0 | 59-82 s |
| Orc Hero | 77 | 45 | 0.4 | 117-153 s |
| Osiris | 78 | 93 | 1.8 | 62-67 s |
| Dark Lord | 80 | 9 | 18 | - |
| Baphomet | 81 | 10 | 20 | - |
| Amon Ra | 88 | 6 | 17 | - |
| Pharaoh | 93 | 8 | 0 | - |
| Lord of Death | 94 | 9 | 18 | - |
| Turtle General | 97 | 66 | 0.3 | 82-102 s |
| Leak (converted) | 75 | 0.8 | 13 | - |

Eight at 99 beat the easy and middling MVPs with no plan, so those need a smaller
or lower party to say anything. Dark Lord, Baphomet, Amon Ra and Lord of Death
knock the party down 17-20 times a minute; Pharaoh downs nobody but barely wears
(DEF 67, MDEF 70). Leak, as converted, is harder than any of them.

### Wild Rider (miniboss), a level-56 Knight, Priest, Wizard and Hunter

Wild Rider (converted, L56) 11 % a minute and 14 falls, against Executioner 91 %
and 0, Mutant Dragon 66 % and 15, Galion 181 % and 1.3. Its falls are far above
the references', so its attack comes first: halved for the next test (the rule
in `calibrate_boss.py`: attack while falls exceed 1.5 x the references' median +
0.5, then HP from wear).

## 3. Boss plans

Players beat these bosses with tactics, not rare cards
([`../companion-strategies/MVP_TACTICS.md`](../companion-strategies/MVP_TACTICS.md)).
Each plan is a file of its own, kept to ship in a boss-plans mod:

- [`mvp-amon-ra.party.yml`](../companion-strategies/mvp-amon-ra.party.yml):
  Land Protector under it (Meteor Storm and Fire Pillar), everyone in its
  middle, the summons first, nothing cast at it. 5.9 % / 16.5 falls -> 11.9 % /
  7.1.
- [`mvp-hell-judgement.party.yml`](../companion-strategies/mvp-hell-judgement.party.yml),
  Dark Lord, Baphomet, Lord of Death: Hell Judgement is Neutral physical damage,
  so Safety Wall stops it within 3 cells and Pneuma beyond; one Pneuma spot for
  the back line, Assumptio (Kyrie banned: they end each other), Aspersio on the
  melee, Dispel on Power Up, Magnus on the slaves, Ankle Snare to pin the boss.
  Lord of Death 9 % / 17.5 -> 10.5 % / 9.6; Baphomet 10.4 % / 20 -> 10.9 % /
  15.7; Dark Lord unchanged.

- [`mvp-mistress.party.yml`](../companion-strategies/mvp-mistress.party.yml),
  a level-80 party of five against Mistress, 15-minute fights, Companion
  inventory on: Quagmire on her (her flee; it is the Wizard's, the Sage has none),
  Lex Divina and Green Potions against her silence, Dispel on her Agi Up (`SC_AGIUP`,
  not Increase AGI's status), Seismic Weapon on the tank, a Fire Wall between a
  caster and a hornet, no Water or Wind skill on her or her slaves. Wind armour
  (a Dustiness card) cuts her Jupitel Thunder to a quarter. 3.3 % / 6.9 falls ->
  falls 1.7 to 2.7, every run at 30-35 % after 15 minutes.

The 30 % wall: below 30 % she heals herself for 9 999 (the `max_heal` cap) about
once a minute, and a level-80 party of five deals 9-14k a minute there, the same
as she heals. Swapping the free slots (Knight, Hunter, Assassin, Gunslinger) moves
the falls, not the wall; without the Wizard it is worse. Before that, the
party's SP was the limit: Magnificat at the bottom of the Priest's list went up
twice a fight (now: whenever it is down and nothing is on the Priest), and
Safety Wall every 2 s and Frost Diver on a Wind boss spent the rest.

Past the wall: the Knight keeps its SP (no Bowling Bash) until she is below 32 %,
then bursts on the Priest's Lex Aeterna, and a sixth member, a Gunslinger casting
Desperado into her and her hornets (a plan rule: the engine has no Gunslinger
rotation, NEEDS 17). Six at level 80 killed her in 422 s (7 falls) and 849 s (52
falls); five with the same plan stayed at 32 % and 51 %. Five with a Gunslinger in
place of the Knight or the Hunter: Hunter and Gunslinger killed her once in two
(483 s, 31 falls; the other ended at 32 %), Knight and Gunslinger not (27 %, 30
%). So six is the reference party for her: the sixth member counts, not only
Desperado.

**References, fixed gear** (`GEAR=mid` in `rwparty.py`: a +7 two-slot weapon with the
boss's race and element cards from `bosscards.py` for the physical damage dealers, a +4
Arc Wand for casters, a +4 Raydric Muffler for everyone; Companion inventory on and
stocked bags), a level-80 Priest, Wizard, Sage, Hunter and Gunslinger, 15-minute fights:

| MVP | Level | Killed | Times | Falls/min |
|---|---|---|---|---|
| Mistress (Wind armour) | 74 | 4 of 4 | 207, 410, 428, 521 s | 1.7 |
| Orc Hero | 77 | 2 of 2 | 434, 674 s | 3.8 |
| Osiris | 78 | 2 of 2 | 529, 753 s | 15.5 |

Osiris dies, but the party falls far too often (his Ancient Mummies 44 % of the damage,
Meteor Assault 26 %): his plan needs work before it is a reference.

Every plan improves the falls; none makes a hard MVP beatable yet. What stops
them is the plan system: companions cannot be held in the middle of a field
(NEEDS.md 11), a plan cannot name its boss apart from miniboss slaves (12), and
a rule that holds casters at bosses that would not teleport for it (6).

### Leak, where it stands (2026-10-11, paused)

Fought by a level-95 transcendent party (Paladin, High Priest, High Wizard,
Professor, Sniper; fixed gear, stocked bags, Fire armour) with `mvp-leak.party.yml`.
Found and fixed on the way: its summoned Banaspaty had no attack speed (a hit
every 0.1 s, 70-80 % of the damage; the converter now gives a `G_` copy its
original's); the Sniper was overweight from the engine's ammunition (the harness
trims bags); the counter Land Protector (NEEDS 18) needed to outrank
companion-roles' `leave_hostile_ground`.

Tried **only in the test copy**, not in the conversion:

- **Phases**: Hell Judgement, Wide Curse/Silence and Land Protector below 60 %;
  Wide Stun/Sleep/Bleeding and Dragon Fear below 30 %. They escalate as meant
  (phase 1 calm, 2 and 3 hard); without Pneuma and Safety Wall the party falls
  a little more but holds: its strikes fit the intended stand-through fight.
- **HP and attack**: at 1.01M HP no trend to a kill; at 200k a kill in about 32
  minutes, 6.8 falls a minute; at 450k with attack x0.6 or x0.75 (equal) about
  1.6 % a minute and a phase 1 that is calm and long. Chosen direction (the user):
  HP near pre-renewal's MVPs (400-450k) and less pressure, not 140k.
- **Phase 1 content**: Butoijo (`G_BUTOIJO`, built from the converted Butoijo)
  below 80 %, and a rare Land Protector in phase 1. rAthena gives all rows of one
  skill the first row's delay (`mob.cpp`), so a summon is throttled by its rate:
  at 100 % Leak called 2 Butoijo every 11 s (8-20 falls a minute); 15 % was
  under test (400k HP, attack x0.75) when the work paused.

Next: finish that round, then write the chosen phases, HP, attack, slaves and
experience into the conversion (`monsters.csv`, the skill rows) with notes; reset
the test copy (`bosswt`, backups `mob_db.before_phase1.yml`,
`mob_skill_db.before_phase1.txt`, `mob_skill_db.before_phases.txt`); then the
level-95 references and Wild Rider.

## 4. What the tests taught

- Read the mechanic in rAthena before planning on it: Hell Judgement has no
  element (Neutral, so Evil Druid armour did nothing); a monster's skill is
  melee within 3 cells and ranged beyond; Kyrie and Assumptio end each other;
  official Land Protector does not shield its own edge.
- Count the damage by source before changing anything (`harness/whohurts.py`);
  ground spells come from their unit, not the monster.
- The harness itself misled twice: summons outlived their boss into the next
  fight, and Land Protector outlived a fight. Both fixed (`FIGHT_TESTS.md` §8).
- Raw results: [`../companion-strategies/harness/boss-attrition.jsonl`](../companion-strategies/harness/boss-attrition.jsonl)
  (`clean_restore: false` rounds ran before the summons fix).

## 5. To do, in order

0. Mistress: done (six at level 80). Repeat the kill for a median.
1. Plans for the easy and middling MVPs (Eddga, Phreeoni, Mistress, Orc Hero,
   Osiris) with smaller, lower parties, so the plan matters: references with
   plans.
2. Leak and Wild Rider against those, plan against plan; `calibrate_boss.py`
   for their attack, HP and experience.
3. The hard MVPs again once NEEDS.md 11 and 12 exist.
4. Drops (no gear or cards, as for monsters), then `bosses: yes` region by
   region.
