# Party tactics against bosses (pre-renewal)

The tactics a companion party uses against MVPs and minibosses, what each one
means, when it pays, how rAthena makes it work, and how a plan writes it. They
come from the boss tests (`../renewal-world/BOSSES.md`), player guides
(`MVP_TACTICS.md`) and the rAthena source (`DAMAGE_MECHANICS.md`, `CLASSES.md`,
`ITEMS.md`). Rule keys are the companion strategy table's
(`docs/mods/companion-strategies/reference.md` on the strategy-needs branch).

## How bosses are balanced

- **Tactics first.** A boss that is too hard is met with tactics, counters and
  preventions first: a plan, elements, cards and armour, the party's make-up,
  cures. Its damage and HP (and its slaves') come down only where no tactic
  helps, and the tactics tried are written down with the cut.
- **The trend, not the kill.** A test need not end in a kill: what counts is
  whether the party keeps wearing the boss down (its HP lost a minute) and how
  often it falls. A boss the party wears at a steady rate could be killed.
- **Phases.** A good boss changes tactics at HP thresholds (Mistress heals and
  casts Agi Up below 30 %, Orc Hero and Osiris Power Up below 30 %). A boss that
  uses everything from full HP gives a party nothing to learn; tests check that
  the party reaches each phase and handles it (`START_HP` starts a boss lower).
- **Not too easy.** Killable, not easy: clearly harder than the easy reference of
  its tier (for an endgame MVP and a level-95 party, Turtle General: 5-10 minutes,
  3-4 falls a minute), about 15-25 minutes with more falls in its later phases;
  every phase asks for its tactic; HP comes down only as far as needed
  (`../renewal-world/PORTING.md`, step 5).
- **Gear decides more than any rule.** A Gunslinger's gun (engine default ATK 4
  vs a +7 The Garrison with two cards) turned Mistress from 1 kill in 4 into 3
  in 4. Reference parties wear fixed gear (`GEAR=mid`).

## Defence

| Tactic | Meaning | How it works | Plan |
|---|---|---|---|
| **Safety Wall / Pneuma split** | Safety Wall under whoever is in melee with the boss, Pneuma for everyone 4 or more cells away | A monster's skill counts as melee within 3 cells and as ranged beyond (`skillrange_by_distance`); Safety Wall stops melee physical hits, Pneuma ranged ones; neither stops magic. Hell Judgement, Pulse Strike, Meteor Assault are physical | `Cast: MG_SAFETYWALL` with `Count: { Enemy: any, Mob: X, Around: target, Range: 3, AtLeast: 1 }`; Pneuma below |
| **Pneuma spot** | One Pneuma, at the Priest's feet, that the back line gathers on | Chasing each member with a Pneuma of its own left most off one when the strike landed | `Cast: AL_PNEUMA, Target: self` + `MoveTo: { Field: AL_PNEUMA, Owner: party, Depth: 1 }` for the back line |
| **Out of its reach** | Everyone but the tank 4 or more cells off the boss | Its melee and melee-range skills miss them; Pneuma covers the rest | `KeepDistance: { Min: 4, Max: 9 }` with `Target: { Enemy: boss, Mob: X }` |
| **Assumptio, not Kyrie** | High Priest keeps Assumptio (half damage) on everyone | Kyrie and Assumptio end each other (`status.yml`): with both cast, 116 Assumptios and 81 Kyries undid each other | `Cast: HP_ASSUMPTIO`, `Ban: [PR_KYRIE]` |
| **Tank with Devotion** | A Crusader/Paladin by the boss takes the Priest's hits | Without a tank the slaves go for the casters | `Cast: CR_DEVOTION` on `Role: support` |
| **Armour element** | Armour of the element that halves or cancels the boss's spells | Wind armour (Dustiness card) cut Mistress's Jupitel Thunder to a quarter. **A monster's normal attack has no element** (100 % to any armour): armour element only helps against its skills | gear (`ARMOR_ELE=` in tests; `Equip:` for unequipped companions) |
| **Raydric garment** | −20 % from Neutral | What a monster's normal attack is: the counter to slaves' melee | gear |
| **Basilica (safe room)** | Non-boss monsters cannot hit anyone inside | Nobody inside can use skills either (`status.cpp:2193`): a breather, not a place to fight from. Bosses ignore it | `Cast: HP_BASILICA` when the party must recover |
| **Status cures** | Lift silence, curse, stun at once | Lex Divina lifts silence from an ally; Status Recovery cures stun, freeze, stone; Panacea cures curse, Green Potion silence and poison. No item works while stunned, frozen, asleep or stoned | `Cast: PR_LEXDIVINA` on `{ Ally: having, Status: SC_SILENCE }`; `UseItem:` one rule per status (a `UseItem` list is an order of preference, not "whichever cures it") |
| **Step off its ground** | Leave a hostile field | A boss's Land Protector under the party erases its Pneuma and Safety Walls and nothing can be laid there | `Leave: { Field: SA_LANDPROTECTOR, Owner: enemy }` |
| **Counter Land Protector** | Lay a Land Protector on the boss's | Pre-renewal: one laid on another removes both (`skill.cpp`, "offensive Land Protector to delete both"), cell by cell: same level as the boss's | `Cast: SA_LANDPROTECTOR, Target: { Field: SA_LANDPROTECTOR, Owner: enemy }` after `MoveTo` its middle (`Depth: 5`); a strategy switch so the Sage's own LP is banned otherwise |
| **Deep in our Land Protector** | Stand in the middle of the party's Land Protector, not on its rim | A Meteor Storm landing outside still hits its edge (official `land_protector_behavior: 0`) | `MoveTo: { Field: SA_LANDPROTECTOR, Owner: party, Depth: 3 }` |

## Crowd control

The boss itself resists Stone, Freeze, Stun, Sleep, Silence, Blind, Curse, Decrease
AGI, Provoke and most other statuses (Class Boss gets `MD_STATUSIMMUNE`). **Its
slaves do not**: they are ordinary monsters. Crowd control is for the slaves, and
for the few effects that do land on a boss.

| Tactic | Meaning | Works on a boss? | Who |
|---|---|---|---|
| **Disable, don't kill, respawning slaves** | Put the slaves out of the fight alive | A boss summons a new pack when its slaves fall to its threshold (Leak: 5 more 10 s after 3 or fewer are left, so killing them brought a new pack every few seconds) | Sleep, Stun, Freeze below |
| **Sleep** | No action until hit | No (resisted); yes on slaves | Hunter Sandman trap (`HT_SANDMAN`, aimed in front of the slave: a trap cannot go on a monster's cell) |
| **Stun** | No action for a few seconds | No; yes on slaves | Whitesmith Hammer Fall (area, no damage), Champion Ki Explosion, Dancer Scream (hits the party too) |
| **Freeze** | No action, Water-weak and Fire-safe | No; yes on slaves | Wizard Frost Diver (one), Frost Nova (round itself), Storm Gust (area). Their damage can kill weak slaves and bring the next pack |
| **Quagmire** | AGI and DEX −10 a level, ends speed buffs | **Yes** (not BossResist) | Wizard. Against Mistress it took her HP loss from 3.3 % to 10.8 % a minute: her flee fell and the Knight and Hunter hit |
| **Slow Grace** | Slower attack and movement | **Yes** (not BossResist) | Dancer/Gypsy |
| **Ankle Snare** | Holds in place | Yes, for 1/5 of the time (pre-renewal) | Hunter, aimed ahead of the boss (`Aim: { Cells: 2, From: target, Lead: true }`) |
| **Fire Wall in its path** | A wall between a caster and what comes for it | Knocks slaves back; a boss is knockback-immune and walks through, taking every hit | `Cast: MG_FIREWALL, Aim: { Cells: 2 }` |
| **Ice Wall** | Block a path | Many MVPs teleport when they cannot reach their target ("rude attack") | Wizard; careful near a boss |
| **Basilica** | see Defence | Bosses ignore it | High Priest |

## Offence

| Tactic | Meaning | How it works | Plan |
|---|---|---|---|
| **Right element** | Attack with what the boss's element takes most | Earth does 200 % to Wind 4 (Mistress), Water 0 %; Fire 175 % to Earth 2 (Orc Hero), 0 % to its Fire 2 High Orcs; Holy 200 % to Undead 4, 150 % to Dark 2 | Sage endows (`SA_SEISMICWEAPON` …), Aspersio (needs Holy Water), elemental ammunition (the engine picks it), `Ban:` the useless elements for the boss **and** its slaves (a `Mob:` entry each: the boss's Ban holds only while it is the target) |
| **Cards** | Race, element and size cards in the weapon | Same kind adds, different kinds multiply: +20 % race × +20 % element = +44 % | `bosscards.py` picks two ordinary cards (no MVP cards) |
| **Focus the boss** | Everyone with a weapon on the boss | Mistress heals her slaves below 60 %: shooting them spread the damage thin | `SetTarget: true` with `Target: { Enemy: boss, Mob: X }` |
| **Save SP, burst at the threshold** | Hold the expensive skills until the boss's dangerous phase | A Knight out of SP after 70 s had nothing left below 30 %, where Mistress heals 9 999 a time | strategies: one with `Ban:` on the SP skills, `Switch:` at `enemy_hp_pct_lt32` |
| **Lex Aeterna on the big hit** | Double the next hit | Works on bosses | `Cast: PR_LEXAETERNA` before the burst |
| **Dispel the boss's buffs** | Take off Power Up (+200 % ATK, double HIT), Agi Up, Two-Hand Quicken | Dispel has no boss check (50 + 10 × level % chance). A monster's Agi Up is `SC_AGIUP`, not Increase AGI's status | `Cast: SA_DISPELL`, `When: { OR: [enemy_powerup, enemy_agiup, enemy_twohandquicken] }` |
| **Damage the boss cannot block** | Hits that ignore its defences | Mistress casts Pneuma on whoever shoots her; Desperado counts as melee (Pneuma does not stop it) and hits her slaves too | a Gunslinger: `Cast: GS_DESPERADO` beside the boss |
| **Don't waste SP** | Ban what does nothing | 70 Frost Divers (Water, 0 % to Wind 4) and 80 Provokes (nothing on a boss) in one Mistress fight | `Ban:` per boss and per slave |
| **Clear line** | Step out from behind an obstacle before casting | "no clear line to the target" refused about half a Sage's casts against Orc Hero | `MoveTo: { Sight: target }` above the casts |
| **No rude attacks** | Never hit a boss from where it cannot reach back | It teleports away (rude attack, idle or walking) | `MoveTo: reachable` |

## Sustain

| Tactic | Meaning | How it works | Plan |
|---|---|---|---|
| **Magnificat always** | Double the party's SP regeneration | With casters a must; cast whenever it is down **and nothing is on the Priest**: above the heals it was started 27 times in 13 minutes, broken off by hits, and the party fell twice as often | `Cast: PR_MAGNIFICAT`, `When: not_self_magnificat`, `Count: { Enemy: attacking, Who: self, Below: 1 }`, below the heals |
| **Ration Safety Wall** | Not one every 2 s | 109-186 walls in a fight left the Priest without SP to heal | `Cooldown: 6000`, `When: self_sp_ge120` |
| **Carry a kit, not too much** | Potions, gems, catalysts, ammunition | With Companion inventory on, a companion only has its bag. Above 50 % weight no natural SP regeneration; above 90 % no attacks. Condensed White Potions weigh 2, White 15 | `ITEMS.md` §7 |

## The party

What a boss party needs, from the tests (`CLASSES.md` has the jobs):

- **A healer with Magnificat** (Priest; High Priest for Assumptio and Basilica).
- **Utility for the boss's tricks**: a Wizard for Quagmire (flee), a Sage for
  Dispel, endows and the counter Land Protector.
- **A tank** when the boss has slaves that go for the casters.
- **Damage the boss cannot block or dodge**, of the right element: physical
  damage dealers with the right cards; magic against low MDEF only (Mistress's
  MDEF 60 cut every spell to 40 %).
- **Crowd control** when slaves respawn.
- For endgame MVPs, a transcendent party: at level 95 it killed Turtle General
  in 309-586 s against a second-job party's 656-810 s.

Five members of the wrong kind cannot beat what five of the right kind can:
without the Wizard, Mistress was worse in every run; with a Gunslinger as the
sixth, or a proper gun on a fifth, she died.
