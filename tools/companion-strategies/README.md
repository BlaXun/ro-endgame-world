# Companion strategies: tested party plans

Plans for companions (`db/population_strategy.yml`, see
[docs/mods/companion-strategies](https://github.com/Flux159/ragnarokoffline.app/blob/main/docs/mods/companion-strategies/README.md)),
kept here until a mod ships them. Each one has been played by a party of
companions on a test server, and the results are below. None of them is shipped,
and nothing here is read by the app.

To ship one, copy its entries into a mod's `db/population_strategy.yml`. They
load in this order, each adding to the one before:

| File | What it is | Needs |
|---|---|---|
| `examples/mods/companion-roles` | the roles at bosses; survival, resurrection and peel in every fight | |
| [`everyday-party.yml`](everyday-party.yml) | the roles in **every** fight: heal whoever is hit, Kyrie (on herself too), walls, cures and buffs; bolts by element, freezing what is on the healer, area spells on packs, casting before moving; traps and Double Strafe from range; a Knight or Paladin tank provoking what is on the healer, Bowling Bash, Auto Guard, Devotion, Grand Cross; a Bard's Bragi; a Champion's combo and Asura | companion-roles |
| [`bifrost-fields.party.yml`](bifrost-fields.party.yml) | the renewal-world Bifrost monsters: who first, interrupting casts, Quagmire and Ankle Snare on Angra Mantis, standing still against Pom Spider | everyday-party |
| [`eclage.party.yml`](eclage.party.yml) | the renewal-world Eclage monsters: Antique Book frozen and snared, healed early, no Lex Aeterna | everyday-party |
| [`rockridge.party.yml`](rockridge.party.yml) | the Rockridge mine: the shooting Elite Buffalo Bandit first, Pneuma under whoever it targets | everyday-party |
| [`dewata.party.yml`](dewata.party.yml) | the renewal-world Dewata monsters (a level-48 party): Cendrawasih first and stood off, casts interrupted, freezing, off Comodo's Bowling Bash | everyday-party |

[NEEDS.md](NEEDS.md) lists what the plans could not say, each with a test case.
[BUILDS.md](BUILDS.md) lists the pre-renewal builds of each class, what each is
good and bad against, and common party setups: the reference for which parties
and builds to try against a monster. There is rarely one answer to a monster;
try more than one build and party.

## The party

Four companions at base 99 / job 70, drafted with `@companion draft` and
raised with `#blvl` / `#joblvl`, wearing what the engine gives their job:

| Name | Job | Role (party chat) |
|---|---|---|
| Tank | Lord Knight | tank |
| Hela | High Priest | support |
| Wiz | High Wizard | attacker |
| Snip | Sniper | attacker |

The owner hides (`@hide`) and stands still, so every action is a plan's or the
engine's. Combat mode Attack. Each pack spawns 6-9 cells east of the owner, on a
field with no spawns of its own; before each pack the party is raised and healed.

## Results

renewal-world 0.2.0 monsters, 2026-10-09: companion-roles + everyday-party +
bifrost-fields, three runs per pack, each run on its own server. A wipe is the
whole party down; "lowest" is the lowest HP any member reached.

| Pack | Run 1 | Run 2 | Run 3 | Lowest HP |
|---|---|---|---|---|
| Miming ×1 | 14 s | 12 s | 12 s | 97 % |
| Miming ×3 | 28 s | 27 s | 34 s | 86-95 % |
| Little Fatum ×1 | 8 s | 7 s | 8 s | 82-91 % |
| Little Fatum ×3 | 22 s | 24 s | 19 s | 25-50 % |
| Angra Mantis ×1 | 12 s | 9 s | 9 s | 89-90 % |
| Angra Mantis ×3 | 25 s | 29 s | 19 s | 20-76 % |
| Pom Spider ×1 | 13 s | 13 s | 13 s | 89-100 % |
| Pom Spider ×3 | 32 s | 167 s | 27 s | 48-69 % |
| Abysmal Knight ×3 | 17 s | 17 s | 17 s | 60-76 % |
| Acidus ×3 | 57 s | 27 s | 44 s | a death in two runs |

The raw results are [`harness/bifrost-calibration.jsonl`](harness/bifrost-calibration.jsonl).

For comparison, with companion-roles alone (no everyday-party), the same party
lost every pack of three of these monsters and of Bloody Knight, Abysmal Knight,
Hell Apocalypse and Naga: its High Priest's SP never fell below 90 %, because
companion-roles keeps her combat healing for bosses. With everyday-party but no
plan of their own, three Bloody Knights, three Hell Apocalypses and three Nagas
still wiped it.

### Experience from these fights

renewal-world's `monsters.csv` sets the four monsters' Base and Job EXP from the
table above:

- **time a kill**: the median seconds per kill of the ×1 runs and of the ×3
  runs, averaged (fields give both singles and pulls);
- **the rate**: the party's base experience per second against Abysmal Knight
  ×3 and Acidus ×3 (1,703), times 1.25 for the tier above;
- **risk**: plus up to a quarter, by the median lowest HP in the ×3 runs
  (1 + 0.25 × (1 − lowest HP)).

Base EXP = rate × time a kill × risk; Job EXP keeps the conversion's ratio to it.
Re-run the fights after a change to the monsters or the plans, and the numbers
with them.

### Eclage, and other parties

The same party, the plans as they stand (with the caster and healer fixes found
in Eclage), three runs each: every Eclage pack of one and of three is cleared,
mostly in one to three times what three Abysmal Knights take, except three
Antique Books. Those hit a tank for about 5,000 a second; after three rounds of
refining the plans the standard party still lost them. Other parties against
three Antique Books, each with its role plan:

| Party (Lord Knight, High Priest, High Wizard and...) | Antique Book ×3 |
|---|---|
| Assassin Cross (Meteor Assault) | cleared 4 of 6 runs |
| Sniper (standard) | lost |
| Paladin tank instead of the Lord Knight, with a Sniper | lost |
| Professor (Spider Web) instead of the High Wizard, with a Sniper | cleared 2 of 3 |
| Asura Champion (STR/INT/DEX) | cleared 1 of 3 |
| Combo Champion | lost (single target, no control) |
| Clown (Bragi) | cleared 2 of 3 |
| a second High Priest instead of a damage dealer | 0 of 3 cleared, survived 2 |

Several answers work, each stopping the books from hitting in its own way
(holding them, stunning them, casting faster); single-target damage does not.
The raw results are [`harness/eclage-calibration.jsonl`](harness/eclage-calibration.jsonl).

### Dewata

A level-48 party: Knight (tank), Priest, Wizard, Hunter, each set to 48 with
`LEVEL=48`; six runs per pack (low levels swing more). With the plans every
single monster is cleared, three Alnoldis, Banaspatys or Butoijos in 7-22 s
(three Argiopes, Wraiths, Orc Archers or High Orcs take 4-42 s), three Comodos
with a Crusader tank in 9-42 s (with a Knight half the runs wipe: they attack
every half second), Cendrawasih alone every time once the others stand off its
Hell Judgement (two at once wipe half the time; sixteen are on its field).
Without plans nearly every pack of three is lost. The raw results are
[`harness/dewata-calibration.jsonl`](harness/dewata-calibration.jsonl).

### Malangdo and Malaya

Same party, at the regions' levels, six runs per pack. Malangdo at 54: three
Siorava or Red Eruma always cleared, Red Eruma in two to three times the time
of Zombie Prisoners or Penomenas. Malaya at 65 (the first field and the
hospital): every single monster and three Jejelings, Tiyanaks or Tikbalangs
cleared; Manananggal and Wakwak teleport out of a pack, so they count alone.
Malaya's second field at 72: three Engkantos, Bungisngis or Mangkukulams
cleared in 9-62 s without a wipe, where three Loli Ruris or Agavs wipe the same
party. At 65 Engkanto wiped it: the second field is for higher levels. Raw
results: [`harness/malaya-malangdo-calibration.jsonl`](harness/malaya-malangdo-calibration.jsonl).

### Izlude dungeon 5, El Dicastes, Rockridge, Verus

Izlude 5 at 65: every pack cleared, in about the time of Alarms and Permeters.
El Dicastes at 78: the Scarabas in packs of three slowly (25-80 s), about as
the party fares against Imps and Acidus there; three Dolomedes wiped every
party tried (Knight, Crusader, Assassin, Sage) until it swung at Pom Spider's
speed, then cleared every run. Rockridge's fields at 63: every pack cleared
about as fast as Alarms. Its mine at 99: every pack but the shooting Elite
Bandit's, which needs Pneuma and its HP halved and still beats the party once
in three. Verus at 99, in the top band: every robot pack cleared in a minute or
so without a wipe. Raw results: [`harness/open-regions-calibration.jsonl`](harness/open-regions-calibration.jsonl).

### Without plans

Not boring, too: the same level-65 party with companion-roles alone (no
everyday-party, no monster plans) lost five of six packs of three of Izlude 5's
and Malaya's monsters (four wipes), and cleared three Alarms, Clocks and
Permeters, slowly. The new monsters want a plan where ordinary ones do not.

## Boss plans

`mvp-*.party.yml` are plans for particular pre-renewal MVPs, each a file of its
own to ship in a boss-plans mod: Mistress (beaten: a level-80 party of five with
fixed gear kills her 4 times in 4, 207-521 s), Eddga, Orc Hero, Osiris, Amon Ra,
and the Hell Judgement bosses (Dark Lord, Baphomet, Lord of Death). Their
headers give what kills, what the plan does, and what it measured;
[`MVP_TACTICS.md`](MVP_TACTICS.md) what players do, with sources;
[`DAMAGE_MECHANICS.md`](DAMAGE_MECHANICS.md) and [`CLASSES.md`](CLASSES.md) the
rules they rest on; [`../renewal-world/BOSSES.md`](../renewal-world-monsters/BOSSES.md) the
boss method and results. The hard MVPs are not beatable yet.

## Running the fights

[`FIGHT_TESTS.md`](FIGHT_TESTS.md) is the full guide: the rig, the plans, pack
and boss (attrition) fights, finding out what happened, and the traps.

[`harness/`](harness/) has the two pieces that are ours:

- `rwtest.txt`, an NPC script the server loads: it spawns a pack beside its
  caller (`pack#<mob>#<n>`), reports each named member's HP and SP and the
  monsters left (`status#Tank,Hela,...`), raises and heals the party
  (`restore#...`), and finds an open spot on a map (`gospot#<map>`).
- `rwsuite.py`, which runs one region's packs on several test servers at once
  (each runs the whole list, so three servers give three runs of every pack),
  merges the plans, restarts the servers with them, and prints per pack how many
  runs cleared it, how many wiped, the median time and the lowest HP anyone
  reached.
- `rwparty.py`, which plays the owner through a headless client (`roclient.py`,
  from the class-mod balance rig): it drafts and levels the party, sets roles
  and Attack mode in party chat, hides, then fights each pack until it is dead,
  the party is, or 180 s pass, and prints one JSON line per pack.

```
RUSER=gmtest MAP=alb2trea LIMIT=180 TRACE=Wiz,Hela \
  python3 rwparty.py 4008:Tank:tank:m,4009:Hela:support:f,4010:Wiz:attacker:m,4012:Snip:attacker:m \
  2137:1 2137:3 2136:3
```

The server is the pinned rAthena with `scripts/apply-server-mods.sh` applied,
built pre-renewal, with `population_engine_enable: 1`, renewal-world, the plans
above and `rwtest.txt` loaded. Things that cost time:

- Run one party per server for timings. Four parties on one map server ran
  fights up to four times slower; separate servers (own ports and database)
  did not.
- The owner needs a party before drafting, and `@party` needs Basic Skill
  level 7 (`@allskill`) and fails without a word on a name with `_`.
- `LEVEL=<n>` puts the owner and every companion at that base level (the
  draft alone gives the job profile's range).
- A party member is `job:name:role:sex:STR/AGI/VIT/INT/DEX/LUK`; the last
  field (optional) sets that companion's stats, for testing a particular
  build.
- `TRACE=<names>` prints each companion's rule-by-rule trace: the way to find
  out why a pack takes long (a cast that never finishes shows as SP that never
  falls).
