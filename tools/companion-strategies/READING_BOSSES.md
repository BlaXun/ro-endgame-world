# Reading a boss: what its designers meant

Every number and every skill on a boss was put there by someone, for a reason.
Together they say what fight the designers had in mind: who should deal the
damage, what the party has to survive, what it has to do quickly, which of its
usual tricks will not work. Read that first, and the counters follow from it;
plan against a boss without reading it, and the plan fights its design (three
versions of a Pneuma plan against Leak, a boss that lays Land Protector to erase
Pneuma).

So, for every boss, before writing its plan or judging its balance, ask of each
thing on it: **why did the developers do this? What does it ask of the party,
and what does it take away?**

This file is how to ask it. The mechanics behind each answer are in
[DAMAGE_MECHANICS.md](DAMAGE_MECHANICS.md); the jobs in [CLASSES.md](CLASSES.md);
the tactics in [TACTICS.md](TACTICS.md).

## How to read

1. **List everything**: its stats (`mob_db.yml`), its skills with their state,
   condition and value (`mob_skill_db.txt`: `attack` or `chase`, `always` or
   `myhpltmaxrate 30`, `slavele 3`, `longrangeattacked` …), its slaves and their
   stats, its map.
2. **For each item, write one line**: "this is here so that …". Some items
   explain themselves only next to another one (Land Protector next to Hell
   Judgement).
3. **Sum it up in two or three sentences**: the intended fight. Who deals the
   damage, how the party survives, what has to be quick, what is denied.
4. **Plan for that fight.** A trick that undoes the design (our own Land
   Protector on the boss's) may stay as a reward for knowing the game, but the
   boss is balanced for the fight it was designed for, without the trick.
5. **Check the conversion kept the message** (below): a converted boss can say
   the opposite of what its designers wrote.

## Its numbers

| What you see | What it likely says |
|---|---|
| **High DEF, low MDEF** | the damage is meant to come from magic: bring casters |
| **Low DEF, high MDEF** | physical damage dealers; spells mostly for utility (Mistress: MDEF 60 takes most of every spell, and the guides say "avoid Wizards") |
| **Both high** (Pharaoh: DEF 67, MDEF 70) | a slow fight: damage that ignores defence (Lex Aeterna, crits, fixed damage), or patience |
| **High AGI / FLEE** | physical hits will miss: Quagmire, HIT gear, crits, magic (Mistress: AGI 165; the Knight missed three hits in four until Quagmire) |
| **High DEX / HIT** | dodging will not save anyone: armour, damage reduction, heals |
| **High VIT** | physical damage reduced further, and statuses resisted |
| **High INT** | magic reduced further (soft MDEF) |
| **High LUK** | crits less sure, perfect dodge |
| **Huge HP** | a long fight: sustain (SP regeneration, potions, cures) matters more than burst |
| **Moderate HP with a heal or Power Up below a threshold** | burst at the threshold: save SP and Lex Aeterna for it |
| **Element** | what to attack it with (Wind 4: Earth 200 %, Water 0 %), and what armour its own spells call for |
| **Race, size** | the cards that pay (race and size cards multiply); a race group can matter (Orc Hero is not in the Orc group) |
| **Attack range above 1** | it reaches past the cell in front of it: keep-away distances grow |
| **Fast walk** (low `WalkSpeed`) | it cannot be outrun: no kiting plan; slow walk invites hit-and-run (Eddga) |
| **Fast attacks** (low `AttackDelay`) | many small hits: per-hit reduction (Safety Wall counts hits, Kyrie too) |
| **AI** | `Ai: 10` stands still (Amon Ra: ranged attacks and staying out of its reach); aggressive or not; whether it changes target |

## Its skills

Each skill on a boss either **threatens** something, **denies** a tactic, or
**sets a pace**. Read which.

| A boss with … | says … | so the party … |
|---|---|---|
| **Land Protector** | "no ground tricks": Pneuma, Safety Wall, Storm Gust, Quagmire, traps, Sanctuary, Magnus, Basilica are erased where it lands | stands through its strikes (HP, heals, Assumptio, a tank), moves the fight off the field, kills with single-target damage |
| **Hell Judgement, Pulse Strike, Earthquake** | heavy hits on everyone near; physical | Safety Wall within 3 cells, Pneuma beyond, unless the boss also denies them (above) |
| **Pneuma on itself when shot** (`longrangeattacked`) | "no archers": ranged physical damage is meant to fail | melee or magic (Mistress) |
| **Magic Mirror, Golden Thief Bug style magic immunity** | "no casters" | physical damage |
| **Dispel or Strip on the party** | "your buffs and gear are not safe" | re-buff quickly; keep a spare (Strip Weapon: a second weapon, Chemical Protection) |
| **Wide Silence, Slow Cast, Spell Breaker** | casters are its target | cures (Lex Divina, Green Potions), physical damage carries the fight |
| **Wide Stun, Sleep, Stone, Freeze** | the party will lose turns | status-resistance cards, Status Recovery, someone free to cure |
| **Critical Wound** | healing is cut | more healers, damage reduction, a shorter fight |
| **Wide Curse, Bleeding** | slow attrition | cures (Panacea, Blessing) or accept it |
| **Stop, Ankle-style holds on the party** | "you will be pinned" | do not stand where it can pin you |
| **Knock-back skills** (Jupitel Thunder, Sight Rasher) | positions will not hold | Safety Wall against knock-back, a shield card, no plan that depends on standing on one cell |
| **Teleport when rude-attacked** | "no free hits from afar" | attack only from where it can hit back |
| **Teleport at random while idle or walking** | "be quick" | keep it in combat; finish it fast |
| **Heal on itself below 30 %** | the last third is a race | burst at the threshold, more damage than it heals |
| **Power Up, Agi Up, Two-Hand Quicken below 30 %** | "it gets worse at the end" | Dispel (works on bosses), Quagmire, a last defensive push |
| **Summons that refill** (`slavele 3`, short delay) | "you cannot kill them all" | disable them alive (sleep, stun, freeze; slaves are not bosses), or kill them all at once, or ignore them and take the boss |
| **Summons of one element** | which area spell they want (Banaspaty are Fire 3: Water) | and which they shrug off |
| **Call Slave** | its slaves come back to its side | fight the pack where it stands |
| **Skills only while chasing** (`chase`) | it punishes running away | do not kite it, or expect those skills when you do |
| **Skills only in melee** (`attack`) | it punishes standing next to it | only the tank in reach |
| **Everything `always` from full HP** | no phases | (a design gap worth fixing, see below) |
| **Skills at HP thresholds** | phases | plan each phase, test each (`START_HP`) |

Skill levels and rates matter too: a 100 % rate at level 10 is the boss's main
weapon; a 5 % rate at level 1 is flavour.

## Its slaves and its map

- **Slaves' stats** say the same as the boss's: their element is the area spell
  that clears them, their DEF/MDEF who clears them, whether they are bosses
  (statuses work on ordinary slaves).
- **A slave without its own attack speed** in the data attacks every 0.1 s: a
  data gap, not a design (Leak's Banaspaty; `../renewal-world/PORTING.md` §3).
- **Its map**: a narrow corridor makes area spells and kiting hard; open ground
  invites them. Its map's monsters arrive with it.

## Worked examples

**Mistress** (pre-renewal, level 74). Wind 4, AGI 165, MDEF 60, DEF 40; Pneuma on
whoever shoots her; Jupitel Thunder with knock-back; Silence and Wide Silence;
Heal and Agi Up below 30 %; Giant Hornets that refill.
*Intended fight:* melee with Earth weapons, through her flee (Quagmire); casters
silenced and their spells weak, so they support; a burst through her last 30 %,
Dispel on Agi Up. *What worked:* exactly that, plus Wind armour against Jupitel
and a sixth member (or a proper weapon) for the last third.

**Leak** (renewal, level 94 there). Resists magic more than physical damage
(renewal: 37 % off a hit, 50 % off a spell). Hell Judgement and Pulse Strike,
**Land Protector beside them**; Wide Curse, Silence, Stun, Sleep, Bleeding; Critical
Wound, Slow Cast, Strip Weapon; Dragon Fear; Banaspaty (Fire 3) that refill.
*Intended fight:* the classic Pneuma answer is denied; the party stands through
heavy strikes with a tank, heals and damage reduction, under status pressure,
casters slowed, healing cut. Its slaves want Water and, being ordinary
monsters, crowd control. *Lesson:* a Pneuma plan fought the design; balance the
stand-through fight.

**Orc Hero** (level 77). Earth 2; High Orcs (Fire 2) with knock-back; Spiral
Pierce; Power Up and Two-Hand Quicken below 30 %. *Intended fight:* control the
orcs (Water on them, Fire is useless), Safety Wall against their knock-back,
Fire on him, and a Dispel ready for his last 30 %.

**Osiris** (level 78). Undead 4; Meteor Assault all round him at every chance;
Stone Curse; Ancient Mummies. *Intended fight:* Holy damage; nobody but the tank
in reach (Meteor Assault counts as melee: Safety Wall stops it); cures for
stone; the mummies handled (they are Undead too).

**Amon Ra** (level 88). `Ai: 10`, it does not move; Meteor Storm and Fire Pillar
around it; summons when attacked from afar. *Intended fight:* stand where its
ground spells cannot land (a Land Protector of your own under the party, deep
inside it); the summons first.

## When the conversion changes the message

`build_monsters.py` ranks DEF, MDEF and the stats **each on its own** against
pre-renewal monsters of the level the boss lands at, and a ranking can turn a
profile around. Check it, but compare **reductions, not raw numbers**: the two
eras turn DEF and MDEF into damage differently.

- Pre-renewal: DEF and MDEF are percentages (DEF 30 takes 30 % off a hit).
- Renewal: a hit is multiplied by (4000 + DEF) / (4000 + 10 × DEF), a spell by
  (1000 + MDEF) / (1000 + 10 × MDEF) (`battle.cpp`, renewal branch).

Leak shows why. In renewal it has DEF 280 and MDEF 128, which looks like a
physical tank; but DEF 280 takes only 37 % off a hit and MDEF 128 takes 50 % off
a spell: it resists **magic** more. Converted it has DEF 30 and MDEF 45 (30 % and
45 %): the same message, kept. The converter notes each boss whose order (which
of physical and magic it resists more) is not the same in both eras; such a boss
is corrected in `monsters.csv`: the designers' choice is respected.

## What to write down

For each boss plan (`mvp-<name>.party.yml`), its header starts with the intended
fight in two or three sentences, before "what kills" and "so". When balancing,
BOSSES.md records whether the boss was balanced for its intended fight or for a
trick, and which.
