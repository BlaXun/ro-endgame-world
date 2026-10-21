# Pre-renewal MVPs: what players do (research notes for the boss plans)

Collected 2026-10-10 for the boss plans in this directory (`mvp-*.party.yml`) and
the boss method (`tools/renewal-world-monsters/BOSSES.md`). Tactics, not rare gear:
the companions own no inventory, and a plan must work for a party that owns no
MVP cards. Skill facts marked **[rA]** are read from rAthena's pre-renewal
`db/pre-re/mob_skill_db.txt`, `mob_db.yml` and `status.yml` and checked in its
source; the rest is quoted from players. Old guides are mostly solo tricks (Asura,
Reject Sword, teleport-dodging); party guides barely exist, so most of this is
reasoned from the kits and tested here.

## Across bosses

- **Hell Judgement** (Dark Lord, Baphomet, Lord of Death) is **Neutral** physical
  damage, not dark, all round the boss (14 cells), every 10 s, with Curse [rA].
  A monster's skill counts as melee within 3 cells and as ranged beyond
  (`skillrange_by_distance`), so **Safety Wall** stops it in melee and **Pneuma**
  beyond [rA]. iRO Wiki: "You can avoid the damage of this skill using Safety
  Wall when closer than 4 cells to the monster ... and Pneuma when more than 4
  cells away" ([irowiki](https://irowiki.org/classic/NPC_HELLJUDGEMENT)). Undead
  armour (Evil Druid) does nothing against it; Ghost armour (Ghostring, rare)
  only cuts it to a quarter. iRO's later rebalance made it always melee; that is
  not pre-renewal.
- **Kyrie Eleison and Assumptio end each other** (`EndOnStart` in status.yml)
  [rA]. Two Priests casting both undo each other's work.
- **Dark Blessing** sets the target's HP to 1: Amon Ra 50 % in a fight, Dark Lord
  and Pharaoh 5 % [rA]. "The only skill with a high chance to kill you"
  ([myrolife](http://myrolife.blogspot.com/2015/12/cocos-mvp-guide-lord-of-death.html));
  the counter players name is a Bathory card (gear). Heal at once.
- **Power Up / Agi Up below 30 % HP** on nearly all of them [rA]. "Quagmire or
  Dispel cancels it" (myrolife): the Sage's Dispel.
- **Teleport for being rude-attacked**, idle or walking only [rA]. "Amon Ra only
  teleports if you attack offscreen like casting SG" (RMS forum, below). "Avoid
  Ice Wall, since it makes the MVP teleport" (myrolife).
- **Land Protector** erases ground spells (Meteor Storm, Lord of Vermilion, Fire
  Wall, Fire Pillar, Quagmire, Venom Dust), the party's own too: Pneuma, Safety
  Wall, Sanctuary, Magnus [rA]. It does not stop Hell Judgement, Earthquake or
  Grand Darkness, which are not ground spells.
- **Holy against Dark and Undead bosses:** Aspersio on the melee is free.

## Dark Lord (Undead 4, Demon, 720k HP, MDEF 70)

- **Kills:** Hell Judgement; Meteor Storm level 11 (50 % in a fight and chasing);
  Fire Wall; Dark Blessing; Break Helm; six Dark Illusions (miniboss slaves,
  103k HP, Meteor Storm level 5 of their own) [rA]. "The deadliest part is that
  he casts meteor storm frequently"
  ([gamergroundz](http://gamergroundzdatabase.blogspot.com/2009/12/ragnarok-mvp-boss-guide.html)).
- **Players:** physical damage with Holy ("With aspersio from a priest, it will do
  260% damage"; spells are poor, "he has very high magical defence"); Magnus on
  the Illusions; Land Protector against Meteor Storm; kill the Illusions down to
  three (it calls more only at three or fewer).
- **Measured here** (8 companions at 99, 5 minutes, falls a minute): Hell
  Judgement did about half the damage the party took, the Illusions 40 %.

## Baphomet (Dark 3, Demon, 668k HP)

- **Kills:** Hell Judgement level 5; Earthquake level 5 below 80 % HP (30 s);
  Lord of Vermilion level 21; Brandish Spear (knock-back); Break Armor; Power Up
  below 30 %; heals while idle; 4 Baphomet Jr, then 6 at three or fewer [rA].
- **Players** ([RMS forum](https://forum.ratemyserver.net/general-discussion/(non-renewal)-tanking-amon-rabaphometkiel-with-high-priest/)):
  "you should be tanking it against a wall, so brandish doesn't push you back";
  "keep pneuma on the sniper at all times because of Hell's Judgement"; "Safety
  Wall works fine if you got Magnus Exorcismus to clear the minions first";
  "You can tank Baphomet with just heals and occasional pots until he gets to 30%
  HP, then Powerup makes it really hard". Keep it fighting (it heals when idle),
  Dispel Power Up, Holy damage.

## Lord of Death (Dark 3, Demon, DEF 77, 603k HP)

- **Kills:** Hell Judgement **level 10**; Stun attack; Decrease Agi; Brandish
  Spear; Undead Attribute Change (Heal then hurts the target); Grand Darkness,
  Power Up and Agi Up below 30 %; slaves [rA]. Hell Judgement "can easily wipe
  the party"; Grand Darkness "is only troublesome if you are in Melee Range"
  ([myrolife](http://myrolife.blogspot.com/2015/12/cocos-mvp-guide-lord-of-death.html)).
- **Players:** Safety Wall and Pneuma for Hell Judgement; Dispel or Quagmire for
  Agi Up; criticals, Acid Terror and Asura ignore its DEF.

## Amon Ra (Earth 3, 1.21M HP, cannot walk)

- **Kills:** Meteor Storm level 11, at once on anyone who shoots it or begins a
  cast at it, and after Fire Wall, Storm Gust, Thunderstorm, Heal, Magnus or
  Meteor Storm on it; Fire Pillar; Blood Drain ("6-9k HP"); Dark Blessing 50 %;
  summons (Khalitzburg, Mimic, Arclouse), which "can flood the map"; heals while
  idle [rA, myrolife](https://myrolife.blogspot.com/2015/12/cocos-mvp-guide-amonra.html).
- **Players:** "Place Land Protector beneath him"; Fire Pillar: "Land Protector
  or Pneuma cancels"; melee tank, the Sniper "can hit it from outside its range,
  while you keep up sanctuary/Safety Wall/Heals" (RMS forum above). Nothing cast
  at it from range: every shot calls summons.
- **Measured here:** Land Protector under it, summons first, no Lex Aeterna: 10 %
  of its HP a minute and 10 falls a minute, against 6 % and 16.5 without a plan.
  The summons did most of the damage.

## Pharaoh (Dark 3, Demihuman, DEF 67, MDEF 70)

- **Kills:** Dark Blessing 5 %; Energy Drain (100 % after a Fire Wall); Dark
  Strike level 10; Thunderstorm after a Fire Wall; Power Up below 30 %; 6 slaves
  (Marduk, Pasana) [rA]. (An old guide's "no offensive spells" is wrong for rA.)
- **Players:** Holy (Aspersio; Dark takes 175 %); no Fire Wall near it; Dispel.
- **Measured here:** nobody falls, but the party took off only 8 % a minute: a
  damage problem (DEF and MDEF), not a survival one.

## The others, briefly

- **Orc Hero:** Spiral Pierce "11-15k", "32-38k in Power-Up state", and Pneuma
  blocks it; Safety Wall against the High Orcs' knock-back; "bring a sage to
  Dispel it"; Quagmire; a Devotion tank; "bring down its mob count to 3"
  ([myrolife](https://myrolife.blogspot.com/2015/12/cocos-mvp-guide-orc-hero.html)).
  Fire on the tank's weapon (Flame Launcher) against Earth 2.
- **Osiris:** Meteor Assault level 10 at every chance, Stone Curse, Curse and
  Poison, Venom Dust, Quagmire [rA]: cure petrify, curse and poison; Holy or Fire;
  Dispel.
- **Turtle General:** Sonic Blow level 10, Water Ball, Stun, Weapon Break,
  Maximize Power [rA]: cure stun, Fire, Assumptio on the tank.
- **Eddga:** walks very slowly; Fire Ball level 93 while chasing [rA]: "Hit and
  run tactic works well on him" (gamergroundz); Water.
- **Phreeoni:** Wide Stone below 80 %, Hiding and Heal below 20 % [rA]: cure
  petrify, Sight or Ruwach to find it.
- **Mistress:** Jupitel Thunder (knock-back), Wide Silence, Stop, heals her
  slaves, Pneuma on herself when shot [rA]: melee damage, Safety Wall against
  knock-back, cure silence ("bring green pots"; Panaceas, gamergroundz), "knights
  need the +80 hit rate" (gamergroundz); Earth on the tank's weapon (Seismic
  Weapon); Magic Rod against Jupitel
  ([myrolife](http://myrolife.blogspot.com/2016/01/cocos-mvp-guide-mistress.html)).
  Lex Divina lifts silence from an ally in rAthena (`skills/acolyte/lexdivina.cpp`).
- **Party guides:** none found for Mistress, Orc Hero or Osiris; the published
  guides are solo or duo, often transcendent. Party plans combine them with
  rAthena's skill table.

## Sources

- [iRO Wiki Classic: NPC_HELLJUDGEMENT](https://irowiki.org/classic/NPC_HELLJUDGEMENT)
- [RateMyServer forum: tanking Amon Ra, Baphomet, Kiel with a High Priest (pre-re)](https://forum.ratemyserver.net/general-discussion/(non-renewal)-tanking-amon-rabaphometkiel-with-high-priest/)
- [RateMyServer: Dark Lord's skills](https://ratemyserver.net/index.php?page=mob_skill_analysis&m_id=1272)
- [Coco's MVP guides (myrolife): Lord of Death](http://myrolife.blogspot.com/2015/12/cocos-mvp-guide-lord-of-death.html), [Amon Ra](https://myrolife.blogspot.com/2015/12/cocos-mvp-guide-amonra.html), [Orc Hero](https://myrolife.blogspot.com/2015/12/cocos-mvp-guide-orc-hero.html), [Mistress](http://myrolife.blogspot.com/2016/01/cocos-mvp-guide-mistress.html)
- [Gamergroundz MVP boss guide](http://gamergroundzdatabase.blogspot.com/2009/12/ragnarok-mvp-boss-guide.html)
- [GameFAQs: resisting Hell's Judgement](https://gamefaqs.gamespot.com/boards/561051-ragnarok-online/40937048)
