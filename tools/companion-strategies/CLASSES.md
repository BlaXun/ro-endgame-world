# Pre-renewal jobs for party plans: what each one brings

A reference for writing companion party plans (`db/population_strategy.yml`,
rules with `Cast: SKILL_NAME`, a `Target:` and a `When:`): which job brings what
to a party, and what works on a boss. It covers the second jobs, their
transcendent versions and the expanded jobs, as **rAthena pre-renewal**
implements them. [BUILDS.md](BUILDS.md) has the stat builds and web sources for
each class; [MVP_TACTICS.md](MVP_TACTICS.md) has the per-boss notes. This file
does not repeat them.

**Ground truth.** The rAthena fork (`development/rathena`, `master` at
`c8b69e407`): `db/pre-re/skill_db.yml`, `db/pre-re/skill_tree.yml`,
`db/pre-re/status.yml`, `conf/battle/skill.conf`, `src/map/skills/**`,
`src/map/skill.cpp`, `src/map/battle.cpp`, `src/map/status.cpp`. Numbers in the
skill tables are read from `skill_db.yml` at the highest level the job's skill
tree allows. Roles and builds are common pre-renewal knowledge (iRO Wiki
Classic, RateMyServer pre-re), cross-checked against BUILDS.md. **None of the
web pages was re-fetched for this file**, so any statement about how a skill
plays that is not marked **[rA]** should be treated as unverified, and a few
are marked **[u]** where I am less sure.

## How to read the tables

| Column | Meaning |
|---|---|
| Skill | AEGIS name, as `Cast:` takes it, then the rAthena English name |
| SP | SP cost at the level shown (the highest the job learns) |
| Cast / ACD | base cast time / after-cast delay in ms at that level. Pre-re cast time falls with DEX and is gone at 150 DEX, except skills marked *fixed* (`IgnoreDex`). ACD does not fall with DEX; Bragi (`BA_POEMBRAGI`) and Kiss-of-the-gods gear lower it |
| Ele | element of the damage. *wpn* = the weapon's (or endow's, or arrow's) element |
| Rng | how the hit counts, which decides what blocks it **[rA]**: **M** = melee (weapon/misc skill with range < 4): Safety Wall blocks it. **R** = ranged (weapon/misc skill with range ≥ 4): Pneuma blocks it. **Mag** = magic: neither blocks it. A dash = no damage |
| Needs | catalyst, weapon, ammo, spheres/coins, or a status that must be on |

How the range class is worked out **[rA]**: `battle_range_type` in
`battle.cpp` calls a player's skill short if `skill_get_range2 < 4`, otherwise
long. `skillrange_from_weapon: 0` in `conf/battle/skill.conf`, so a negative
`Range:` in `skill_db.yml` is taken as its absolute value, not the weapon's
range. So Pierce (`-2`) is melee, Spear Stab (`-4`) is ranged, and **Desperado,
Meteor Assault and every self-centred weapon AoE (range 0) is melee**: Safety
Wall stops them, Pneuma does not. Traps are always short. Monsters use distance
instead (`skillrange_by_distance: 14`): within 3 cells a monster's attack is
melee, beyond it ranged.

Safety Wall and Pneuma also protect the party **from** the boss: Safety Wall
under a member stops the boss's melee (and its skills cast from ≤ 3 cells),
Pneuma stops its ranged weapon hits. Neither stops magic.

---

## What a boss shrugs off, and what still works [rA]

A monster with `Class: Boss` gets `MD_DETECTOR | MD_STATUSIMMUNE |
MD_KNOCKBACKIMMUNE` in `MobDatabase::loadingFinished` (`src/map/mob.cpp`).
`status_change_start` then refuses every status flagged `BossResist` in
`db/pre-re/status.yml` (`status.cpp`, `SCF_BOSSRESIST`). Guardians get
`MD_STATUSIMMUNE` only.

**Resisted by bosses (BossResist):** Stone, Freeze, Stun, Sleep, Poison, Deadly
Poison, Curse, Silence, Confusion, Blind, Bleeding, Coma, Fear, Burning,
Provoke, **Blessing** (the curse on undead/demon), **Decrease AGI**, all four
Strips (`RG_STRIP*`, `ST_FULLSTRIP`, `GS_DISARM`), Blinding Mist (`PF_FOGWALL`),
Gravitation's status, Close Confine, Classical Pluck (`BD_ROKISWEIL`),
Mental Sensing, Hidden Water's slow (`NJ_SUITON`).

**Not BossResist, so they land on a boss:**

| Effect | Skill | Note |
|---|---|---|
| Lex Aeterna (next hit ×2) | `PR_LEXAETERNA` | fails on a frozen or stoned target only |
| Quagmire (AGI/DEX −10/lv on monsters, ends Inc AGI, Adrenaline, quickens, Wind Walk, Concentration) | `WZ_QUAGMIRE` | MVP_TACTICS: Quagmire or Dispel takes off a boss's Power Up / Agi Up |
| Dispel | `SA_DISPELL` | success 50+10×lv %; no boss check; a monster also drops its target |
| Fiber Lock (pinned, FLEE −50 %, next fire hit ×2) | `PF_SPIDERWEB` | |
| Vital Strike's broken joints (DEF2 −50 % shoulder, −25 % waist; slow; etc.) | `LK_JOINTBEAT` | |
| Down Tempo (soft DEF = 0) | `BD_ETERNALCHAOS` | ensemble |
| Slow Grace (ASPD and move slowed) | `DC_DONTFORGETME` | |
| Fling (DEF and VIT DEF −5 %/coin) | `GS_FLING` | |
| Eske (target ATK +300 %, DEF halved) | `SL_SKE` | double-edged |
| Eswoo (move slowed) | `SL_SWOO` | duration ÷5 on status-immune |
| Signum Crucis (DEF down on undead/demon) | `AL_CRUCIS` | |
| Ankle Snare | `HT_ANKLESNARE` | pre-re only: holds a boss for **1/5** of the time (`skill.cpp`, `#ifndef RENEWAL`) |
| Tarot Card | `CG_TAROTCARD` | works, but ~15 % is *The Lovers*, which **teleports the boss away** off PvP maps |

**Skills that check for a boss and fail or weaken [rA]:** Provoke
(`swordman/provoke.cpp`), Stone Curse, Mind Breaker, Elemental Change (all
four), Venom Splasher (and pre-re also needs the target ≤ 75 % HP), Spell
Breaker (10 % chance), Absorb Spirit Sphere (no SP from a boss), Bull's Eye
(no ×5 bonus), Spiral Pierce's and Glacier Fist's root, Grimtooth's slow, Throw
Zeny (÷3), Wall of Thorns, Electric Shocker. Bowling Bash cannot knock a boss
back, so on a lone boss it hits once, not twice (`swordman/bowlingbash.cpp`:
the second hit needs another monster in the splash).

**Detector:** bosses see Hiding, Cloaking and Stalk/Chase Walk. A hidden
Assassin or Rogue is still attacked, and the boss keeps targeting them.

**Basilica does not protect against bosses** (pre-re `battle.cpp`: its block
skips `MD_STATUSIMMUNE` attackers).

**Things that always connect:** pre-re criticals ignore FLEE and DEF
(`is_attack_hitting`, `attack_ignores_def` under `#ifndef RENEWAL`); magic never
misses; skills with `IgnoreFlee` in `skill_db.yml` (Asura, Occult Impaction,
Back Stab, Blitz Beat, Falcon Assault, Land Mine/Blast Mine/Claymore,
Gloria Domini, Martyr's Reckoning, Acid Terror, Acid Demonstration,
Gravitation, Final Strike, Throw Zeny, Ground Drift, Counter Kick). Union
(`SG_FUSION`) makes every hit land. Skills that also ignore DEF: Asura,
Acid Terror, Spiral Pierce, Piercing Shot, Martyr's Reckoning, Fire Pillar
(MDEF), Counter Attack.

**Other boss facts that change plans:**
- Kyrie Eleison and Assumptio end each other (`EndOnStart`); so do Kaite and
  Assumptio. One Priest per target.
- Magnus Exorcismus only damages Undead-element or Demon-race targets in pre-re
  (`UNT_MAGNUS`, `#ifndef RENEWAL`).
- Ice Wall makes many MVPs teleport (MVP_TACTICS.md).
- Land Protector (on either side) wipes ground spells: Meteor Storm, Storm Gust,
  Lord of Vermilion, Fire Wall, Fire Pillar, Quagmire, Safety Wall, Pneuma,
  Sanctuary, Magnus, Volcano/Deluge/Whirlwind, traps.

---

## Party buffs at a glance

Who gives the party what. "Self" means the caster only.

| Buff | Skill | From | Effect (pre-re) | Note |
|---|---|---|---|---|
| Blessing | `AL_BLESSING` | Acolyte line, Super Novice | +STR/DEX/INT by level (+10 at L10), cures Curse/Stone | 240 s |
| Increase AGI | `AL_INCAGI` | Acolyte line, SN | +AGI by level, move speed | 240 s; costs the caster 15 HP; Quagmire ends it |
| Angelus | `AL_ANGELUS` | Acolyte line, SN | VIT DEF +% to the party around | |
| Kyrie Eleison | `PR_KYRIE` | Priest | barrier: absorbs (10+2×lv) % MaxHP or (lv/2+5) hits **[rA]** | ends Assumptio |
| Magnificat | `PR_MAGNIFICAT` | Priest | **double SP regen** (`regen->rate.sp += 100`) **[rA]**, party around | 90 s, 4 s cast |
| Gloria | `PR_GLORIA` | Priest | +30 LUK, party around | 30 s |
| Impositio Manus | `PR_IMPOSITIO` | Priest | +5×lv weapon ATK **[rA]** | 60 s |
| Suffragium | `PR_SUFFRAGIUM` | Priest | next cast −15/30/45 % | not on self |
| Aspersio | `PR_ASPERSIO` | Priest | Holy weapon | Holy Water |
| B.S. Sacramenti | `PR_BENEDICTIO` | Priest | Holy armour | needs 2 Acolyte-line jobs next to the Priest [u] |
| Assumptio | `HP_ASSUMPTIO` | High Priest | damage taken ÷2 (÷1.5 on PvP maps) **[rA]** | ends Kyrie / Kaite |
| Devotion | `CR_DEVOTION` | Crusader | the Crusader takes the hits for up to 5 members | level gap ≤ 10, range limits [u] |
| Providence | `CR_PROVIDENCE` | Crusader | +Holy and Demon resistance | not on self or Crusaders [u] |
| Endows | `SA_FLAMELAUNCHER` / `SA_FROSTWEAPON` / `SA_LIGHTNINGLOADER` / `SA_SEISMICWEAPON` | Sage | weapon element | 1 elemental stone each, 30 min |
| Volcano / Deluge / Whirlwind | `SA_VOLCANO` / `SA_DELUGE` / `SA_VIOLENTGALE` | Sage | ground: +ATK fire / +MaxHP water / +FLEE wind, to those standing on it | Yellow Gemstone |
| Wind Walker | `SN_WINDWALK` | Sniper | +move speed, +FLEE, party | |
| Adrenaline Rush | `BS_ADRENALINE` | Blacksmith | +ASPD (axe/mace users), party | Full Adrenaline (`BS_ADRENALINE2`, with the Blacksmith spirit) takes any weapon |
| Power-Thrust / Weapon Perfection | `BS_OVERTHRUST` / `BS_WEAPONPERFECT` | Blacksmith | +ATK % (party gets a smaller share) / no size penalty, party | |
| Chemical Protection | `AM_CP_*`, `CR_FULLPROTECTION` | Alchemist / Creator | weapon/armour cannot be stripped or broken | Glistening Coat |
| Songs, dances, ensembles | `BA_*`, `DC_*`, `BD_*` | Bard, Dancer | see Bard/Dancer | the performer does not get its own song |
| Soul links | `SL_*` | Soul Linker | job-specific (table under Soul Linker) | |
| Ka- buffs | `SL_KAIZEL`, `SL_KAAHI`, `SL_KAUPE`, `SL_KAITE` | Soul Linker | revive, heal-on-hit, dodge, magic reflect | on others only while the caster has the Soul Linker spirit (or on a Soul Linker, spouse, child); otherwise the caster is stunned [rA] |
| Gospel | `PA_GOSPEL` | Paladin | random party buffs and enemy debuffs every few s | the Paladin cannot act while it runs |
| Kihop | `TK_POWER` | Taekwon (passive) | +ATK per party member | [u] |

---

## Swordsman line

First-job skills every Knight and Crusader also has: `SM_BASH` (melee, 15 SP),
`SM_MAGNUM` (fire AoE around self, 30 SP + 16 HP, ACD 2000), `SM_PROVOKE`
(fails on bosses), `SM_ENDURE` (no flinch, 10 s cooldown), `SM_AUTOBERSERK`.

### Knight (7) / Lord Knight (4008)

**Role:** main melee damage; AoE on packs (Bowling Bash, Brandish Spear);
off-tank. **Builds:** Bowling Bash (2H sword, Two-Hand Quicken), spear/peco
(Pierce, Brandish, Spear Boomerang), Counter Attack/crit. LK: Spiral Pierce
(heavy spear), Frenzy (`LK_BERSERK`) solo-killer, Parry tank.

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `KN_BOWLINGBASH` Bowling Bash | 500 % hit with 1-cell splash; chains on packs | 22 | 700 / – | wpn | M | |
| `KN_PIERCE` Pierce | 200 %, 1/2/3 hits by target size small/med/large | 7 | – | wpn | M | spear |
| `KN_SPEARSTAB` Spear Stab | line hit, knocks back | 9 | – | wpn | R | spear |
| `KN_BRANDISHSPEAR` Brandish Spear | frontal AoE | 12 | 700 / – | wpn | M | spear, **riding** |
| `KN_SPEARBOOMERANG` Spear Boomerang | 11-cell throw | 10 | – / 1000 | wpn | R | spear |
| `KN_TWOHANDQUICKEN` Two-Hand Quicken | +ASPD, 300 s | 50 | – | – | – | 2H sword |
| `KN_AUTOCOUNTER` Counter Attack | stance: counters the next melee hit as a crit (ignores FLEE/DEF) | 3 | – | wpn | M | |
| `KN_CHARGEATK` Charge Attack | rush 14 cells | 40 | 500 / – | wpn | R | |
| `KN_ONEHAND` One-Hand Quicken | +ASPD with 1H sword | 100 | – | – | – | needs the Knight spirit |
| `LK_AURABLADE` Aura Blade | +ATK that ignores DEF | 50 | – | – | – | |
| `LK_CONCENTRATION` Concentration | +ATK/HIT %, −DEF | 30 | – | – | – | |
| `LK_PARRYING` Parrying | blocks some melee | 50 | – | – | – | 2H sword |
| `LK_BERSERK` Frenzy | MaxHP ×3, max ASPD, no SP regen, no skills/items, FLEE −50 % [rA], HP drain [u] | 200 | – | – | – | |
| `LK_SPIRALPIERCE` Spiral Pierce | 5 hits, scales with weapon weight, **ignores DEF** | 30 | 1000 / 2000 | wpn | R | spear |
| `LK_HEADCRUSH` Traumatic Blow | hit + Bleeding | 23 | – / 500 | wpn | R | |
| `LK_JOINTBEAT` Vital Strike | hit + broken joint (**works on bosses**) | 20 | – / 1000 | wpn | R | spear |

**Against bosses:** Bowling Bash is one 500 % hit on a lone boss, two only when
slaves stand in the splash. Spiral Pierce ignores DEF and is ranged (a boss's
Pneuma would stop it, so would Pneuma from an enemy Priest-type monster).
Vital Strike's DEF-down lands on bosses. Counter Attack crits through FLEE/DEF.
Provoke does nothing to a boss. Weak to boss Quagmire/Decrease AGI on
themselves (end Two-Hand Quicken).
**Gives the party:** a damage sponge; nothing else.
**Companion rotation:** yes (7, 4008): Bowling Bash, the spear skills, quickens,
Counter Attack, LK self-buffs, Frenzy, Spiral Pierce, Traumatic Blow, Vital
Strike.

### Crusader (14) / Paladin (4015)

**Role:** tank and party protector (Devotion, Defender, Providence), holy
damage vs undead/demon (Grand Cross). **Builds:** Devotion/tank (VIT, shield),
Grand Cross (INT/VIT, holy), Spear Quicken/Shield Boomerang. Paladin:
Martyr's Reckoning, Shield Chain, Gloria Domini, Gospel support.

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `CR_HOLYCROSS` Holy Cross | 2 hits, 100+35×lv % each, Blind chance | 20 | – | Holy | M | |
| `CR_GRANDCROSS` Grand Cross | ATK+MATK holy cross around self, 3 cells | 100 + 20 % HP | 3000 / 1500 | Holy | Mag [u] | hurts the caster too |
| `CR_SHIELDCHARGE` Smite | hit + Stun + knockback | 10 | – | wpn | M | shield |
| `CR_SHIELDBOOMERANG` Shield Boomerang | 11-cell throw | 12 | – / 700 | neutral | R | shield |
| `CR_AUTOGUARD` Guard | block chance vs. melee/ranged hits | 30 | – | – | – | shield |
| `CR_REFLECTSHIELD` Shield Reflect | reflects melee % | 80 | – | – | – | shield |
| `CR_DEFENDER` Defending Aura | −ranged damage, slower | 30 | – / 800 | – | – | shield |
| `CR_DEVOTION` Sacrifice | takes hits for up to 5 members | 25 | 3000 / – | – | – | |
| `CR_PROVIDENCE` Resistant Souls | +holy/demon resistance on another | 30 | 3000 / – | – | – | |
| `CR_SPEARQUICKEN` Spear Quicken | +ASPD | 60 | – | – | – | 2H spear |
| `AL_HEAL`, `AL_CURE` | Heal (L10) and Cure from the Crusader tree | 40 / 15 | – / 1000 | Holy | Mag | |
| `PA_PRESSURE` Gloria Domini | fixed damage, ignores FLEE/element, drains target SP [u] | 50 | 4000 / 4000 | – | R (misc) | |
| `PA_SACRIFICE` Martyr's Reckoning | next 5 attacks deal damage from the Paladin's own HP, ignore DEF/FLEE | 100 | – / 2000 | – | M | |
| `PA_GOSPEL` Battle Chant | random party buffs/heals and enemy damage/debuffs every few s, 60 s | 100 | – | – | – | caster cannot act |
| `PA_SHIELDCHAIN` Shield Chain | 5 hits, shield weight/refine | 40 | 1000 / 1000 | – | R | shield |

**Against bosses:** Devotion + a healer on the Crusader turns the boss's damage
onto one durable target; Defender halves ranged hits; Grand Cross does holy
damage regardless of FLEE (strong vs Dark/Undead bosses, but costs 20 % HP per
cast). Holy Cross on Dark bosses. Martyr's Reckoning hits through FLEE/DEF.
Gospel's enemy effects include statuses bosses resist. Shield Boomerang with
the Crusader spirit always hits and does double damage [rA].
**Gives the party:** Devotion, Providence, Heal/Cure, Gospel.
**Companion rotation:** yes (14, 4015). **`PA_GOSPEL` is not in it**, so only a
plan can cast Gospel. `PR_KYRIE` is in it but not in the pre-re Crusader skill
tree, so the engine's legality filter drops it.

---

## Acolyte line

Acolyte skills every Priest and Monk has: `AL_HEAL` (40 SP, Holy, also damages
Undead), `AL_INCAGI`, `AL_DECAGI` (fails on bosses), `AL_BLESSING`,
`AL_ANGELUS`, `AL_PNEUMA` (10 SP, blocks ranged weapon hits on a 3×3), `AL_CRUCIS`,
`AL_RUWACH`, `AL_CURE`, `AL_TELEPORT`, `AL_WARP`, `AL_HOLYLIGHT` (quest).

### Priest (8) / High Priest (4009)

**Role:** the healer and buffer; the SP economy (Magnificat); damage multiplier
(Lex Aeterna); anti-undead. **Builds:** full support (INT/DEX/VIT), battle
priest (mace, STR/AGI, Impositio), ME priest (Magnus Exorcismus, Turn Undead
for undead/demon maps). HP: Assumptio, Basilica, Meditatio (heal/SP regen).

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `AL_HEAL` Heal | heals; damages Undead | 40 | – / 1000 | Holy | Mag | |
| `PR_SANCTUARY` Sanctuary | ground heal over time; damages undead/demon | 42 | 5000 / – | Holy | Mag | Blue Gemstone |
| `PR_KYRIE` Kyrie Eleison | barrier, see buffs table | 35 | 2000 / 2000 | – | – | |
| `PR_MAGNIFICAT` Magnificat | 2× SP regen, party | 40 | 4000 / 2000 | – | – | |
| `PR_GLORIA` Gloria | +30 LUK, party | 20 | – / 2000 | – | – | |
| `PR_IMPOSITIO` Impositio Manus | +25 ATK | 25 | – / 3000 | – | – | |
| `PR_SUFFRAGIUM` Suffragium | next cast faster | 8 | – / 2000 | – | – | not self |
| `PR_ASPERSIO` Aspersio | Holy weapon | 30 | – / 2000 | – | – | Holy Water |
| `PR_BENEDICTIO` B.S. Sacramenti | Holy armour | 20 | – | – | – | |
| `PR_LEXAETERNA` Lex Aeterna | target's next damage ×2 (**works on bosses**) | 10 | – / 3000 | – | – | |
| `PR_LEXDIVINA` Lex Divina | Silence (resisted by bosses) | 10 | – / 3000 | – | Mag | |
| `PR_STRECOVERY` Status Recovery | cures Freeze/Stone/Stun | 5 | – / 2000 | – | – | |
| `PR_SLOWPOISON`, `AL_CURE` | Poison / Silence-Blind-Confusion | 12 / 15 | | | | |
| `PR_TURNUNDEAD` Turn Undead | chance to kill Undead outright, else damage | 20 | 1000 / 3000 | Holy | Mag | |
| `PR_MAGNUS` Magnus Exorcismus | 7×7 ground, 10 hits; **only Undead/Demon** in pre-re | 58 | 15000 / 4000 | Holy | Mag | Blue Gemstone |
| `ALL_RESURRECTION` Resurrection | revive | 60 | 2000 / 3000 | – | – | Blue Gemstone |
| `MG_SAFETYWALL` Safety Wall | blocks melee hits on one cell | 40 | 1000 / – | – | – | Blue Gemstone |
| `PR_REDEMPTIO` Redemptio | revive all party around (costs the caster) | 400 | 4000 fixed | – | – | |
| `HP_ASSUMPTIO` Assumptio | damage taken ÷2 | 60 | 3000 / 1500 | – | – | ends Kyrie |
| `HP_BASILICA` Basilica | sanctuary zone: non-boss monsters cannot hit in [rA] | 120 | 9000 / 6000 | – | – | Yellow+Red+Blue Gem, Holy Water |
| `HP_MEDITATIO` Meditatio | passive: +Heal power, +SP regen, +MaxSP | – | | | | |

**Against bosses:** the Priest is the reason a party survives a boss. Lex
Aeterna before the biggest hit (an Asura, a Meteor, a Spiral Pierce) doubles it;
it is used up by the first hit, so time it before multi-hit spells, not after.
Kyrie on whoever the boss is on; Safety Wall under a melee target; Pneuma under
a ranged target. Basilica is useless against a boss. Magnus and Turn Undead
only on undead/demon bosses. Decrease AGI and Lex Divina do nothing to a boss.
**Gives the party:** most of the buffs table; SP sustain (Magnificat).
**Companion rotation:** yes (8, 4009), covering all of the above incl.
Assumptio and Basilica.

### Monk (15) / Champion (4016)

**Role:** single-target burst (Asura Strike), combo melee DPS, small AoE (Ki
Explosion). **Builds:** Asura (INT/STR/DEX, Fury + Asura from Spirit Spheres,
often with Sage/Priest SP support), combo (AGI/STR, Triple → Chain → Combo
Finish), Champion combo-Asura (`CH_*` chain ends in Asura without the cast).

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `MO_CALLSPIRITS` Summon Spirit Sphere | +1 sphere (max 5) | 8 | 1000 / – | – | – | |
| `MO_EXPLOSIONSPIRITS` Fury | +CRIT, enables Asura | 15 | – | – | – | 5 spheres |
| `MO_EXTREMITYFIST` Asura Strike | ATK × (8 + SP/10) + flat; **ignores DEF and FLEE**; sets SP to 0, no SP regen for 5 min | all SP | 2000 / 1000 | wpn | M | Fury on, 5 spheres (or in combo) |
| `MO_TRIPLEATTACK` Raging Trifecta Blow | passive 3-hit chance; opens combos | – | | wpn | M | |
| `MO_CHAINCOMBO` Raging Quadruple Blow | combo 2 | 15 | – | wpn | M | after Triple |
| `MO_COMBOFINISH` Raging Thrust | combo 3, 200+60×lv % splash | 15 | – | wpn | M | 1 sphere |
| `MO_INVESTIGATE` Occult Impaction | 75×lv %, **scales with target DEF**, ignores FLEE | 20 | 1000 / 500 | neutral | M | 1 sphere |
| `MO_FINGEROFFENSIVE` Throw Spirit Sphere | 1 hit per sphere, 9 cells | 10 | 1000 / 500 | wpn | R | spheres |
| `MO_BALKYOUNG` Ki Explosion | AoE stun around the target | 20 + 10 HP | – / 2000 | wpn | M | |
| `MO_STEELBODY` Mental Strength | DEF/MDEF 90, slow, no skills | 200 | 5000 / – | – | – | 5 spheres |
| `MO_BLADESTOP` Root | locks a melee attacker and self | 10 | – | – | – | 1 sphere |
| `MO_BODYRELOCATION` Snap | instant move 18 cells | 14 | – | – | – | 1 sphere (0 under Fury) |
| `MO_KITRANSLATION` / `MO_ABSORBSPIRITS` | give a sphere / eat spheres for SP (no SP from bosses) | 40 / 5 | | | | |
| `CH_PALMSTRIKE` Raging Palm Strike | combo hit, knockback | 10 | fixed | wpn | M | Fury |
| `CH_TIGERFIST` Glacier Fist | combo, root (not on bosses) | 12 | – | wpn | M | 1 sphere |
| `CH_CHAINCRUSH` Chain Crush Combo | combo, 400+100×lv % | 22 | – | wpn | M | 2 spheres |
| `CH_SOULCOLLECT` Zen | 5 spheres at once | 20 | 2000 / – | – | – | |

**Against bosses:** Asura ignores DEF and FLEE, so it is the best single hit a
party has against a high-DEF boss, and with Lex Aeterna it doubles. Its cost is
the whole SP bar and 5 minutes without SP regen; an Asura Monk needs SP brought
to them (Magnificat does not help during the lock; Aid Potion/Blue Potions do
[u]). Occult Impaction gets better the higher the boss's DEF. Melee: a boss's
Safety-Wall-type defences, its knockback and its AoE all hit the Monk. Combos
need the attack to keep landing; bosses with high FLEE punish combo builds.
**Gives the party:** nothing but damage (Ki Translation gives a sphere).
**Companion rotation:** yes (15, 4016), incl. combos and Asura.

---

## Mage line

Mage skills every Wizard and Sage has: bolts `MG_FIREBOLT` / `MG_COLDBOLT` /
`MG_LIGHTNINGBOLT` (10 hits, 30 SP, 7000 / 2800), `MG_SOULSTRIKE` (Ghost),
`MG_NAPALMBEAT`, `MG_FIREBALL`, `MG_FIREWALL` (blocks walkers by knocking them
back; a boss is knockback-immune and walks through, taking every hit), `MG_FROSTDIVER` (Freeze, resisted),
`MG_STONECURSE` (fails on bosses), `MG_THUNDERSTORM`, `MG_SAFETYWALL` (Blue
Gem), `MG_ENERGYCOAT` (SP absorbs damage), `MG_SIGHT`.

### Wizard (9) / High Wizard (4010)

**Role:** AoE damage and crowd control; the strongest pre-re magic single
target too (Jupitel, Earth Spike, bolts). **Builds:** INT/DEX AoE (Storm Gust,
Lord of Vermilion, Meteor Storm), Quagmire/utility; HW adds Mystical
Amplification and Gravitation.

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `WZ_STORMGUST` Storm Gust | 9×9 ground, 10 hits, Freeze chance (resisted) | 78 | 15000 / 5000 | Water | Mag | |
| `WZ_VERMILION` Lord of Vermilion | 9×9 ground, 10 hits, Blind | 96 | 10500 / 5000 | Wind | Mag | |
| `WZ_METEOR` Meteor Storm | 7 cells, falling meteors, Stun | 64 | 15000 / 7000 | Fire | Mag | |
| `WZ_JUPITEL` Jupitel Thunder | single, 12 hits, knockback | 47 | 7000 / – | Wind | Mag | |
| `WZ_EARTHSPIKE` Earth Spike | single, 5 hits | 20 | 3500 / 1800 | Earth | Mag | |
| `WZ_HEAVENDRIVE` Heaven's Drive | 5×5 ground, 5 hits | 44 | 5000 / 1000 | Earth | Mag | |
| `WZ_FIREPILLAR` Fire Pillar | trap-like pillar, 12 hits, **ignores MDEF** | 75 | 300 / 1000 | Fire | Mag | Blue Gem at L6+ |
| `WZ_FROSTNOVA` Frost Nova | Freeze around self | 27 | 4000 / 1000 | Water | Mag | |
| `WZ_WATERBALL` Water Ball | hits by water cells around | 25 | 5000 / – | Water | Mag | water/Deluge cells |
| `WZ_QUAGMIRE` Quagmire | 5×5, AGI/DEX −50, ends speed buffs, **works on bosses** | 25 | – / 1000 | – | – | |
| `WZ_ICEWALL` Ice Wall | wall of ice | 20 | – | – | – | makes MVPs teleport |
| `WZ_SIGHTRASHER`, `WZ_SIGHTBLASTER` | AoE fire around self / reactive shield | 53 / 40 | | Fire | Mag | Sight on |
| `WZ_ESTIMATION` Sense | shows a monster's stats | 10 | | | | |
| `HW_MAGICPOWER` Mystical Amplification | +50 % MATK for the next spell | 50 | 700 fixed / – | – | – | |
| `HW_NAPALMVULCAN` Napalm Vulcan | 5 Ghost hits, splash, Curse | 70 | 1000 / 1000 | Ghost | Mag | |
| `HW_GRAVITATION` Gravitation Field | 5×5 fixed damage over 9 s, ignores FLEE/element; caster stands still | 100 | 5000 / 9000 | – | R (misc) | Blue Gem |
| `HW_GANBANTEIN` Ganbantein | removes ground effects (e.g. a boss's Land Protector) | 40 | 3000 / 5000 | – | – | Yellow + Blue Gem |
| `HW_MAGICCRASHER` Stave Crasher | MATK as physical hit | 8 | 300 / 300 | wpn | R | |
| `HW_SOULDRAIN` Soul Drain | passive: SP per kill by spell | – | | | | |

**Against bosses:** magic never misses and ignores Pneuma/Safety Wall, so a
Wizard deals reliable damage to any boss; elements matter (Water vs Fire
bosses, Wind vs Water, Earth vs Wind, Fire vs Earth/Undead). Storm Gust and LoV
keep hitting a boss (no knockback to break the stack) and clear its slaves.
Freeze/Stun/Blind effects do nothing to the boss itself. Quagmire is the one
debuff that lands on bosses. Fire Pillar ignores MDEF (good against high-MDEF
bosses such as Dark Lord/Pharaoh). Long casts are the weakness: they need
Suffragium, Bragi and protection, and SP runs dry (Magnificat). Mystical
Amplification + Lex Aeterna before a Jupitel or Storm Gust is the pre-re burst.
**Gives the party:** Quagmire, Safety Wall, Ice Wall (careful), slave clearing.
**Companion rotation:** yes (9, 4010).

### Sage (16) / Professor (4017)

**Role:** utility caster: Dispel, Land Protector, endows, Magic Rod/Spell
Breaker vs casters, Hindsight autocast battle-sage; Professor adds SP transfer
(Soul Exhale), Fiber Lock, Double Casting, Mind Breaker. **Builds:** support
sage (endows, LP, Dispel), Hindsight battle sage (STR/AGI book), magic-damage
sage/Double-Cast Professor.

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `SA_DISPELL` Dispell | removes buffs (Power Up, Assumptio, etc.); 50+10×lv %; **works on bosses** | 1 | 2000 / – | – | – | Yellow Gemstone |
| `SA_LANDPROTECTOR` Magnetic Earth | 7×7+ zone where no ground spell can be placed (both sides) | 50 | 5000 / – | – | – | Blue + Yellow Gem |
| `SA_FLAMELAUNCHER` / `SA_FROSTWEAPON` / `SA_LIGHTNINGLOADER` / `SA_SEISMICWEAPON` | endow fire / water / wind / earth | 40 | 3000 / – | – | – | Red Blood / Crystal Blue / Wind of Verdure / Green Live |
| `SA_VOLCANO` / `SA_DELUGE` / `SA_VIOLENTGALE` | ground buff zones | 40 | 5000 / – | – | – | Yellow Gem |
| `SA_AUTOSPELL` Hindsight | auto-cast bolts / Soul Strike / Heaven's Drive on melee | 35 | 3000 / – | – | – | |
| `SA_MAGICROD` Magic Rod | absorbs one targeted spell into SP | 2 | – | – | – | |
| `SA_SPELLBREAKER` Spell Breaker | breaks a cast, steals SP; 10 % on bosses | 10 | 700 / – | – | – | |
| `SA_CASTCANCEL`, `SA_FREECAST` | cancel / walk while casting | 2 | | | | |
| `SA_ABRACADABRA` Hocus-pocus | random skill | 50 | | | | 2 Yellow Gem |
| `SA_ELEMENTWATER`... Elemental Change | change a monster's element (**fails on bosses**) | 30 | 2000 / 1000 | | | elemental stone |
| `WZ_EARTHSPIKE`, `WZ_HEAVENDRIVE` | earth spells (from the tree) | 20 / 44 | | Earth | Mag | |
| `PF_SOULCHANGE` Soul Exhale | swap/give SP with a party member | 5 | 3000 / 5000 | – | – | |
| `PF_HPCONVERSION` Indulge | HP → SP | 5 | – / 1800 | | | |
| `PF_SPIDERWEB` Fiber Lock | pins target, FLEE −50 %, fire ×2 (**works on bosses**) | 50 | – | – | – | Cobweb |
| `PF_FOGWALL` Blinding Mist | ranged hits miss more inside; blind (bosses resist) | 25 | – | – | – | |
| `PF_DOUBLECASTING` Double Casting | bolts fire twice (chance) | 60 | 2000 fixed | – | – | |
| `PF_MEMORIZE` Foresight | next 5 casts at ⅓ cast time | 1 | 5000 fixed | | | |
| `PF_MINDBREAKER` Mind Breaker | +MATK, −MDEF (**fails on bosses**) | 24 | – / 1200 | | | |
| `PF_SOULBURN` Soul Siphon | drains target SP; damage on monsters [u] | 120 | – / cd 15000 | – | Mag | |

**Against bosses:** Dispel is the reason to bring a Sage: it strips a boss's
Power Up / Agi Up / Assumptio and makes it drop its target (Kyrie cannot be put on a monster at all [rA]). Land
Protector stops a boss's ground spells (and the party's). Endows turn the
party's weapons to the boss's weakness (Fire endow vs Earth bosses, etc.). Fiber
Lock pins a boss and halves its FLEE (good for melee who miss). Magic Rod eats a
boss's targeted spells. Mind Breaker and Elemental Change fail on bosses.
Volcano/Deluge/Whirlwind are cheap party buffs on a stationary fight.
**Gives the party:** endows, ground zones, Dispel, SP (Professor).
**Companion rotation:** yes (16, 4017). **`SA_SPELLBREAKER` and
`PF_SOULCHANGE`, `PF_HPCONVERSION`, `PF_MEMORIZE` are not in it.**

---

## Archer line

Archer skills: `AC_DOUBLE` Double Strafe (2 hits, 12 SP, bow, 1 arrow, R),
`AC_SHOWER` Arrow Shower (AoE, R), `AC_CHARGEARROW` Arrow Repel (knockback),
`AC_CONCENTRATION` Improve Concentration (+AGI/DEX, reveals hidden), passive
`AC_VULTURE` (+range). Arrows set the element: pick the arrow against the boss.

### Hunter (11) / Sniper (4012)

**Role:** ranged single-target and trap control; falcon damage that ignores
FLEE and DEF. **Builds:** Double Strafe AGI/DEX, Blitz Beat (INT/DEX/LUK auto
Blitz), trapper (Claymore/Blast Mine). Sniper: Falcon Assault, Sharp Shooting,
Falcon Eyes, Wind Walker.

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `HT_BLITZBEAT` Blitz Beat | falcon, 5 hits, splash; misc damage (INT/DEX), ignores FLEE/DEF | 22 | 1500 / 1000 | neutral | R | falcon |
| `HT_ANKLESNARE` Ankle Snare | traps; holds a boss for 1/5 of the time in pre-re | 12 | – | – | – | 1 Trap |
| `HT_CLAYMORETRAP` Claymore Trap | 5×5 fire, ignores FLEE | 15 | – | Fire | M (trap) | 2 Traps |
| `HT_BLASTMINE` Blast Mine | 3×3 wind, ignores FLEE | 10 | – | Wind | M (trap) | 1 Trap |
| `HT_LANDMINE` Land Mine | earth + Stun | 10 | – | Earth | M (trap) | 1 Trap |
| `HT_FREEZINGTRAP` / `HT_SANDMAN` / `HT_FLASHER` | Freeze / Sleep / Blind (all resisted by bosses) | 10-12 | | | | 1 Trap |
| `HT_SKIDTRAP` Skid Trap | slides the target (not a boss: knockback-immune) | 10 | | | | 1 Trap |
| `HT_SHOCKWAVE` Shockwave Trap | drains SP | 45 | | | | 2 Traps |
| `HT_DETECTING` Detect | reveals hidden | 8 | | | | falcon |
| `HT_SPRINGTRAP` / `HT_REMOVETRAP` | remove traps | | | | | |
| `HT_POWER` Beast Strafing | 2 hits on brute/insect after Double Strafe | 12 | | wpn | R | Hunter spirit, bow |
| `SN_SHARPSHOOTING` Focused Arrow Strike | line pierce, can crit | 30 | 2000 / 1500 | wpn | R | bow, arrow |
| `SN_FALCONASSAULT` Falcon Assault | big single falcon hit, ignores FLEE | 46 | 1000 / 3000 | neutral | R | falcon |
| `SN_SIGHT` Falcon Eyes | +stats, +ATK %, +CRIT, +HIT | 40 | – | | | |
| `SN_WINDWALK` Wind Walker | party move speed + FLEE | 100 | 5600 / 2000 | | | |

**Against bosses:** steady ranged damage from outside the boss's melee and
AoE; Blitz Beat/Falcon Assault ignore FLEE and DEF. Traps: damage traps ignore
FLEE and are melee-class (a boss's Pneuma does not stop them); Ankle Snare buys
a short hold; status traps fail. A Pneuma-casting boss blocks arrows. Detect
uncovers hiding slaves.
**Gives the party:** Wind Walker (Sniper), Improve Concentration (self only).
**Companion rotation:** yes (11, 4012).

### Bard (19) / Clown (4020) and Dancer (20) / Gypsy (4021)

**Role:** party support through songs (one song at a time, area around the
performer, the performer is slowed and does not get its own song), ensembles
when a Bard and a Dancer stand together; Arrow Vulcan damage on trans.
**Builds:** support (DEX/INT/VIT, Bragi for casters, Assassin Cross for melee),
Arrow Vulcan Clown/Gypsy (DEX/AGI/LUK).

| Skill | Who | Does | SP | Note |
|---|---|---|---|---|
| `BA_POEMBRAGI` Magic Strings | Bard | −cast time, −after-cast delay | 85 | the caster song |
| `BA_ASSASSINCROSS` Impressive Riff | Bard | +ASPD | 65 | the melee song |
| `BA_WHISTLE` Perfect Tablature | Bard | +FLEE, +perfect dodge | 60 | |
| `BA_APPLEIDUN` Song of Lutie | Bard | +MaxHP %, heal over time | 85 | |
| `BA_DISSONANCE` Unchained Serenade | Bard | damage around, ignores FLEE | 30 | |
| `BA_FROSTJOKER` Unbarring Octave | Bard | Freeze chance on **everyone** on screen | 20 | hits the party too |
| `BA_MUSICALSTRIKE` Melody Strike | Bard | ranged hit | 9 | instrument + arrow |
| `DC_HUMMING` Focus Ballet | Dancer | +HIT | 40 | |
| `DC_FORTUNEKISS` Lady Luck | Dancer | +CRIT (10×lv) [rA] | 70 | |
| `DC_SERVICEFORYOU` Gypsy's Kiss | Dancer | +MaxSP %, −SP cost | 85 | |
| `DC_DONTFORGETME` Slow Grace | Dancer | enemies: −ASPD, slower (**not BossResist**) | 55 | |
| `DC_UGLYDANCE` Hip Shaker | Dancer | drains enemies' SP | 35 | |
| `DC_SCREAM` Dazzler | Dancer | Stun on screen (party too) | 20 | |
| `DC_THROWARROW` Slinging Arrow | Dancer | ranged hit | 9 | whip + arrow |
| `BD_DRUMBATTLEFIELD` Battle Theme | ensemble | +ATK, +DEF | 60 | |
| `BD_RINGNIBELUNGEN` Harmonic Lick | ensemble | +damage with level-4 weapons [u] | 50 | |
| `BD_ETERNALCHAOS` Down Tempo | ensemble | enemies' soft DEF = 0 (**not BossResist**) [rA] | 30 | |
| `BD_SIEGFRIED` Acoustic Rhythm | ensemble | +elemental and status resistance | 20 | |
| `BD_INTOABYSS` Power Chord | ensemble | skills need no gemstones | 10 | |
| `BD_LULLABY` / `BD_ROKISWEIL` | ensemble | Sleep / no skills for anyone (bosses resist both) | | |
| `BD_RICHMANKIM` Mental Sensing | ensemble | +EXP | | |
| `CG_ARROWVULCAN` Vulcan Arrow | trans | 9-hit ranged | 30 | 3800 / 3000 |
| `CG_MARIONETTE` Marionette Control | trans | give half the caster's stats to a party member | 100 | |
| `CG_LONGINGFREEDOM` Longing for Freedom | trans | move/attack during an ensemble | 15 | |
| `CG_MOONLIT` Sheltering Bliss | trans | nobody can enter the area | 70 | |
| `CG_HERMODE` Wand of Hermode | trans | removes allies' buffs, blocks magic targeting | 60 | |
| `CG_TAROTCARD` Tarot Card of Fate | trans | random card (works on bosses; may teleport it away) | 40 | 1000 / 3000 |

All songs and ensembles need an instrument (Bard) or whip (Dancer); the Bard
and Dancer spirit lets one performer get its own song and play the partner's
solo (`pc.cpp`, linked skills) [rA].
**Against bosses:** Bragi is the single biggest boost to a caster party (more
Storm Gusts per minute, faster heals); Assassin Cross for melee parties; Down
Tempo on a high-VIT boss; Slow Grace slows a boss's attacks. Dazzler and Frost
Joker hit the party. Hermode strips the party's buffs: never near the party.
Tarot can send the boss away.
**Companion rotation:** yes (19, 20, 4020, 4021), incl. every song,
ensembles, Marionette, Hermode.

---

## Merchant line

Merchant skills: `MC_MAMMONITE` (zeny per hit, M), `MC_CARTREVOLUTION`
(cart AoE, M), `MC_LOUD` (+4 STR).

### Blacksmith (10) / Whitesmith (4011)

**Role:** melee damage and party ASPD/ATK buffs. **Builds:** axe/mace
battlesmith (Adrenaline, Power-Thrust, Maximize Power); Whitesmith Cart
Termination (cart-weight, Cart Boost) and Meltdown.

| Skill | Does | SP | Cast / ACD | Rng | Needs |
|---|---|---|---|---|---|
| `BS_ADRENALINE` Adrenaline Rush | +ASPD, party (axe/mace) | 32 | – | – | axe/mace; Quagmire/Decrease AGI end it |
| `BS_ADRENALINE2` Full Adrenaline Rush | Adrenaline for any weapon | 64 | – | – | Blacksmith spirit |
| `BS_OVERTHRUST` Power-Thrust | +ATK %, party smaller share; weapon break risk | 10 | – | – | |
| `BS_WEAPONPERFECT` Weapon Perfection | no size penalty, party | 10 | – | – | |
| `BS_MAXIMIZE` Maximize Power | max weapon damage, drains SP | 10 | – | – | |
| `BS_HAMMERFALL` Hammer Fall | AoE Stun (bosses resist) | 10 | – | M | |
| `WS_CARTTERMINATION` Cart Termination | huge hit scaled by cart weight, Stun | 15 + 1500 z | – | M | Cart Boost on |
| `WS_MELTDOWN` Shattering Strike | chance to break weapon/armour on hit | 90 | 1000 / – | – | |
| `WS_OVERTHRUSTMAX` Maximum Power-Thrust | +ATK %, self | 15 + 5000 z | – | – | |
| `WS_CARTBOOST` Cart Boost | move speed | 20 | – | – | cart |

**Against bosses:** Adrenaline and Weapon Perfection raise the whole melee
party's damage; Cart Termination is one of the hardest single physical hits in
pre-re, melee-class. Hammer Fall's stun does nothing to a boss.
**Companion rotation:** yes (10, 4011).

### Alchemist (18) / Creator (4019)

**Role:** Acid Demonstration (Acid Bomb) Creator is a top boss killer: misc
damage from the target's VIT, ignores FLEE; Chemical Protection for the tank;
Aid Potion/Condensed Potion heals; homunculus. **Builds:** Acid Bomb Creator
(INT/VIT/DEX), battle alchemist (axe), farm/brew.

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `CR_ACIDDEMONSTRATION` Acid Demonstration | 10 hits, from target VIT and caster INT; ignores FLEE; breaks weapon/armour chance | 30 | 1000 / 1000 | neutral | R (misc) | 1 Bottle Grenade + 1 Acid Bottle |
| `AM_ACIDTERROR` Acid Terror | ignores FLEE and DEF, armour break, Bleeding | 15 | 1000 / – | neutral | R | Acid Bottle |
| `AM_DEMONSTRATION` Bomb | fire ground DoT, weapon break | 10 | 1000 / – | Fire | ground | Bottle Grenade |
| `AM_POTIONPITCHER` Aid Potion | throws a potion at a member (Blue Potion = SP) | 1 | – / 500 | – | – | the potion |
| `CR_SLIMPITCHER` Aid Condensed Potion | AoE potion heal | 30 | 1000 / 1000 | – | – | Slim potions |
| `AM_CP_WEAPON` / `_SHIELD` / `_ARMOR` / `_HELM`, `CR_FULLPROTECTION` | Chemical Protection | 25-40 | 2000 / – | – | – | Glistening Coat |
| `AM_CANNIBALIZE`, `AM_SPHEREMINE` | summon plants / marine spheres | 20 / 10 | | | | bottles |
| `AM_BERSERKPITCHER` | Berserk Potion on another | 10 | | | | 2 Berserk Potion |
| `AM_CALLHOMUN` etc. | homunculus | | | | | Embryo |

**Against bosses:** Acid Demonstration does not care about FLEE and grows with
the boss's VIT, so high-VIT MVPs melt; Pneuma blocks it (ranged misc).
Aid Potion with Blue Potions feeds an Asura Monk's SP. Chemical Protection keeps
the tank's gear from a boss's Armor Break / strip skills.
**Companion rotation:** yes (18, 4019).

---

## Thief line

Thief skills: `TF_DOUBLE` (passive double attack with daggers), `TF_MISS`
(FLEE), `TF_STEAL`, `TF_HIDING` (useless against a Detector boss),
`TF_POISON` (Poison, resisted), `TF_DETOXIFY`, `TF_SPRINKLESAND`,
`TF_BACKSLIDING`, `TF_THROWSTONE`.

### Assassin (12) / Assassin Cross (4013)

**Role:** single-target melee DPS. **Builds:** katar crit (LUK/AGI, crits ignore
FLEE and DEF in pre-re [rA]), Sonic Blow (STR/AGI), dual-dagger/sword; Assassin
Cross: EDP + Soul Destroyer / Meteor Assault, Sonic Blow EDP.

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `AS_SONICBLOW` Sonic Blow | 8 hits, 400+50×lv % total, Stun | 34 | – / 2000 | wpn | M | katar |
| `AS_GRIMTOOTH` Grimtooth | AoE from hiding | 3 | – | wpn | R | katar, Hiding |
| `AS_ENCHANTPOISON` Enchant Poison | Poison weapon | 20 | – | – | – | |
| `AS_POISONREACT` Poison React | counter poison attackers | 45 | – | | | |
| `AS_VENOMDUST` Venom Dust | poison ground (bosses resist poison) | 20 | – | – | – | Red Gemstone |
| `AS_SPLASHER` Venom Splasher | delayed burst (**fails on bosses**) | 30 | 1000 / cd 12000 | | | Red Gemstone |
| `AS_VENOMKNIFE` Throw Venom Knife | ranged poison | 15 | – | | R | Venom Knife |
| `AS_CLOAKING` Cloaking | invisible (not to bosses) | 15 | | | | |
| `ASC_EDP` Enchant Deadly Poison | ×4ish weapon damage for 60 s [u on multiplier] | 100 | – / 2000 | Poison | – | Poison Bottle |
| `ASC_BREAKER` Soul Destroyer | ranged ATK+MATK hit | 30 | 700 / 2800 | wpn | R | |
| `ASC_METEORASSAULT` Meteor Assault | AoE around self, stun/blind/bleed | 28 | 500 / 500 | wpn | M | |
| `ASC_CDP` Create Deadly Poison | makes Poison Bottles | 50 | | | | |

**Against bosses:** crit katar Assassins ignore the boss's FLEE and DEF; EDP
is the classic MVP damage burst. Sonic Blow is melee (Safety Wall-style
defences and boss AoE). Hiding/Cloaking do not hide from a boss. Venom Splasher
and every poison status fail. Soul Destroyer is ranged (blocked by a monster's
Pneuma).
**Companion rotation:** yes (12, 4013).

### Rogue (17) / Stalker (4018)

**Role:** utility melee/bow hybrid: strips (PvP and non-boss), Plagiarism copies
a skill, Back Stab, bow Double Strafe; Stalker adds Full Strip, Preserve, Counter
Instinct. **Builds:** Back Stab, bow/Double Strafe Rogue, Plagiarism (e.g. a
copied Storm Gust / Bowling Bash) [u], strip-support.

| Skill | Does | SP | Cast / ACD | Rng | Needs |
|---|---|---|---|---|---|
| `RG_BACKSTAP` Back Stab | 200+40×lv %, ignores FLEE | 16 | – / 500 | M | (from behind/hiding) |
| `RG_RAID` Sightless Mind | AoE from hiding, Stun/Blind | 20 | – | M | Hiding |
| `RG_INTIMIDATE` Snatch | hit + teleport both; **no teleport on bosses** [rA, `skill.cpp`] | 25 | – | M | |
| `RG_STRIPWEAPON` / `SHIELD` / `ARMOR` / `HELM` | strip (**bosses resist**) | 20-25 | 1000 / 1000 | M | |
| `ST_FULLSTRIP` Divest All | all four (**bosses resist**) | 30 | – / 1000 | M | |
| `RG_CLOSECONFINE` Close Confine | lock self + target (bosses resist) | 25 | | M | |
| `RG_STEALCOIN` Mug | steal zeny (not from status-immune) | 15 | | M | |
| `AC_DOUBLE` Double Strafe | from the Rogue tree | 12 | | R | bow |
| `RG_PLAGIARISM` Intimidate (passive) | keeps the last skill used on the Rogue | – | | | |
| `ST_REJECTSWORD` Counter Instinct | reflect/halve sword/dagger/axe melee | 30 | | | |
| `ST_PRESERVE` Preserve | keep the copied skill | 30 | | | |
| `ST_CHASEWALK` Stealth | | 10 | | | |

**Against bosses:** little special; Back Stab ignores FLEE; strips fail. The
Rogue spirit makes strip durations ×10 and the Rogue immune to Dispel [rA].
**Companion rotation:** yes (17, 4018).

---

## Expanded jobs

### Super Novice (23)

Learns nearly every first-job skill (Swordsman, Mage, Archer's Improve
Concentration, Acolyte incl. Heal/Blessing/Inc AGI, Merchant, Thief); low HP/SP.
**Role:** a flexible weak support/caster or melee; a "poor man's" Priest
buffer. With the Super Novice spirit at 90+/96+ it can wear any helm and level-4
weapons [rA]. Against bosses: Blessing/Inc AGI/Heal and bolts; Decrease AGI,
Stone Curse, Provoke fail.
**Companion rotation:** only in the strategy-needs worktree (23, plus 4190 for
the renewal-id Super Novice): Heal/Blessing/Inc AGI, bolts, Safety Wall, Bash,
Magnum Break. In main, see the note at the end.

### Gunslinger (24)

**Role:** ranged physical DPS with gun type choosing the role. **Builds:**
Desperado (Revolver, AoE around self), Tracking/Rifle (single target), Full
Buster/Spread Attack (Shotgun), Gatling Fever (Gatling), Ground Drift
(Grenade). Coins come from `GS_GLITTERING` (Flip the Coin).

| Skill | Does | SP | Cast / ACD | Rng | Needs |
|---|---|---|---|---|---|
| `GS_DESPERADO` Desperado | random hits on everything within 3 cells, 100+50×(lv−1) % each | 50 | – / 1000 | **M** (range 0) | **Revolver**, 10 Bullets |
| `GS_TRACKING` Tracking | big single hit, 100×(lv+1) % extra | 60 | 3000 fixed | R | Revolver/Rifle, 1 Bullet |
| `GS_RAPIDSHOWER` Rapid Shower | 5 hits | 40 | – / 1000 | R | Revolver, 5 Bullets |
| `GS_FULLBUSTER` Full Buster | big hit, self-blind chance | 65 | – / 3000 | R | Shotgun, 10 Bullets |
| `GS_SPREADATTACK` Spread Attack | AoE around the target | 60 | – | R | Shotgun, 5 Bullets |
| `GS_GATLINGFEVER` Gatling Fever | +ASPD, +ATK, slow | 48 | – | – | Gatling |
| `GS_GROUNDDRIFT` Ground Drift | grenade mines, ignore FLEE | 40 | 2000 / – | ground | Grenade Launcher, Grenade |
| `GS_PIERCINGSHOT` Piercing Shot | ignores DEF, Bleeding | 15 | 1500 / – | R | Revolver/Rifle |
| `GS_MADNESSCANCEL` Madness Canceller | +ATK, +ASPD, no flinch | 30 | 3000 / 4000 | – | 4 coins |
| `GS_ADJUSTMENT` Adjustment | +FLEE, −HIT, less ranged damage taken | 15 | 1000 / 1000 | – | 2 coins |
| `GS_INCREASING` Increasing Accuracy | +HIT, +DEX/AGI | 30 | – / 1000 | – | 4 coins |
| `GS_FLING` Fling | target DEF/VIT DEF −5 %/coin (**works on bosses**) | 10 | – | R | coins |
| `GS_MAGICALBULLET` Magical Bullet | Ghost hit from MATK | 7 | – | R | 1 coin |
| `GS_TRIPLEACTION` / `GS_CRACKER` / `GS_BULLSEYE` | 3 hits / stun / ×5 on brute-demihuman non-boss | | | R | 1 coin |
| `GS_DISARM` Disarm | strip weapon (bosses resist) | 35 | | R | Revolver/Rifle |
| `GS_DUST` Dust | knockback shot | 30 | | M | Shotgun |

The bullet's element is the attack's element (Silver Bullet = Holy) [u].
**Against bosses:** Tracking/Piercing Shot for single target; Desperado
around a boss also clears slaves but puts the Gunslinger in melee. Fling
lowers a boss's DEF. Bull's Eye's bonus never applies to bosses.
**Companion rotation:** strategy-needs worktree only (24): every skill above.

### Ninja (25)

**Role:** hybrid: ninjutsu magic (Fire/Water/Wind) or throwing physical (Huuma,
Shuriken, Kunai), Final Strike burst. **Builds:** magic Ninja (INT/DEX),
Huuma/Throwing Ninja, Final Strike (HP-based).

| Skill | Does | SP | Cast / ACD | Ele | Rng | Needs |
|---|---|---|---|---|---|---|
| `NJ_KOUENKA` Crimson Fire Petal | bolt-like | 36 | 7000 / – | Fire | Mag | |
| `NJ_HYOUSENSOU` Spear of Ice | bolt-like | 42 | 7000 / – | Water | Mag | |
| `NJ_HUUJIN` Wind Blade | multi-hit | 30 | 5500 / 1000 | Wind | Mag | |
| `NJ_BAKUENRYU` Raging Fire Dragon | AoE | 40 | 3000 / 2000 | Fire | Mag | Flame Stone |
| `NJ_KAENSIN` Crimson Fire Formation | fire ground | 25 | 1500 / 1000 | Fire | Mag | Flame Stone |
| `NJ_HYOUSYOURAKU` Ice Meteor | AoE, Freeze | 60 | 4000 / 2000 | Water | Mag | Ice Stone |
| `NJ_SUITON` Hidden Water | water ground (enables water spells) | 42 | 3000 / – | Water | – | Ice Stone |
| `NJ_RAIGEKISAI` Lightning Strike | AoE around self | 32 | 4000 / – | Wind | Mag | Wind Stone |
| `NJ_KAMAITACHI` Kamaitachi | line | 40 | 4000 / – | Wind | Mag | Wind Stone |
| `NJ_HUUMA` Throw Huuma Shuriken | AoE throw | 40 | 3000 / 2000 | wpn | R | Huuma |
| `NJ_SYURIKEN` / `NJ_KUNAI` | throws | 2 / 10 | | wpn | R | shuriken / kunai |
| `NJ_ZENYNAGE` Throw Zeny | zeny damage (÷3 on bosses) | 50 | – / 5000 | – | R | zeny |
| `NJ_ISSEN` Final Strike | damage from current HP, ignores FLEE, leaves 1 HP | 100 | – | – | R | |
| `NJ_KASUMIKIRI` / `NJ_KIRIKAGE` / `NJ_SHADOWJUMP` | hide-slash / leap | | | | M | |
| `NJ_UTSUSEMI` Cicada Skin Shedding | dodge hits by sliding | 24 | | | | |
| `NJ_BUNSINJYUTSU` Mirror Image | absorbs hits | 48 | | | | Shadow Orb |
| `NJ_NEN` Soul | +STR/+INT | 60 | 1000 / – | | | |
| `NJ_TATAMIGAESHI` Improvised Defense | wall that knocks back | 15 | | | | |

**Against bosses:** magic Ninja = an element-picking caster with shorter casts
than a Wizard's AoE; Final Strike is a one-shot burst that leaves the Ninja at 1
HP (pair with a healer). Throw Zeny is weak on bosses.
**Companion rotation:** strategy-needs worktree only (25).

### Taekwon (4046)

**Role:** melee kicker, mostly a stepping stone to Star Gladiator / Soul
Linker. Stances ready a kick that fires on the next normal attack.

| Skill | Does | SP | Rng |
|---|---|---|---|
| `TK_READYSTORM` → `TK_STORMKICK` | AoE kick | 1 / 2 | M |
| `TK_READYDOWN` → `TK_DOWNKICK` | Heel Drop, Stun | 1 / 2 | M |
| `TK_READYTURN` → `TK_TURNKICK` | Roundhouse, knockback around | 1 / 2 | M |
| `TK_READYCOUNTER` → `TK_COUNTER` | counter kick, ignores FLEE | 1 / 2 | M |
| `TK_JUMPKICK` Flying Kick | gap closer | 10 | R (range 9) |
| `TK_SEVENWIND` Mild Wind | weapon element (Holy at L7 etc.) | 50 | – |
| `TK_RUN` Running | sprint; Spurt (+STR) after | 10 | – |
| `TK_POWER` Kihop | passive +ATK with party members [u] | – | |

**Companion rotation:** strategy-needs worktree only (4046): stances + kicks.

### Star Gladiator (4047, flying 4048)

**Role:** melee DPS that is strong only on its chosen maps and against its
chosen monsters. **Mechanics [rA]:** `SG_FEEL` binds a map to Sun/Moon/Star;
`SG_HATE` binds a monster **ID** permanently: Sun = small, Moon = medium (Max HP
≥ 6000), Star = large (Max HP ≥ 20000) (`pc_set_hate_mob`). Against a hated
monster the Anger passive adds (BaseLv + DEX + LUK [+ STR for Star]) % damage
(`battle.cpp`). So a Star Gladiator who has hated a specific large boss is a
real boss killer against **that** boss only.

| Skill | Does | SP |
|---|---|---|
| `SG_SUN_WARM` / `SG_MOON_WARM` / `SG_STAR_WARM` | aura around self that hits/pushes, on the felt map | 20 / 20 / 10 |
| `SG_SUN_COMFORT` / `SG_MOON_COMFORT` / `SG_STAR_COMFORT` | +DEF / +FLEE / +ASPD on the felt map | 40 |
| `SG_FUSION` Union | every hit lands; with Soul Linker's Star spirit | 100 |
| TK kicks | as Taekwon | |

**Companion rotation:** strategy-needs worktree only (4047, 4048): the Taekwon
kicks; no `SG_*` skill (they need a felt map or a hated monster).

### Soul Linker (4049)

**Role:** support: casts a **spirit** on one class that unlocks that class's
hidden bonus; Ka- buffs; Es- spells. **Builds:** support linker, Esma caster.

Spirits, as the fork implements them [rA]:

| Spirit | Target | Effect |
|---|---|---|
| `SL_KNIGHT` | Knight | One-Hand Quicken |
| `SL_CRUSADER` | Crusader | Shield Boomerang always hits, ×2 damage, half delay |
| `SL_ASSASIN` | Assassin | Sonic Blow +100 % (25 % in WoE), half delay |
| `SL_ROGUE` | Rogue | strip duration ×10, immune to Dispel |
| `SL_MONK` | Monk | combo skills cost 2 SP |
| `SL_PRIEST` | Priest | Holy Light ×5 damage, ×5 SP |
| `SL_WIZARD` | Wizard | gemstones not used up (except Ganbantein) |
| `SL_SAGE` | Sage | Hindsight always casts, bolts at L10 |
| `SL_HUNTER` | Hunter | Beast Bane adds STR; Beast Strafing |
| `SL_BARDDANCER` | Bard/Dancer | own song affects self; partner's songs solo |
| `SL_BLACKSMITH` | Blacksmith | Full Adrenaline Rush |
| `SL_ALCHEMIST` | Alchemist | Aid Potion heals + base level |
| `SL_STAR` | Star Gladiator | Union without the SP cost [u: SP detail] |
| `SL_SUPERNOVICE` | Super Novice | any helm (90+), level-4 weapons (96+) |
| `SL_HIGH` | transcendent first jobs | stat bonus |
| `SL_SOULLINKER` | Soul Linker | Ka- skills usable on others |

| Skill | Does | SP | Cast / ACD | Ele | Rng |
|---|---|---|---|---|---|
| `SL_KAIZEL` Kaizel | revive on death | 60 | 1500 fixed | – | – |
| `SL_KAAHI` Kaahi | heals on each hit taken, costs SP | 30 | – / 500 | – | – |
| `SL_KAUPE` Kaupe | dodges hits (chance) | 40 | 500 / 500 | – | – |
| `SL_KAITE` Kaite | reflects magic | 70 | 3000 / – | – | – |
| `SL_STIN` Estin / `SL_STUN` Estun | small spells; open Esma | 30 | 100 / 500 | Endowed | Mag |
| `SL_SMA` Esma | 10-hit spell after Estin/Estun | 80 | 2000 / 500 | Endowed | Mag |
| `SL_SKE` Eske | target ATK +300 %, DEF ½ | 15 | 1000 / 500 | – | – |
| `SL_SKA` Eska | target MDEF 90, VIT DEF 90 (makes it tankier) | 60 | | | |
| `SL_SWOO` Eswoo | target slowed (÷5 on bosses) | 15 | | | |

Soul Linkers cannot be Dispelled [rA, `dispell.cpp`].
**Against bosses:** the Assassin and Crusader links are big damage boosts; the
Wizard link saves gemstones; Kaizel is a free revive on the tank. Eske on a boss
raises its damage too.
**Companion rotation:** strategy-needs worktree only (4049): its own spirit and
the Ka- buffs on itself, Estin/Estun/Esma. **It never links another member**:
only a plan can cast `SL_*` spirits on allies.

---

## A party for a boss

General guidance, not boss-specific (5–6 members):

| Seat | Why | Typical jobs |
|---|---|---|
| **Healer** | the party dies without Heal, Kyrie/Assumptio, Status Recovery and Resurrection; Lex Aeterna doubles the big hit | High Priest (one; two Priests' Kyrie and Assumptio cancel each other) |
| **SP sustain** | casters and Asura empty their SP in seconds against an MVP | Magnificat (Priest); Gypsy's Kiss; Soul Exhale (Professor); Aid Potion with Blue Potions (Alchemist) |
| **Tank / damage sink** | the boss needs a target that is not the healer | Paladin with Devotion + Defender, or a VIT Lord Knight; Safety Wall under them, Kyrie on them |
| **Utility vs buffs and FLEE** | bosses Power Up, Agi Up, Assumptio, cast Land Protector; some have high FLEE | Sage/Professor (Dispel, Land Protector, endows, Fiber Lock); Wizard's Quagmire |
| **Damage the boss cannot block** | bosses have high DEF/FLEE and some cast Pneuma or Safety Wall | magic (Wizard, Ninja, Esma); crits (katar Assassin Cross); FLEE/DEF-ignoring skills (Asura, Acid Demonstration, Martyr's Reckoning, Blitz/Falcon Assault); Lex Aeterna on top |
| **Slave/AoE clearing** | many MVPs summon slaves that kill the healer | Wizard (Storm Gust, LoV, Meteor), Bowling Bash Knight, Desperado |
| **Performer (optional)** | Bragi for casters, Assassin Cross for melee, Down Tempo vs high-VIT bosses | Clown/Gypsy |

Rules of thumb for plans:
- Status ailments are for the **slaves**, not the boss. On the boss use
  Quagmire, Lex Aeterna, Dispel, Fiber Lock, Vital Strike, Down Tempo, Slow
  Grace, Fling.
- Put the element on the weapon (Sage endow, Aspersio, arrows, Mild Wind) and
  on the armour (Benedictio) to match the boss.
- Melee-class attacks (incl. Desperado, Meteor Assault, traps) are blocked by
  a Safety Wall on the boss; ranged weapon and misc (Spiral Pierce, Acid
  Demonstration, arrows, Soul Destroyer) by Pneuma; magic by neither.
- Do not cast Ice Wall, Tarot, Hermode, Frost Joker or Dazzler near the
  party/boss.
- Pre-re casts fall with DEX: a 15-second Storm Gust is ~5 s at 100 DEX; Bragi
  and Suffragium make the difference.

---

## Companion skill rotations by job

`population_skill_db.yml` (population engine) gives each job a rotation the
engine casts on its own; a job without an entry only auto-attacks unless a plan
`Cast:`s for it. State checked on 2026-10-10:

| JobId | Job | `ragnarokoffline.app` (main) / this worktree | `ragnarokoffline.app-strategy-needs` |
|---|---|---|---|
| 7, 4008 | Knight, Lord Knight | yes | yes |
| 14, 4015 | Crusader, Paladin | yes (no `PA_GOSPEL`) | yes |
| 8, 4009 | Priest, High Priest | yes | yes |
| 15, 4016 | Monk, Champion | yes | yes |
| 9, 4010 | Wizard, High Wizard | yes | yes |
| 16, 4017 | Sage, Professor | yes (no Spell Breaker, Soul Exhale, Foresight) | yes |
| 11, 4012 | Hunter, Sniper | yes | yes |
| 19, 4020 / 20, 4021 | Bard, Clown / Dancer, Gypsy | yes | yes |
| 10, 4011 | Blacksmith, Whitesmith | yes | yes |
| 18, 4019 | Alchemist, Creator | yes | yes |
| 12, 4013 | Assassin, Assassin Cross | yes | yes |
| 17, 4018 | Rogue, Stalker | yes | yes |
| 23 / 4190 | Super Novice | **no** | yes (uncommitted) |
| 24 | Gunslinger | **no** | yes (uncommitted) |
| 25 | Ninja | **no** | yes (uncommitted) |
| 4046 | Taekwon | **no** | yes (uncommitted) |
| 4047, 4048 | Star Gladiator | **no** | yes (uncommitted), kicks only |
| 4049 | Soul Linker | **no** | yes (uncommitted), no links on others |
| 4001–4007 | High Novice … High Thief | **no** | yes (uncommitted) |
| 4211, 4212, 4215, 4218, 4239, 4240 | Kagerou, Oboro, Rebellion, Summoner, Star Emperor, Soul Reaper | **no** | yes (uncommitted) |

The strategy-needs entries are working-tree modifications of
`third-party/population-engine/files/db/population_skill_db.yml` in
`development/ragnarokoffline.app-strategy-needs` (branch
`core/population-engine-strategy-needs`), not committed.

**Fallback quirk [source].** A job with no entry falls back to
`population_engine_job_base_class()` → `get_base_job()` in
`population_engine.cpp`. Its first test is `job_id >= JOB_KNIGHT && job_id <=
JOB_ROYAL_GUARD`, i.e. 7..4066, which catches almost every job id (Wizard 9,
Gunslinger 24, Ninja 25, Taekwon 4046, Soul Linker 4049...) and returns
Swordsman. So a job with no entry gets the **Swordsman's** rows, filtered to
skills its own tree grants: nothing for Gunslinger/Ninja/Taekwon line, but a
Super Novice (who learns SM_BASH, SM_MAGNUM, SM_ENDURE, SM_PROVOKE) casts the
Swordsman's rotation. Harmless where every job has its own entry; wrong for any
that lacks one.

---

## Sources

- rAthena fork `development/rathena` @ `c8b69e407`: files named in each [rA]
  note. Range rule: `battle.cpp` `battle_range_type`, `skill.cpp`
  `skill_get_range2`, `conf/battle/skill.conf` (`skillrange_from_weapon: 0`,
  `skillrange_by_distance: 14`). Boss modes: `mob.cpp`
  `MobDatabase::loadingFinished`. Boss resist: `db/pre-re/status.yml` +
  `status.cpp` (`SCF_BOSSRESIST`). Crits: `battle.cpp` `is_attack_hitting`,
  `attack_ignores_def`. Kyrie/Magnificat/Assumptio values: `status.cpp`,
  `battle.cpp`.
- Population engine: `third-party/population-engine/files/db/population_skill_db.yml`
  and `src/map/population_engine.cpp` in both app checkouts.
- Roles, builds and playstyle: iRO Wiki Classic (https://irowiki.org/classic/)
  and RateMyServer pre-re (https://ratemyserver.net/), as summarised in
  [BUILDS.md](BUILDS.md) and [MVP_TACTICS.md](MVP_TACTICS.md); not re-fetched
  for this file.
