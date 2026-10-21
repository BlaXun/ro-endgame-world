# Fight tests: new monsters against parties of companions

How a new or converted monster is tested in a real rAthena server: a party of
companions (the population engine's AI players), driven by the strategy plans in
this directory, fights it, and the numbers decide whether its stats, skills and
experience are right. Written for an agent picking this work up. It is how the
renewal-world monsters (`tools/renewal-world-monsters/`) and the boss plans
(`mvp-*.party.yml`) were tested.

Read first: [`../renewal-world/BALANCING.md`](../renewal-world-monsters/BALANCING.md) (the
rules for ordinary monsters), [`../renewal-world/BOSSES.md`](../renewal-world-monsters/BOSSES.md)
(bosses), [`README.md`](README.md) (the plans and their results),
[`NEEDS.md`](NEEDS.md) (what the plan system cannot do yet),
[`MVP_TACTICS.md`](MVP_TACTICS.md) (what players do against pre-renewal MVPs),
and [`docs/mods/companion-strategies/reference.md`](https://github.com/Flux159/ragnarokoffline.app/blob/main/docs/mods/companion-strategies/reference.md)
(the plan table).

## 1. The idea

- **The party is the measuring stick.** A monster is fair when a common party
  at its level, playing a sensible plan, beats it in a reasonable time without
  being wiped; it is engaging when the same party without a plan does worse.
  Not every party has to beat every monster.
- **Compare, don't judge alone.** Every converted monster is fought beside
  stock pre-renewal monsters of the same level and kind (its references), by
  the same party, in the same way. The target is a range set by them, not a
  number of your own.
- **Plans before numbers.** When a party loses, first write or refine its plan
  (two or three tries), then change the monster. A monster that falls to a party
  with no plan at all is too easy.
- **Vary the party.** Use common compositions (a tank, one healer, damage
  dealers; not two healers as a rule) and different builds of a class. There is
  never one solution.

## 2. The rig

The test server is the app's pinned rAthena, pre-renewal, packet version
20221005, with the app's own server additions (the population engine), in
Docker, on its own ports and database, next to anything else running.

1. **The base rig** is the class mods' balance rig, committed on the class-mod
   branches (`mods/rebellion`, `mods/transcendent-third-classes`, ...) under
   `ro-endgame-classes/tools/expanded_class/balance/`. Copy that directory out to a work
   directory (it is not on every branch):
   `git archive mods/rebellion ro-endgame-classes/tools/expanded_class/balance | tar -x -C <dir> --strip-components=4`.
   It has `setup.sh` (clones the pinned rAthena into `./rathena`), `build.sh`
   (builds it in a container), `up.sh` / `down.sh`, `roclient.py` (a headless
   game client that plays a character from the command line, printing JSON),
   and `base/` (configs and test accounts).
2. **Add the population engine:** after `setup.sh`,
   `scripts/apply-server-mods.sh <dir>/rathena`, then `<dir>/build.sh`.
3. **Turn it on** in `base/conf/battle_conf.txt`:
   ```
   population_engine_enable: 1
   population_engine_companion_limit: 8
   population_engine_companion_inventory: 1
   ```
   Without the limit, an owner gets 4 companions ("Your party is at the
   companion limit") and the rest of the draft fails quietly. With Companion
   inventory on, a companion lives on its bag as a player does: potions,
   gemstones, catalysts, arrows and traps run out, and `UseItem` rules have
   something to use. `rwparty.py` tops each bag up to a job's kit before every
   pack (`KITS` in it; `STOCK=0` turns that off). Test with it on: off, the
   engine hands out a free supply that never runs out.
4. **Accounts:** `base/sql/accounts.sql` creates `gmtest` (GM). Make every
   test account a GM (`group_id 99`) so each can drive its own party.
5. **Several servers** for parallel runs: copy the rig and change, in `up.sh`,
   `down.sh`, `tools/run_servers.sh`, `base/conf/*.txt` and `roclient.py`, the
   container names and the four ports (login, char, map, database). One party
   per server: four parties on one map server ran fights up to four times
   slower.
6. **The harness** ([`harness/`](harness/)) goes beside it: `rwparty.py` and
   `rwsuite.py` into the rig directory, and `rwtest.txt` as
   `<rig>/rwtest/npc/rwtest.txt` (it is loaded like a mod).
   They are copies: after changing either in `harness/`, copy it to every rig
   again, or the rigs keep running the old one without a word.

`./up.sh <mod-dir> ...` starts from clean import directories every time, copies
each mod's `db/`, `npc/`, `lua/` and `conf/` in, and starts the servers. For a
fight test, load the monster mod, a directory with the merged plans (below), and
`<rig>/rwtest`. It prints the map server's errors and warnings: read them; a
plan with an unknown key or skill is skipped with a warning, not an error.

## 3. The plans

`rwsuite.py` merges `examples/mods/companion-roles` (every role's behaviour),
then `everyday-party.yml`, the region plans, and every other `*.yml` in this
directory, into one `db/population_strategy.yml`, and loads that. Write a new
plan as a file of its own here (`<region>.party.yml`, `mvp-<boss>.party.yml`),
with a header that says what kills, what the plan does about it, and what it
measured; rule names get a prefix of their own. A plan that works is kept for a
mod later, and so is the record of what did not work.

## 4. A fight

`rwparty.py` logs in as the owner, drafts the party, levels it, sets roles and
Attack mode in party chat, hides (the owner only watches), then for each pack:
moves to an open spot, heals and raises everyone, spawns the monsters 6-9 cells
away, and polls the party's HP and SP every 2 s until the pack is dead, the
party is, or the time is up. One JSON line per pack.

```
cd <rig>
LEVEL=99 LIMIT=180 MAP=alb2trea TRACE=Wiz \
  python3 rwparty.py 4008:Tank:tank:m,4009:Hela:support:f,4010:Wiz:attacker:m,4012:Snip:attacker:m \
  2137:1 2137:3
```

- **Party:** `job_id:Name:role:sex[:STR/AGI/VIT/INT/DEX/LUK]`. Roles are `tank`,
  `support`, `attacker`. Names without `_`. The stats field sets a build.
- **`LEVEL`** sets the owner and every companion to that base level.
- **`SKILLS_OFF=Name:SKILL,...`** unticks skills (a Champion without Chain
  Combo plays the Asura build).
- **`TRACE=Name,...`** prints those companions' rule-by-rule decisions: the way
  to find out why a fight goes wrong.
- **Packs:** `mob_id:count`. Test x1 and x3 of each monster.

`rwsuite.py` runs the same list on several rigs at once and summarises:

```
RIGS=<rig1>,<rig2>,<rig3> SUITE_OUT=<out> python3 harness/rwsuite.py \
  --tag dewata --level 48 --party <party> 2151:1 2151:3 ...
```

Each rig runs the whole list, so three rigs give three runs of every pack. The
summary per pack: how many runs cleared it, how many wiped, the median time and
the lowest HP anyone reached. Use `--mod` to load a different build of the
monster mod, `--no-load` to keep the servers as they are.

## 5. Ordinary monsters: what to measure

For each new monster and its references (stock monsters of its level the party
also fights):

1. **Without plans** (companion-roles only) and **with** the plans. Without
   plans the party should struggle more; if it clears just as easily, the
   monster is too easy.
2. **Fairness bars:** the party clears x1 and x3 without a wipe across the runs,
   nobody is killed in a couple of seconds, and the time per kill is close to
   the references'. A level-99 Lord Knight in plain armour (`RwTest lk#1`) that
   dies in under 3 s marks a monster as unfair; [`../renewal-world/prere_unfair.csv`](../renewal-world-monsters/prere_unfair.csv)
   lists the stock ones.
3. **Experience** from the fights: [`harness/calibrate.py`](harness/calibrate.py)
   (`Base EXP = pay x rate x time x risk`: the references' experience per
   second, the monster's seconds per kill, and 1 + 0.25 x (1 - the lowest HP)
   for risk). [`harness/merge_csv.py`](harness/merge_csv.py) writes the rows into
   `monsters.csv`; the converter reads them.

## 6. Bosses: attrition fights

A party rarely kills a pre-renewal MVP inside a test, so "did it clear" says
nothing. Bosses are fought in **attrition** mode: `rwsuite.py --attrition 5
--rejoin 10 --limit 300`.

- **Attrition:** a member who falls is raised, full, 5 s later, and a wipe does
  not end the fight. Two numbers come out: **wear**, the boss's HP the party
  takes off a minute, and **falls**, how often a member goes down a minute.
- **Rejoin:** a boss that teleports away (most do, when hit by someone they
  cannot reach) is set back beside the party after 10 s out of sight, as players
  hunt it down. Without it a run measures whether the boss got lost.
- **References:** pre-renewal bosses of the same kind (MVP or miniboss) and
  level, fought the same way. [`harness/calibrate_boss.py`](harness/calibrate_boss.py)
  turns the results into the converted boss's attack (first, while its falls are
  well above the references'), then its HP (wear scales with 1/HP) and its
  experience.
- **Boss plans** are learnt on pre-renewal MVPs first (easy, middling, hard),
  then the new bosses are judged against those, plan against plan.

Four or more runs of 5 minutes per boss; single runs swing widely.

## 7. Finding out what happened

- **`TRACE=`**: which rule won each turn. A rule that never appears never
  applied (a condition failed, or a higher rule always won).
- **[`harness/whohurts.py`](harness/whohurts.py)** `<rig>/logs/client-gmtest.jsonl`:
  who did the damage the party took in the last session, by monster and skill.
  Ground spells come from their unit, not the monster, and are listed apart.
- **The client log** (`<rig>/logs/client-<user>.jsonl`): every damage, cast,
  ground skill (with cell), status and chat line the owner saw. Count casts of
  a skill, compare where ground spells landed, check blocked hits (damage 0).
- **The map log** (`<rig>/logs/map.log`): script errors in the test NPC, plan
  warnings, engine messages.
- **Ask the server:** the test NPC has small probes (`lpcells` counts Land
  Protector cells around the owner); `PROBE=lpcells` sends one each poll. Add a
  probe rather than guess.
- **Read rAthena** for a mechanic before building a plan on it
  (`src/map/battle.cpp`, `skill.cpp`, `status.cpp`, `mob.cpp`,
  `db/pre-re/*.yml`, `conf/battle/*.conf`). Several guesses here were wrong
  until checked.

## 8. Things that cost hours

- **The test client runs behind the script.** It works its commands off one after another,
  waits included, so after a long stretch of them (stocking four bags) it is seconds behind
  and lines of the pack before are still arriving. Until 2026-10-12 `rwparty.py` took such a
  "left=0" line for the new pack's and ended it at once: packs of three came out at a
  constant 13, 15 or 17 s. It now waits for the NPC's own "pack" line, and the NPC times the
  last kill itself (to 0.1 s; the poll only comes every 2 s). Results from before that date
  with those round times for a pack of three are suspect.
- **Never `pkill -f <pattern>`**: it matched the agent's own shell and killed
  it, and everything it had started. Kill by PID (`pgrep -fa`, then `kill`).
- **Start long runs as tracked background jobs**, not with `nohup ... &` in a
  shell that may die.
- **Companions fire no `OnPCDieEvent`** (the engine skips it). Falls are counted
  from the HP the harness polls.
- **A test-NPC message is cut off past about 200 characters**; the status line
  is split for that.
- **Clear the whole map between fights** (`killmonster <map>, "All"`): what a
  boss summoned outlives it and joins the next fight.
- **Ground spells outlast a fight** (a Land Protector lasts 345 s): each boss
  fight starts at a fresh spot.
- **Companions' gear is the engine's own.** A card put into it by script is
  lost. To test a piece of gear's effect, give the bonus with `bonus_script`
  (`ARMOR_ELE=` does that for an armour element).
- **Read a skill's element in `skill_db.yml`.** Hell Judgement has none, so it
  is Neutral, not dark: dark-resistant armour did nothing.
- **A monster's skill is melee within 3 cells and ranged beyond**
  (`skillrange_by_distance`): Safety Wall stops it close, Pneuma far.
- **Kyrie Eleison and Assumptio end each other** in pre-renewal.
- **Land Protector (official behaviour) does not shield its own edge** from a
  Meteor landing outside it, and `MoveTo: { Field }` walks to the edge.
- **`{ Enemy: boss }` matches any boss-class monster**, a boss's miniboss
  slaves included (Dark Lord's Illusions). NEEDS.md 12.
- **companion-roles' "never hit a boss from where it cannot fight back"** holds
  casters for whole fights against bosses that would not teleport for it.
  Boss plans `Disable` it. NEEDS.md 6.
- **Ground-spell damage** in the client log comes from the spell's unit id,
  not the monster: count it separately (whohurts.py does).

## 9. When the plan system cannot do it

Write it in [`NEEDS.md`](NEEDS.md): what is needed, what happens now (with the
evidence: a trace line, a count), and a test case that shows it working. Add
new entries at the end of their section with the next number; never renumber,
others work from those numbers. Work round it in the plan if you can, and say
so in the plan's header.
