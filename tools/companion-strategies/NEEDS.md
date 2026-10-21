# What the companion strategies could not do

Found while writing and testing party plans for the renewal-world monsters
(`bifrost-fields.party.yml`). Each entry says what was missing, why a plan
needs it, what it does now, and a test case that fails today and should
pass once it is added.

The test cases run on a pre-renewal server with the population engine and
a hidden owner whose party is four companions (Lord Knight `tank`, High
Priest `support`, High Wizard and Sniper `attacker`, all level 99), the way
the plans were tested. The rig that does this is described at the end.

## Status

On branch `core/population-engine-strategy-needs` (2026-10-10; the boss tests
run on it):

| # | | Status |
|---|---|---|
| 1 | `Role` lists in selectors | done |
| 2 | `{ Enemy: casting, Skill }` | done |
| 3 | `NotOwner` in `Ally` selectors | done |
| 4 | `encounter_ended { Boss }` | done |
| 5 | `Requires: { Lacks }` reads the skill selection | done |
| 6 | `Reach` asks rAthena's rude-attack question | done |
| 7 | gear for a fight | done for companions that **started unequipped** (Settings → Population): `Equip: <item>`, any worn piece, weapons too; spares are handed over in the Companions window's Gear tab or `@companion spare`; put back by itself, and the save keeps the normal set. Gear sets: see the note under 7 |
| 8 | a draft comes at its owner's level | done |
| 9 | companions renamed after a restart | not reproduced |
| 10 | `OnPCDieEvent` for companions | done |
| 11 | `MoveTo { Depth }` | done |
| 12 | `Mob` in selectors and `Count` | done |
| 13 | why a cast was refused, in the trace | done |
| 14 | move to where there is a clear line to the target | done (`MoveTo: { Sight: target }`) |
| 15 | aim a ground cast at a cell, and lead a walking monster | done (`Aim: { Cells, From, Lead }`) |
| 16 | `encounter_ended` is missed by a companion that sits down to rest | done |
| 17 | the expanded jobs have no skill rotation (auto-attack only) | done: lists for 23, 24, 25, 4002-4007, 4046-4049, 4190, 4211, 4212, 4215, 4218, 4239, 4240, Desperado for 4306, and `get_base_job` asks rAthena's job map. Rig-tested: Gunslinger, Ninja, Taekwon, Star Gladiator, Soul Linker, High Mage, High Swordsman. Not tested: Super Novice (would not draft on the rig) and the jobs plain pre-renewal lacks |
| 18 | aim a ground cast at an enemy's ground field (Land Protector on a boss's Land Protector) | done: `Target: { Field: SA_LANDPROTECTOR, Owner: enemy, Within: 9 }` with a ground `Cast`; lands on the field's middle cell. Land Protector reaches 2 cells, so pair it with `MoveTo: { Field, Owner: enemy, Depth: 5 }` below it; with Companion inventory on the caster needs the gemstones in its bag |

New entries are added at the end of their section with the next number;
numbers are never reused.

## Strategy table

### 1. A selector's `Role` takes one role, not a list

**Need:** `Target: { Ally: attacked, Role: [attacker, support] }`: wall
whoever is being hit unless it is the tank.

**Why:** a healer protects the squishy members and leaves the tank to its
heals. With one role per selector it takes two rules, and they share no
cooldown, so the same member can be walled twice.

**Now:** `Requires: { Role: [..] }` takes a list, but the selector reads
`Role` as one string. A list makes the whole entry fail to load with
"This entry is shaped wrong (check failed: has_val(node))", pointing at the
entry rather than the key, so every rule of that monster is lost.
(`Job` in the same selector takes a list.)

**Test:**
```yaml
- Mob: MIMING
  Jobs:
    - Job: Priest
      Rules:
        - Name: t_wall_squishy
          Priority: 90
          Cast: MG_SAFETYWALL
          Target: { Ally: attacked, Role: [attacker, support] }
          Cooldown: 4000
```
Load it. Expected: no error; with the Wizard being hit, the trace shows
`t_wall_squishy` walling the Wizard; with only the tank being hit, the rule
does not fire. Today: the entry is skipped at load.

At the least, the load error should name the key (`Role` in a selector
takes one value) rather than the entry.

### 2. `{ Enemy: casting }` cannot ask which skill

**Need:** `Target: { Enemy: casting, Skill: [WZ_JUPITEL, MG_THUNDERSTORM] }`:
interrupt only the casts that matter.

**Why:** Little Fatum casts Lightning Bolt on chase, Jupitel Thunder and
Thunderstorm, all cancellable by damage; it also casts Lex Aeterna, which
is not worth a Double Strafe. A Sniper that interrupts every cast spends its
SP on the wrong ones. `On: { Event: monster_casts, Skill }` can filter by
skill, but an event fires once, and the interrupt has to keep going (and
pick the nearest such caster) for as long as the cast lasts.

**Now:** `{ Enemy: casting }` picks any monster that is casting.

**Test:** two Little Fatums, one casting Lex Aeterna (1 s cast in its skill
row) and one casting Jupitel Thunder (1.5 s).
Expected: a rule with `Target: { Enemy: casting, Skill: WZ_JUPITEL }`
fires at the second and never at the first.

### 3. No way to leave the owner out of an `Ally` selector

**Need:** `Target: { Ally: missing, Status: SC_BLESSING, NotOwner: true }`:
buff the party, not the player it follows.

**Why:** the owner can be someone a buff is refused on. With a hidden owner
(the test rig's), a Priest's "whoever lacks Blessing" picked the owner every
turn: 239 refused Blessings and 239 refused Increase AGIs in one 90-second
fight, and the companions went unbuffed. A player may also not want the
companions' buffs (a Soul Linker's spirit, a class that buffs itself
differently).

**Now:** one rule per role (`Role: tank`, `Role: attacker`, `Role:
support`), which leaves out the owner because it has no role. Six rules
where two would do, and see 1: a list of roles would make it two again.

**Test:** owner hidden (`@hide`), a High Priest companion with
`Target: { Ally: missing, Status: SC_BLESSING, NotOwner: true }`.
Expected: the trace shows Blessing on each companion, no "not cast
(refused)" lines.

### 4. `encounter_ended` cannot tell a boss from an ordinary encounter

**Need:** `On: { Event: encounter_ended, Boss: true }`, or the event firing
only for the monster a plan was about.

**Why:** examples/mods/companion-roles regroups with the owner when an
encounter ends (`boss_gone_say`, `boss_gone_regroup`), meant for a boss that
teleported away. A monster plan with `Encounter: true` (needed so that a
healer, who has no target, uses it) makes ordinary monsters encounters too.
Then every kill ended an encounter: against Pom Spider the Wizard walked
back to the hidden owner and stood there from 30 s to 66 s of the fight.

**Now:** the monster plan says `Disable: [boss_gone_say, boss_gone_regroup]`
for `Job: All`. Each plan for ordinary monsters with `Encounter: true` has
to know about those two rules of another mod.

**Test:** companion-roles plus a plan `Mob: PORING, Encounter: true` with
any rule. The party kills a Poring 10 cells from the owner. Expected: no
`boss_gone_regroup` in the trace. Today: "retreat to owner".

### 5. A plan cannot tell which build a companion plays

**Need:** two Champions in one party, one playing the combo plan and one the
Asura plan; generally, one class with several builds (BUILDS.md lists two to
five per class).

**Why:** `Build` + `Requires` picks a plan by skills, role or level. Every
companion has its whole skill tree, so skills do not tell builds apart, and the
owner's skill selection (`@companion skills <name> toggle <skill>`, the
companion window) is not seen by `Requires`. With Chain Combo unticked, a
Champion still matched `Requires: { Skills: [MO_CHAINCOMBO] }` (the combo plan,
whose combo rules then never fired) and never matched `Lacks: [MO_CHAINCOMBO]`
(the Asura plan): it stood and did nothing.

**Now:** the Asura plan requires `Role: none` and the combo plan `Role:
attacker`, a test workaround: a player who sets no role gets the Asura build.

**Test:** a Champion with Chain Combo unticked
(`@companion skills Ash toggle MO_CHAINCOMBO`), a plan with
`Build: asura, Requires: { Lacks: [MO_CHAINCOMBO] }` and one with
`Build: combo, Requires: { Skills: [MO_CHAINCOMBO] }`. Expected: the trace
shows the Asura plan's rules. Today: the combo plan's, refused. Either
`Requires` reads the selection, or a companion carries a build name
(`@companion build Ash asura`, `Requires: { Build: asura }`).

### 6. `Reach: false` holds casters at bosses that cannot teleport for it

**Need:** "never hit a boss from where it cannot fight back" applies only
where hitting from there would really make the boss teleport.

**Now:** companion-roles' `no_rude_attack` (`Reach: false` → `MoveTo:
reachable`, else `Hold`, priorities 98 and 97) won almost every turn for the
Priests and the Wizard against Dark Lord and Amon Ra, with "cannot move (no
reachable cell nearby)". Amon Ra cannot walk at all (AI 10), and Dark Lord
casts Teleport for being rude-attacked only when idle or walking, never in
the fight itself (its mob_skill_db rows). In rAthena an immobile monster is
rude-attacked only in narrow cases (`mob.cpp`, the rude-attack check). Both
boss plans now `Disable` the two rules; without that, the party's casters
stood still for most of a 5-minute fight.

**Test:** a level-99 party of eight against Amon Ra on an open field, the
Wizard traced. Expected: Fire Bolts at it from 5-9 cells, and it does not
teleport. Today: `no_rude_attack_hold: hold` most turns.

### 7. A plan cannot prepare gear for a fight

**Need:** a boss plan names gear a member should wear for it (a shield card
against bosses, armour of an element), and the companion puts it on when the
encounter starts.

**Now:** companions have no inventory of their own ("What it cannot do yet"
in the reference), and a card put into a companion's armour by script is
lost: the engine dresses it from its gear set. The boss tests give a member
an armour element with `bonus_script` instead (`ARMOR_ELE=` in
`rwparty.py`). Not needed for the tactics found so far (Pneuma and Safety
Wall against Hell Judgement), but players do prepare for some bosses (an
Alice shield, fire-resistant armour against Meteor Storm).

**Test:** a plan for Dark Lord that says "Raydric garment"; the companion
wears one while Dark Lord is within 14 cells.

**More evidence (Mistress, 2026-10-10):** gear decides more than any rule.
A level-80 party of five (Priest, Wizard, Sage, Hunter, Gunslinger) with the
same plan killed Mistress once in four 15-minute fights while the Gunslinger
wore the engine's gear set (`para_gun`: `P_Revolver1`, ATK 4, or
`P_Revolver2`, ATK 60), and three times in four, in 162, 309 and 412 s, with
a +7 The Garrison carrying a Caramel and a Mandragora card (put on by the
test NPC: `arm#` in `rwtest.txt`; it stays on, the persistence row shows it).

The engine's other gear sets name rental weapons that pre-renewal's item
table does not have (`P_Slayer1`, `P_Bow1`, `P_Staff1` ...), so companions
end up with what is left, different from server to server: a Hunter with a
Composite Bow (ATK 29) on one and an Arbalest (ATK 90) on another, a caster
with an Arc Wand (60) or a Mighty Staff (130). Two runs of the same plan
then measure different parties. Two needs come out of it: gear sets that
exist in pre-renewal and are the same each time (an engine data fix), and,
for plans, gear a plan can ask for (this item).

**Answer (2026-10-10, strategy-needs session):** the plan half is built
(`Equip`, status table). The gear-set half is smaller than it looks: on this
branch every gear set already has a `PreRenewal` block (upstream e78e19c), and
measured against the pinned pre-renewal item table no slot of any set a
pre-renewal job wears comes out empty. The rental names (`P_Slayer1`, `P_Bow1`
...) are the renewal pools those blocks replace. What is left is that a slot is
a pool and the engine picks one at random: Arc Wand or Mighty Staff, Composite
Bow or Arbalest, `P_Revolver1` or `P_Revolver2`. A test that wants the same
party every run can have it today without an engine change: draft with
`population_engine_companion_start_unequipped: 1` and hand each member its gear
from the test NPC; the engine then never dresses it. Making the engine's own
pick fixed would change what every player's companions wear and is not done.

### 11. `MoveTo` the middle of a field, not its nearest cell

**Need:** "stand inside the party's Land Protector", deep enough that ground
spells landing outside it do not reach.

**Now:** `MoveTo: { Field: SA_LANDPROTECTOR, Owner: party }` walks to the
nearest cell of the field, its edge. rAthena's official Land Protector
(`land_protector_behavior: 0`) blocks a Meteor Storm that lands on it, but
one that lands outside still hits whoever stands on its edge (its 7x7
splash). Against Amon Ra, with a Land Protector up all fight, Meteor Storm
and Fire Pillar still did 62 % of the damage the party took. The Amon Ra
plan works round it with a signal: the Sage, on its own Land Protector,
signals every 2 s and everyone does `MoveTo: event`.

**Test:** a Sage lays Land Protector (level 5, 11x11) and a Wizard 9 cells
off runs `MoveTo: { Field: SA_LANDPROTECTOR, Owner: party, Depth: 3 }`.
Expected: it stops 3 or more cells inside the edge. Today: on the edge.

### 12. A selector for the encounter's own monster

**Need:** in a boss plan, `Target`, `Count` and `KeepDistance` about *that*
boss (Dark Lord), not about any boss-class monster near it.

**Now:** `{ Enemy: boss }` and `Count: { Enemy: boss }` match every monster of
the boss class, and some bosses' slaves are minibosses: Dark Lord's six Dark
Illusions. In the Dark Lord plan, "4 or more cells off the boss" and "Pneuma
where no boss stands within 3 cells" measured from whichever Illusion was
nearest, and the Sniper's Ankle Snare "on the boss" went on Illusions 9 times
out of 10 (a trace: `hj_snare_the_boss: Ankle Snare on Dark Illusion`).
Filtering by kind cannot separate them: Dark Lord and Dark Illusion are
both Undead 4, Demon, Large. Selectors (`population_strategy.cpp`, the
`Target` and `Count` keys) take `Boss`, `Race` and `Element`, and a rule's
`Enemy:` filter `Element`, `Race`, `Size` and `Boss`; only an entry's `Mob:`
and `encounter_ended` name a monster.

**Simplest shape:** `Mob` in a selector and in `Count`, as an entry takes it
(AegisName or id, or a list): `Target: { Enemy: boss, Mob: DARK_LORD }`,
`Count: { Enemy: any, Mob: DARK_LORD, Range: 3, Below: 1 }`.

**Test:** an encounter plan for DARK_LORD with `Target: { Enemy: boss, Mob:
DARK_LORD }`, Dark Lord plus two Dark Illusions in range. Expected: the rule
picks Dark Lord every time. Today `{ Enemy: boss }` picks the nearest of the
three, and `Mob` in a selector is an unknown key.

### 13. The trace says a cast was refused, not why

**Need:** when a `Cast` rule's skill is refused, the trace names the reason:
out of range, the cell is taken, the companion is still in its cast delay,
not enough SP, a catalyst missing, rAthena's own skill check (and which).

**Now:** `rule hj_snare_the_boss: Ankle Snare not cast (refused)`, 14 times
in one minute against Dark Lord, and the same for Pneuma, Magnus Exorcismus
and Assumptio. Whether a plan should move the companion closer, aim
elsewhere, wait, or drop the rule depends entirely on the reason, and today
it can only be guessed. The selector already explains itself this way
(`Poring is claimed (frozen) by Kira`).

**Test:** a Sniper traced with a rule `Cast: HT_ANKLESNARE, Target: { Enemy:
boss }` against a boss standing on the only free cell next to a wall, then
against one 12 cells off. Expected: `not cast (the cell is taken)` and `not
cast (out of range: 12 > 3)`. Today: `not cast (refused)` both times.

### 14. Move to where there is a clear line to the target

**Need:** a caster or archer whose casts are refused for want of a clear line
(a tree, a wall, a corner between it and the target) steps to a cell from
which it has one, instead of standing still.

**Now:** with NEEDS 13 the trace says so: against Orc Hero on `alb2trea`, a
level-80 Sage tried Frost Diver, Fire Bolt (three rules) and Heaven's Drive
57, 57 and 50 times in 82 s, each `not cast (no clear line to the target)`
or `(... to the cell)`, cast 25 times in all, and spent the other turns on
companion-roles' last rule, `no_melee: hold` (105 times). The Wizard did
the same less often; against Osiris the Priest's Heals were refused the same
way. Nothing in the table moves a companion for line of sight:
`MoveTo: reachable` asks whether the monster could reach the companion, a
different question, and `KeepDistance` keeps a distance, not a line. Every
real map has obstacles, so a party loses its casters wherever the boss
stands near one.

**Shape:** `MoveTo: { Sight: target, Within: 6 }`, the nearest cell from
which the rule's target is in the clear (and, with `KeepDistance`'s band,
at that distance); or the rotation itself steps aside when every cast it
tried this turn was refused for line of sight.

**Test:** a Wizard 7 cells from a Poring with a wall between them (a corner
of `prt_fild08`'s fence, or any map's wall), a bolt rule and the line-of-
sight rule above. Expected: it steps out from behind the wall within a few
turns and casts. Today: `not cast (no clear line to the target)` every
turn, then `hold`.

### 15. A ground cast lands only at its target's feet

**Need:** an Ice Wall between a Wizard and the monster coming for it, a Fire
Wall in a monster's path, a trap in front of a boss; and for a spell with a
cast time, the cell a walking monster will be on when the cast lands.

**Now:** a ground `Cast` lands on the cell of its `Target`, always a unit. An
Ice Wall aimed at the monster goes up on the monster; a trap aimed at it is
refused (NEEDS 13: `the cell is taken: Dark Lord stands on it`). Nothing takes
a monster's walk or the companion's cast time into account.

**Shape:** `Aim: { Cells: 3 }` (three cells from the companion, toward the
target), `Aim: { Cells: 2, From: target }` (two cells in front of the target),
`Aim: { Lead: true }` (where its walk will have brought it when the cast
lands), or together.

**Test:** a Wizard 7 cells from a held Raydric with `Cast: WZ_ICEWALL, Aim:
{ Cells: 3 }`. Expected: the trace shows the wall 3 cells from the Wizard and
4 from the Raydric. A Raydric walking in, `Cast: MG_FIREWALL, Aim: { Lead:
true }`: the trace shows the cell ahead of it (`led 1 cells`).

## Engine and testing

These are not plan keys, but they shaped what could be measured.

### 8. A drafted companion's level is clamped to its job profile

**Need:** a companion at a chosen level, for a test (and for a player who
wants a level-99 party).

**Why:** a balance test compares party against monster at a fixed level.
`@companion draft 4009` by a level-99 owner gave a High Priest of 81, a
Sniper of 72, a Lord Knight of 79 and a High Wizard of 96: each clamped to
its profile's range.

**Now:** `#blvl <name> 98` and `#joblvl <name> 69` afterwards. They work,
but at job level 50 or more the engine then tries a third-class job change
every few seconds, which pre-renewal refuses ("job change 4008 -> 4054
failed", a warning per companion per try).

**Test:** with the hire mode free (`population_engine_companion_hire: 0`),
a level-99 owner drafts `@companion draft 4009 Hela f`. Expected: `@companion
list raw` shows `Hela|High Priest|99`. Separately: a level-99 trans
companion in pre-renewal stops trying to change to a third class.

### 9. Saved companions come back under other names after a restart

**Need:** `@companion summon Hela` after a server restart brings back Hela.

**Now:** the summon answers "Summoned 1 saved companion(s)", the map-server
log shows "recalled 3 companion(s)", but the companions in the world are
named Corazel, Serachor and Caeles, and `@where Hela` finds nobody. The log
also warns that their indexes are "owned by a persisted companion; refusing
it for ambient spawn ... the collision that makes a companion's skill
selection attach to the wrong shell".

**Test:** draft Hela, Wiz and Snip; restart the map server; log in;
`@party test`; `@companion summon Hela`. Expected: `@where Hela` names a
map. Today: "Character not found".

### 10. `OnPCDieEvent` does not run for companions

**Need:** a script that counts deaths in a fight sees a companion die.

**Now:** the map-server log says "companion Tank died and remains available
for resurrection", but an `OnPCDieEvent` label does not run for it, so a
test counted 0 deaths for a party that wiped.

**Test:** a script with `OnPCDieEvent: announce strcharinfo(0) + " died", bc_all; end;`.
A companion is killed (`@killmonster` is not it: spawn a monster that kills
it, or `#kill <name>` if that is supported). Expected: the announcement.

### 16. `encounter_ended` is missed by a companion that sits down to rest

**Need:** when a boss dies or teleports away, every companion that fought it
sees `encounter_ended` (and `target_lost`), whatever its HP and SP.

**Now:** the engine's rest runs before a companion's turn (`pop_shell_rest`,
then `continue`, in the companion loop of `population_engine.cpp`), and a
companion rests as soon as it is no longer needed: no target, not hit for 5 s,
no threat on the party. The tick a lone boss goes is the tick that becomes
true, so a companion below its rest mark (30 % SP or HP by default) sits down
at once and takes no turn. Its rules never see the monster gone, and once it
stands up again more than 2 s have passed and the event is dropped. Found with
a Lord Knight out of SP: `boss gone, regroup` fired in some runs and not in
others, by how much SP the fight had left it.

**Shape:** a companion whose fight has just ended, with that ending not yet
seen by its rules, takes its turn before it rests; it rests the tick after.

**Test:** a Lord Knight and a Champion against an Angeling with 5 000 000 HP
for 10 s; the Lord Knight's SP is set to 0; the Angeling is killed. A rule
`On: { Event: encounter_ended, Boss: true }` on the Lord Knight. Expected: the
trace shows the event. Today: nothing, and the Lord Knight sits down.

Not covered by this: a companion already resting sees no event at all
(`party_chat`, `signal`, `party_member_died`), because no rule runs during a
rest.

## The rig

`rig-pe` in the session scratchpad: the pinned rAthena with
`scripts/apply-server-mods.sh` applied, built pre-renewal at packet version
20221005, on its own ports (46900/46121/45121, database 43306),
`population_engine_enable: 1`. `rwparty.py` plays the owner: it removes
the old companions, drafts the party, sets roles and Attack mode in party
chat, hides, spawns a pack 6-9 cells away on `alb2trea` (a field with no
spawns of its own) and polls each member's HP and SP until the pack is dead,
the party is, or 180 s pass. A test NPC (`rwtest.txt`) spawns the pack and
counts kills.

### 17. The expanded jobs have no skill rotation: they only auto-attack

**Need:** an expanded-job companion that fights as its job does: a Gunslinger's
Desperado among a pack (it hits everything within 3 cells and counts as a
short-range attack, so a boss's Pneuma does not stop it), Tracking or Full
Buster on one target, Increasing Accuracy, Gatling Fever, Flip the Coin for the
coins; a Ninja's, a Taekwon's, a Star Gladiator's and a Soul Linker's skills the
same way.

**Now:** `population_skill_db.yml` has no entry for any of these jobs, and the
profiles in `population_engine.yml` have no `Skills:` block. The rotation falls
back to the base job's list, which for these jobs is missing too, and then the
companion "auto-attacks only" (`population_engine_combat.cpp`). No list for:
Super Novice (23), Gunslinger (24), Ninja (25), Taekwon (4046), Star Gladiator
(4047), Soul Linker (4049), expanded Super Novice (4190), Kagerou (4211), Oboro
(4212), Rebellion (4215), Summoner (4218), Star Emperor (4239), Soul Reaper
(4240). Only their 4th jobs (4302-4307) have one, and Night Watch's leaves out
Desperado. The class mods that add Kagerou, Oboro, Rebellion, Star Emperor and
Soul Reaper to pre-renewal ship none either.

Found against Mistress: a level-80 Gunslinger with a Revolver and 3 000 Bullets
cast no Gunslinger skill in a 15-minute fight, only normal shots. A plan's
`Cast` rules can still use the skills a companion has learned, so this is the
engine's default play, not something a plan cannot do.

**Shape:** an entry per job, like the 2nd jobs' (Desperado with `Condition:
enemy_count_nearby` and `AroundRange: 3`; the self buffs with `not_self_status`;
Flip the Coin while it has fewer coins than the buffs need), and Desperado in
the Night Watch list. For the jobs a class mod adds, either the mod ships its
own `population_skill_db.yml` rows (if the engine reads them from a mod) or the
engine carries them.

**The fallback is wrong as well:** `get_base_job()` (`population_engine.cpp`,
about line 9323) tests `job_id >= JOB_KNIGHT && job_id <= JOB_ROYAL_GUARD`
first, which is ids 7..4066, so nearly every job maps to Swordman. A job with
rows of its own never reaches the fallback, but one without them gets the
Swordman's rows: a Super Novice casts Bash, Magnum Break, Endure and Provoke.
The same function picks the base job's gear profile (`population_engine.cpp`
about 1425, 1438).

**Test:** a level-80 Gunslinger with a Revolver and Bullets against three
Orc Warriors standing beside it. Expected: Desperado in the client log
(`skill_cast` 516). Today: none. The same for a Ninja, a Taekwon and a Star
Gladiator with their own skills.

### 18. A ground cast cannot be aimed at an enemy's ground field

**Need:** a Sage or Professor lays its own Land Protector on the one a boss put
down, which removes both (pre-renewal: `skill.cpp` about line 11233, "offensive
Land Protector to delete both"), and the Priest's Pneuma or Safety Wall can go back
on that ground. More generally: a ground skill aimed at the cell of a ground unit
someone else placed.

**Now:** `Field:` is a condition only (is there one within `Range`, `At: target`),
and `MoveTo: { Field }` / `Leave: { Field }` walk onto or off one. Nothing gives a
`Cast` the field's cell as its target. Found against Leak (renewal-world's
converted MVP): it lays Land Protector about every 40 s (20 in a 13-minute fight)
on whoever it targets, erasing the party's Pneuma and Safety Walls there, which are
what stop its Hell Judgement and Pulse Strike. The plan can only step off it.

**Shape:** a target `{ Field: SA_LANDPROTECTOR, Owner: enemy, Within: 9 }`: the
cell of the nearest such unit (its centre for a field of several cells), for a
ground `Cast`. With `Aim` it could also be the cell nearest the companion.

**Test:** a monster with Land Protector (or a GM-cast one owned by a monster) on
the ground 5 cells from a Professor; a rule `Cast: SA_LANDPROTECTOR`, `Target:
{ Field: SA_LANDPROTECTOR, Owner: enemy }`. Expected: both Land Protectors are
gone. Today: no such target.

