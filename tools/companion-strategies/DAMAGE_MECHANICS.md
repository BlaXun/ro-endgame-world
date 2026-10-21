# Pre-renewal damage mechanics (rAthena), for strategy writers

This file explains how damage works in the pre-renewal build, so that a plan can
choose a skill, target, element, card or armour for a reason. It is reference
material only, and nothing reads it.

**Ground truth.** Everything here comes from the rAthena fork beside this
checkout (`development/rathena`, branch `ragnarokoffline` @ `c8b69e407`). Its
`battle.cpp`, `status.cpp`, `skill.cpp`, `mob.cpp`, `db/` and `conf/battle/` do
not differ from `master`, the branch the app pins. Citations are written
`file:line` against that commit. Wiki pages ([irowiki classic][iro]) were used
only as a cross-check. Where a wiki and the source disagree, this file follows
the source and says so. **[unverified]** marks anything not traced in the
source.

Conventions used below:
- "Pre-re" means the code under `#ifndef RENEWAL`.
- "%" values are damage multipliers: 100 = unchanged.
- *Atk element* is the element of the hit. *Def element* is the target's element and level.

[iro]: https://irowiki.org/classic/Main_Page

---

## 0. Order of a physical hit (pre-re)

`battle_calc_weapon_attack`, `src/map/battle.cpp:5388-5797`:

1. **Lucky Dodge (perfect dodge)** is rolled first, and only for normal attacks
   and Sacrifice (`:5424`).
2. **Critical** is decided next. A critical hit always lands (`:3241`).
3. **HIT/FLEE roll** (`:3229-3317`).
4. **Base damage** (`battle_calc_base_damage`, `:2516-2625`). This is the weapon
   ATK roll, times the **size modifier** (players only, `:2581-2583`). The
   status ATK from STR (`batk`) is added *after* the size fix, so STR damage is
   never size-penalised.
5. × **skill ratio**, then + constant additions (`:5456-5460`).
6. × **ATK% buffs** (Provoke, Concentration, Power Up, Curse…), applied as a
   multiplier on top (`:4573-4575`, `battle_get_atkpercent` `:4356`).
7. **DEF**: first × (100 − hard DEF)%, then − soft (VIT) DEF (`:4721-4885`).
8. × **element table** (`:3646-3705`).
9. \+ flat mastery damage. This includes refine ATK, so it ignores both element and DEF.
10. × **attacker cards**, then × **target's reduction cards** (`:5739-5758`).
11. × **Lex Aeterna** and other end-of-hit modifiers (`battle_calc_damage`, `:1669`).
    This is also where Safety Wall, Pneuma, Kyrie and Assumptio act.

Magic (`battle_calc_magic_attack`, `:5802`) is shorter: a MATK roll, × skill
ratio, × MDEF, × element (`:6239`), × cards (`:6243`), then `battle_calc_damage`.
**Magic never checks HIT/FLEE** and never uses the size table.

---

## 1. Elements

### 1.1 The table: `db/pre-re/attr_fix.yml` (all 400 values)

In each table, rows are the **attack** element and columns are the **defender**
element. Values are damage %. A negative value would heal the target, but
`attribute_recover: no` (`conf/battle/battle.conf:75`) clamps it to **0**: for
magic at `battle.cpp:706-707`, and for physical hits through
`battle_min_damage` at `:3770-3771`.

Cross-check: iRO Wiki's classic table ([Element][el]) has the same values, but
its layout is transposed (defender down the side).

[el]: https://irowiki.org/classic/Element

**Defence level 1**

| Atk \ Def | Neut | Water | Earth | Fire | Wind | Pois | Holy | Dark | Ghost | Undead |
|---|---|---|---|---|---|---|---|---|---|---|
| Neutral | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 25 | 100 |
| Water | 100 | 25 | 100 | 150 | 50 | 100 | 75 | 100 | 100 | 100 |
| Earth | 100 | 100 | 100 | 50 | 150 | 100 | 75 | 100 | 100 | 100 |
| Fire | 100 | 50 | 150 | 25 | 100 | 100 | 75 | 100 | 100 | 125 |
| Wind | 100 | 175 | 50 | 100 | 25 | 100 | 75 | 100 | 100 | 100 |
| Poison | 100 | 100 | 125 | 125 | 125 | 0 | 75 | 50 | 100 | -25 |
| Holy | 100 | 100 | 100 | 100 | 100 | 100 | 0 | 125 | 100 | 150 |
| Dark | 100 | 100 | 100 | 100 | 100 | 50 | 125 | 0 | 100 | -25 |
| Ghost | 25 | 100 | 100 | 100 | 100 | 100 | 75 | 75 | 125 | 100 |
| Undead | 100 | 100 | 100 | 100 | 100 | 50 | 100 | 0 | 100 | 0 |

**Defence level 2**

| Atk \ Def | Neut | Water | Earth | Fire | Wind | Pois | Holy | Dark | Ghost | Undead |
|---|---|---|---|---|---|---|---|---|---|---|
| Neutral | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 25 | 100 |
| Water | 100 | 0 | 100 | 175 | 25 | 100 | 50 | 75 | 100 | 100 |
| Earth | 100 | 100 | 50 | 25 | 175 | 100 | 50 | 75 | 100 | 100 |
| Fire | 100 | 25 | 175 | 0 | 100 | 100 | 50 | 75 | 100 | 150 |
| Wind | 100 | 175 | 25 | 100 | 0 | 100 | 50 | 75 | 100 | 100 |
| Poison | 100 | 75 | 125 | 125 | 125 | 0 | 50 | 25 | 75 | -50 |
| Holy | 100 | 100 | 100 | 100 | 100 | 100 | -25 | 150 | 100 | 175 |
| Dark | 100 | 100 | 100 | 100 | 100 | 25 | 150 | -25 | 100 | -50 |
| Ghost | 0 | 75 | 75 | 75 | 75 | 75 | 50 | 50 | 150 | 125 |
| Undead | 100 | 75 | 75 | 75 | 75 | 25 | 125 | 0 | 100 | 0 |

**Defence level 3**

| Atk \ Def | Neut | Water | Earth | Fire | Wind | Pois | Holy | Dark | Ghost | Undead |
|---|---|---|---|---|---|---|---|---|---|---|
| Neutral | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 0 | 100 |
| Water | 100 | -25 | 100 | 200 | 0 | 100 | 25 | 50 | 100 | 125 |
| Earth | 100 | 100 | 0 | 0 | 200 | 100 | 25 | 50 | 100 | 75 |
| Fire | 100 | 0 | 200 | -25 | 100 | 100 | 25 | 50 | 100 | 175 |
| Wind | 100 | 200 | 0 | 100 | -25 | 100 | 25 | 50 | 100 | 100 |
| Poison | 100 | 50 | 100 | 100 | 100 | 0 | 25 | 0 | 50 | -75 |
| Holy | 100 | 100 | 100 | 100 | 100 | 125 | -50 | 175 | 100 | 200 |
| Dark | 100 | 100 | 100 | 100 | 100 | 0 | 175 | -50 | 100 | -75 |
| Ghost | 0 | 50 | 50 | 50 | 50 | 50 | 25 | 25 | 175 | 150 |
| Undead | 100 | 50 | 50 | 50 | 50 | 0 | 150 | 0 | 100 | 0 |

**Defence level 4**

| Atk \ Def | Neut | Water | Earth | Fire | Wind | Pois | Holy | Dark | Ghost | Undead |
|---|---|---|---|---|---|---|---|---|---|---|
| Neutral | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 0 | 100 |
| Water | 100 | -50 | 100 | 200 | 0 | 75 | 0 | 25 | 100 | 150 |
| Earth | 100 | 100 | -25 | 0 | 200 | 75 | 0 | 25 | 100 | 50 |
| Fire | 100 | 0 | 200 | -50 | 100 | 75 | 0 | 25 | 100 | 200 |
| Wind | 100 | 200 | 0 | 100 | -50 | 75 | 0 | 25 | 100 | 100 |
| Poison | 100 | 25 | 75 | 75 | 75 | 0 | 0 | -25 | 25 | -100 |
| Holy | 100 | 75 | 75 | 75 | 75 | 125 | -100 | 200 | 100 | 200 |
| Dark | 100 | 75 | 75 | 75 | 75 | -25 | 200 | -100 | 100 | -100 |
| Ghost | 0 | 25 | 25 | 25 | 25 | 25 | 0 | 0 | 200 | 175 |
| Undead | 100 | 25 | 25 | 25 | 25 | -25 | 175 | 0 | 100 | 0 |

Patterns worth remembering:
- **Neutral attacks are 100 % against everything except Ghost** (25 / 25 / 0 / 0 %).
- **The element that counters a level-3 or level-4 target deals 200 %.** Its
  neighbours are weak: Water does **0 %** to Wind 3/4 while Wind does 200 %,
  and Fire, Earth and Wind each do 0 % to the next element along the cycle.
- **Holy and Dark at level 3/4 are hit only by each other** (175/200 %).
  Elemental attacks drop to 25 % → 0 % against them.
- **Ghost targets** take 0 % from Neutral at level 3/4, so they need an element, a Ghost attack or magic.
- **Undead targets**: Holy and Fire do well (Fire 175 % against level 3), while Poison and Dark heal them and are clamped to 0.

### 1.2 What gives an attack its element

`battle_get_weapon_element`, `battle.cpp:3461-3502`:

| Source | Rule | Cite |
|---|---|---|
| Skill with a fixed element (`Element: Fire` in `skill_db.yml`) | The skill's element wins over everything. Weapon, arrow and endow are ignored. | `:3462` |
| `Element: Weapon` (normal attacks, Bash, Bowling Bash, Arrow Shower, Double Strafe…) | The weapon's element, `status.rhw.ele`, is used… | `:3468-3475` |
| … with an elemental arrow, bullet or kunai | …replaced by the ammo's `bAtkEle`, but only if the ammo has one. A Neutral arrow keeps an elemental bow's element. | `:3477`, `pc.cpp:3911-3922` |
| … with an endow status | **An endow overrides the weapon and the arrow.** `status_calc_attack_element` gives SC_ENCHANTARMS (converters) priority, then Water/Earth/Fire/Wind endows, Enchant Poison, Aspersio (Holy), Shadow, Ghost. | `status.cpp:8836-8866`, `battle.cpp:3484` |
| `Element: Endowed` / `Random` | Endow element only / random element. | `:3490-3493` |
| Magic `Element: Weapon` (e.g. NPC_MAGICALATTACK) | The weapon element. For monsters this is Neutral, see 1.4. | `:3505-3528` |
| Misc skills (traps, Acid Demonstration, Gravitation…) | Weapon/Endowed is **forced to Neutral**. Fixed elements are kept. | `:3530-3541` |

Ways to give the party an element (pre-re DB):

| Source | Element | Cost / catalyst | Notes |
|---|---|---|---|
| Sage **Endow Blaze / Frost Weapon / Lightning Loader / Seismic Weapon** (SA_FLAMELAUNCHER 280, SA_FROSTWEAPON 281, SA_LIGHTNINGLOADER 282, SA_SEISMICWEAPON 283) | Fire / Water / Wind / Earth | Red Blood / Crystal Blue / Wind of Verdure / Green Live, 1 each (`skill_db.yml` Requires) | Lasts 20 min (lv 1-4) or 30 min (lv 5). **Success 70/80/90/100/100 % by level. A failure unequips the target's weapon.** Fails if the target is unarmed. (`skills/mage/endowblaze.cpp:26-37`) |
| Priest **Aspersio** (PR_ASPERSIO 68) | Holy | 1 Holy Water | 60-180 s. |
| Assassin **Enchant Poison** (AS_ENCHANTPOISON 138) | Poison | — | 30-165 s. |
| Elemental Converter items 12114-12117 | Fire / Water / Earth / Wind | Consumable (`itemskill ITEM_ENCHANTARMS`) | `item_db_usable.yml:3649-3688`. SC_ENCHANTARMS beats every other endow. |
| Small Bottle (12353) | Water | Consumable, 90 s | `item_db_usable.yml:6591-6601` |
| Arrows (bAtkEle) | Silver/Holy/Counter-Evil = Holy, Fire, Crystal/Frozen = Water, Wind, Stone = Earth, Immaterial = Ghost, Rusty/Poison = Poison, Shadow = Dark | — | `item_db_etc.yml` ids 1750-1772 |
| Bullets / spheres / kunai | Silver Bullet = Holy; Flare / Lightning / Poison / Blind / Freezing sphere; elemental kunai | — | ids 13200-13259 |

Fields (pre-re, `battle.cpp:531-560`): with **Volcano / Deluge / Violent Gale**
on the attacker, Fire / Water / Wind hits deal **+10/14/17/19/20 %** by level
(`status.cpp:10996`). The ATK, HP and FLEE part of each field only works for a
character whose *armour* matches it (`status.cpp:10999-11030`).

### 1.3 Armour (defence) element

- A player's def element is Neutral 1. An armour card with `bDefEle` changes it:

  | Card (Armor slot) | Element | Drops from |
  |---|---|---|
  | Ghostring | Ghost 1 (also −25 % HP regen) | Ghostring (Class Boss) |
  | Angeling | Holy 1 | Angeling (Class Boss) |
  | Pasana | Fire 1 | Pasana |
  | Swordfish | Water 1 | Swordfish |
  | Sandman | Earth 1 | Sandman |
  | Dokebi | Wind 1 | Dokebi |
  | Argiope | Poison 1 | Argiope |
  | Bathory | Dark 1 | Bathory |
  | Evil Druid | Undead 1 | Evil Druid |

- Statuses override the armour element (`status_calc_element`, `status.cpp:8769-8792`):
  Frozen = Water 1, Stone = Earth 1, Benedictio = Holy 1, Change Undead = Undead 1,
  armour scrolls = SC_ELEMENTALCHANGE. Freezing a monster therefore makes it
  **Water 1**: Wind hits for 175 % and Fire for 50 %.
- Resist potions (12118-12121) are not an element. They add +20 % resistance to
  one element and −15 % to the opposite one (`item_db_usable.yml:3689-3728`).

### 1.4 What element are monster attacks?

- **A monster's normal attack has no element.** `attack_attr_none: 14`
  (mob + pet + homunculus, `battle.conf:134`) makes the element step **return
  early** for `skill_id == 0` (`battle.cpp:3670-3671`), so a monster's normal
  attack does 100 % against every armour element. Monsters also have no attack
  element in `mob_db` (`mob.cpp` sets only `def_ele`, `:5386`), so their
  `rhw.ele` is Neutral.
  - **Consequence:** armour element cards (Ghostring, Pasana, Evil Druid…) do
    **nothing** against a monster's normal attacks. To reduce those, use
    `bSubEle Neutral` (Raydric, Noxious, Deviling…) together with race, size
    and class reductions.
- **Monster skills do use the element table** against the player's armour:
  - Skills with a fixed element (NPC_FIREATTACK, NPC_DARKBREATH, Dark Strike,
    Jupitel…) use that element.
  - Skills with `Element: Weapon` (NPC_COMBOATTACK, NPC_CRITICALSLASH, Hell
    Judgement, Bash…) hit as **Neutral**. Ghost armour cuts those to 25 %.
  - Misc skills are Neutral.
- Monsters change their *own* def element with `NPC_CHANGEFIRE`,
  `NPC_CHANGEWATER` and similar (skill ids 161-169). Check
  `mob_skill_db.txt` before trusting `mob_db`'s element.

---

## 2. Sizes

### 2.1 Weapon × target size

The table is `db/size_fix.yml:34-87` plus the pre-re overrides in
`db/pre-re/size_fix.yml:35-40` (Knuckle and Whip). Unlisted fields default to
100 (`status.cpp:501-580`). It matches iRO Wiki's [Size](https://irowiki.org/classic/Size) table.

| Weapon | Small | Medium | Large |
|---|---|---|---|
| Fist (unarmed) | 100 | 100 | 100 |
| Dagger | 100 | 75 | 50 |
| 1H Sword | 75 | 100 | 75 |
| 2H Sword | 75 | 75 | 100 |
| 1H / 2H Spear | 75 | 75 (**100 mounted**) | 100 |
| 1H / 2H Axe | 50 | 75 | 100 |
| Mace | 75 | 100 | 100 |
| 2H Mace, Staff, 2H Staff | 100 | 100 | 100 |
| Bow | 100 | 100 | 75 |
| Knuckle (claw) | 100 | 75 | 50 |
| Instrument | 75 | 100 | 75 |
| Whip | 75 | 100 | 50 |
| Book | 100 | 100 | 50 |
| Katar | 75 | 100 | 75 |
| Guns, Huuma | 100 | 100 | 100 |

A spear on a Peco uses its Large value for Medium targets (`status.cpp:4238-4244`).

### 2.2 What escapes the size fix

- **Monsters, pets and homunculi never get a size fix.** Only players do (`battle.cpp:2581`).
- **Magic and misc damage** are not size-fixed.
- **STR / status ATK** (`batk`) is added after the size fix (`:2622-2625`).
  Only the weapon's ATK roll is reduced.
- **Weapon Perfection** (BS_WEAPONPERFECT, SC_WEAPONPERFECTION) gives 100 %
  against every size, for the party members it buffs (`:4152`).
- **Drake card** (`bNoSizeFix`, MVP card) does the same permanently (`:2582`).
- **Spiral Pierce** ignores the table above and uses its own: Small 125 %,
  Medium 100 %, Large 75 % (`:4046-4053`).
- Size cards (Desert Wolf / Skeleton Worker / Minorous) are card bonuses (section 4), not the size fix.

---

## 3. Races, race groups and classes

| Race (`Race:` in mob_db) | Count in pre-re mob_db | Notes |
|---|---|---|
| Formless | 218 | |
| Demihuman | 176 | Also players (RC_Player_Human). Many cards cover both. |
| Brute | 152 | Also Doram players (RC_Player_Doram). |
| Demon | 141 | Signum Crucis and Divine Protection work on Demons. |
| Plant | 82 | |
| Insect | 73 | |
| Undead | 71 | **Race** Undead is not **element** Undead, see below. |
| Fish | 33 | |
| Angel | 31 | |
| Dragon | 27 | |

**Undead detection.** `undead_detect_type: 0` (`battle.conf:72`): Heal-as-damage,
Signum Crucis, Provoke's undead immunity and Turn Undead all look at the
**element** Undead. Race Undead is only immune to Freeze and Stone.

**Race groups (Race2)** are an extra tag, and cards add damage per group
(`bAddRace2`, +30 %). In pre-re mob_db:

| Group | Members |
|---|---|
| Goblin | Goblin ×5, Goblin Archer, Goblin Leader |
| Kobold | Kobold ×3, Kobold Archer, Kobold Leader |
| Orc | Orc Warrior, Orc Skeleton, Orc Zombie, Orc Archer, High Orc, Orc Lady. **Orc Hero and Orc Lord are not in the group.** |
| Golem | Golem, Stalactic, Lava, Wooden, Bradium Golem |
| Ninja | Assaulter ×2, Shinobi ×2 |
| Others | Treasure (49), Manuk (8), Splendide (5), GvG (4) |

**Classes.** `Class: Normal | Boss | Guardian | Battlefield` (mob_db has 281 Boss
entries). `MobDatabase::loadingFinished` (`mob.cpp:5581-5598`) gives every
**Class: Boss** these modes:

- `MD_STATUSIMMUNE`: immune to every BossResist status (section 6.4).
- `MD_KNOCKBACKIMMUNE`: cannot be pushed by Bowling Bash, Arrow Repel, Firewall
  and similar. It also cannot be snared, see below.
- `MD_DETECTOR`: sees Hide and Cloaking.

Guardians get `MD_STATUSIMMUNE` only.

`Mvp: true` is separate from `Class: Boss`. Minibosses such as Ghostring,
Angeling, Deviling, Mysteltainn and Executioner are Class Boss but not MVPs.
"vs Boss" cards (`Class_Boss`) work on all of them.

---

## 4. Cards and equipment bonuses

### 4.1 How they combine: `battle_calc_cardfix`, pre-re branch

The rule (`battle.cpp:770-1200`): **bonuses of the same category add together,
and the categories multiply.** The multiplier starts at 1000, so the result is
rounded down to 0.1 % (`APPLY_CARDFIX`, `:807`).

**Physical (BF_WEAPON), attacker side, melee** (`:972-1086`)

    dmg × (100 + Σ race + Σ race_ALL)%
        × (100 + Σ ele[target def element] + Σ ele_ALL)%
        × (100 + Σ size + Σ size_ALL)%
        × Π over each race2 of target (100 + Σ race2)%
        × (100 + Σ class + Σ class_ALL)%
        × (100 + 10 + 2·AdvKatarMastery)%      ← pre-re, katar only (:1057)
        × (100 + bAddDamageClass[this mob id])%
        × (100 + bShortAtkRate)% if BF_SHORT,  × (100 + bLongAtkRate)% if BF_LONG

- `bAddEle` is matched against the **target's def element**, not the attack
  element. Vadon "+20 % vs Fire" means "against Fire-element monsters".
- **Left hand:** `left_cardfix_to_right: yes` (`conf/battle/player.conf:20`).
  The off-hand weapon's cards are **added** to the right hand's in each category
  (`:1020-1052`). Ignore-DEF and DEF-ratio cards also move to the right hand (`:3192-3197`, `:3376-3381`).
- **Armour, garment, shoes and accessories** with `bAddRace` and similar count
  as right hand. Example: Gloom Under Night, armour slot, +40 % vs Holy/Dark
  elements and Angel/Demon races.
- **Ranged (bow or gun normal attacks and arrow skills, `arrow_atk`)** (`:944-971`):
  the same categories, plus the arrow's own `bAddRace`/`bAddEle`/… added into
  each category. Example: Holy Arrow, +5 % vs Demon.

**Which attacks get the attacker cards:** every BF_WEAPON hit, normal or skill,
except skills flagged `IgnoreAtkCard` in `skill_db.yml`. Pre-re examples:

- Acid Terror and Demonstration
- Soul Breaker (ASC_BREAKER)
- Meteor Assault
- Cart Termination
- Venom Splasher, Venom Knife
- Sprinkle Sand, Freezing Trap
- Throw Shuriken / Kunai, Bull's Eye, Ground Drift, Tatami Gaeshi
- Turn Undead (magic)

**Magic (BF_MAGIC), attacker side** (`:850-870`). Only `bMagic*` bonuses count,
never `bAddRace`/`bAddEle`. The categories are race (+race2), target def
element, **attack element** (`bMagicAtkEle`), size, class, and monster id
(`bAddMDamageClass`), all multiplied.

**Misc (BF_MISC)** (traps, Acid Demonstration, Gravitation, Pressure…) gets **no
attacker cards**. Only the target's reductions apply (`:1164-1200`).

**Target side (reductions, the player is hit)**, physical `:1087-1150` and magic `:872-934`:

    dmg × (100 − Σ subEle[attack element] − subEle_ALL)%
        × (100 − Σ subDefEle[attacker's own element])%         (weapon/misc)
        × (100 − Σ subSize[attacker size])% × (100 − weapon_subsize / magic_subsize)%
        × (100 − Σ subRace2[attacker groups])%
        × (100 − Σ subRace[attacker race])%
        × (100 − Σ subClass[attacker class])%
        × (100 − bAddDefMonster[this mob id])%
        × (100 − bNearAtkDef)% if BF_SHORT,  else (100 − bLongAtkDef)%
        × (100 − bMagicDefRate)% (magic only) × SC_DEF_RATE / SC_MDEF_RATE

- `bSubSize` keys on the **attacker's** size. Executioner card cuts damage from
  **Large monsters**. It has nothing to do with your own size.
- **Pre-re only:** near/long reductions also apply to **magic**
  (`:924-930`, "ranged defense also counts vs magic"). Magic is BF_LONG when
  the skill's range is ≥ 4 (`:5862`), so **Horn card (−35 % long) cuts most bolts
  and AoE spells by 35 %**.
- `cardfix_monster_physical: yes` (`conf/battle/items.conf:144`, `battle.cpp:801-804`):
  monster magic counts as "weapon" for the flag-filtered `bonus3 bSubEle` and
  `bSubRace` items. Plain `bSubEle`/`bSubRace` work on everything anyway.
- A monster's normal attack is Neutral (1.4), so **`bSubEle,Ele_Neutral` (Raydric) is the general reduction against normal attacks.**

### 4.2 Common damage cards (pre-re item_db / mob_db)

Weapon slot unless stated. "Source" is the monster that drops it in
`db/pre-re/mob_db.yml`. **MVP** = `Mvp: true` drop; **Boss** = Class Boss
miniboss; otherwise an ordinary monster.

| Category | Card | Bonus | Source |
|---|---|---|---|
| Race +20 % | Hydra | DemiHuman (+player humans) | Hydra L14 |
| | Goblin | Brute | Goblin |
| | Strouf | Demon | Strouf L48 |
| | Caramel | Insect | Caramel |
| | Scorpion | Plant | Scorpion |
| | Flora | Fish | Flora |
| | Earth Petite | Dragon | Petite |
| | Peco Peco Egg | Formless | Peco Peco Egg |
| | Deviace | +7 % DemiHuman/Brute/Plant/Insect | Deviace |
| Element +20 % (vs target element) | Vadon | Fire | Vadon |
| | Drainliar | Water | Drainliar |
| | Mandragora | Wind | Mandragora |
| | Kaho | Earth | Kaho |
| | Anacondaq | Poison | Anacondaq |
| | Orc Skeleton | Holy | Orc Skeleton |
| | Santa Poring | Dark | Santa Poring |
| | Mao Guai | Ghost | Mao Guai |
| | Scorpion King | Undead | **no drop source in pre-re mob_db** (its drop line is commented out) |
| Size | Desert Wolf / Skeleton Worker / Minorous | +15 % Small / Medium / Large, +5 ATK | ordinary |
| Class | Abysmal Knight | +25 % vs Class Boss | Abysmal Knight L79 (ordinary) |
| | Turtle General | +20 % vs all, autocasts Magnum Break | **MVP** |
| | Randgris | +10 % vs all, autocasts Dispell | **MVP** |
| Race2 +30 % | Goblin Leader / Kobold Leader / Orc Lady / Lava Golem | Goblin / Kobold / Orc / Golem group | ordinary |
| Monster id | Crab / Aster / Shellfish +30 %, Elder +40 % | single monster ids | ordinary |
| Ranged | Archer Skeleton | +10 % long-range damage | ordinary |
| Ignore DEF | Samurai Specter | ignores DEF of **Normal** class (not bosses); −HP drain | **MVP** |
| DEF→damage | Memory of Thanatos | `bDefRatioAtkClass` all (see 5.1); −30 DEF/FLEE | **MVP** |
| No size fix | Drake | 100 % vs all sizes | **MVP** |
| Armour slot | Gloom Under Night | +40 % vs Holy/Dark element and Angel/Demon race | **MVP** |
| Magic | Dolor of Thanatos (+10 % Angel), Skeggiold (+2 % Demon) | `bMagicAddRace` | Boss |
| Magic, shoes | Fallen Bishop Hibram | MATK +10 %, +50 % magic vs Angel/DemiHuman, −50 % SP | **MVP** |

Weapons with the same effects: Ice Pick (1230, 13017) has `bDefRatioAtkClass`.
Several weapons have `bIgnoreDefRace` (Plant, Dragon or DemiHuman), for
example `item_db_equip.yml:961`, `:1645`, `:1708`.

### 4.3 Common reduction cards

| Slot | Card | Reduction | Source |
|---|---|---|---|
| Shield −30 % race | Thara Frog | DemiHuman (+player humans) | ordinary |
| | Orc Warrior | Brute | ordinary |
| | Khalitzburg | Demon | ordinary |
| | Bigfoot | Insect | ordinary |
| | Rafflesia | Fish | ordinary |
| | Sky Petite | Dragon | ordinary |
| | Penomena | Formless | ordinary |
| | Teddy Bear | Undead race | ordinary |
| | Anubis | Angel | ordinary |
| | Soldier Andre | Plant | **no drop source in pre-re mob_db** |
| | Medusa | −15 % Demon, Stone immunity | ordinary |
| Shield, class | Alice | **−40 % from Class Boss**, +40 % from Normal | ordinary (L62) |
| Shield −25 % size (attacker) | Mysteltainn / Ogretooth / Executioner | Small / Medium / Large | **Boss** (minibosses) |
| | Hodremlin | −15 % all sizes | ordinary |
| Shield, range | Horn | **−35 % long range**: ranged weapons, ranged monster skills and long-range magic | ordinary |
| Shield, element | Tatacho / Aqua Elemental / Draco / Luciola Vespa / Centipede / Cornus / Dark Shadow | −20 % Neutral / Water / Earth / Wind / Poison / Holy / Dark (+5 % dmg vs same) | ordinary, L82-114 |
| Garment −30 % element | Jakk (Fire), Marse (Water), Hode (Earth), Dustiness (Wind), Myst (Poison), Isis (Dark), Marionette (Ghost), Orc Zombie (Undead) | +5 FLEE | ordinary |
| Garment, Neutral | Raydric −20 %; Noxious −10 % & −10 % long; Orc Baby −10 % (−15 % at +9); Harpy −15 % | | ordinary |
| | Deviling | −50 % Neutral, **+50 % from every other element** | Boss |
| | Whisper | +20 FLEE, **+50 % Ghost damage taken** | ordinary |
| Headgear | Giearth (Earth 15), Permeter (Dark/Undead 15), Leib Olmai (Fire 10), Leaf Cat (Water 10), Giant Hornet (Wind 10), Dryad (Earth 10) | | ordinary |
| Armour | Element cards (1.3); Orc Lord reflects 30 % melee (**MVP**); Maya reflects 50 % magic (shield, **MVP**) | | |
| Shoes | Am Mut, Iron Fist, Mini Demon and similar: **+20 % damage taken** from a race, +10 % EXP | | ordinary |

Equal reductions **within** a category add up. Two −30 % race items make −60 %.
Different categories multiply: Thara Frog plus Raydric against a DemiHuman
normal attack is 0.7 × 0.8 = **0.56**.

---

## 5. DEF and MDEF

### 5.1 Physical DEF (`battle_calc_defense_reduction`, `battle.cpp:4721-4885`)

    dmg = dmg × (100 − DEF)/100 − VitDEF          (DEF capped at 100, :4873)

| Target | VitDEF (random each hit) | Cite |
|---|---|---|
| Monster (and pets) | `VIT + rnd(0, (VIT/20)² − 1)` | `:4826-4835` |
| Player | `⌊0.3·def2⌋ + rnd(0, max(0, ⌊def2²/150⌋ − ⌊0.3·def2⌋ − 1)) + ⌊0.5·def2⌋`, where def2 = VIT (+ buffs) | `:4808-4812` |

- Monster `DEF` is mob_db `Defense`. Monster soft DEF is mob_db `Vit` (`status.cpp:2714`).
- Player hard DEF comes from equipment and refines.
- Pre-re DEF is a **flat percentage**, so a 60-DEF monster blocks 60 % of a
  normal hit. Ignore-DEF effects therefore matter a lot.
- **Several attackers:** a player targeted by ≥ 3 monsters loses 5 % of DEF and
  VitDEF per attacker beyond the second (`vit_penalty_*`, `battle.conf:101-111`, `battle.cpp:4789-4806`).
  Steel Body keeps hard DEF.
- DEF modifiers on monsters:

  | Effect | Hard DEF | VitDEF | Cite |
  |---|---|---|---|
  | Provoke | −(5 + 5·lv) % | same | `status.cpp:11667-11669`, `:7804`, `:7891` |
  | Signum Crucis | −(10 + 4·lv) % | — | Undead element / Demon only; `:10878`, `:10327-10331` |
  | Frozen / Stone | ÷2 | — | MDEF +25 %; `:7793-7795`, `:7950-7953` |
  | Poison | −25 % | −25 % | `:7796`, `:7887` |
  | Steel Body | hard DEF and MDEF = 90 | | `:7762`, `:7932` |

**Hits that ignore DEF** (`attack_ignores_def`, `:3329-3390`):

- **Critical hits**, pre-re (`:3341-3343`).
- `IgnoreDefense` skills: Auto Counter, Acid Terror, Asura Strike (MO_EXTREMITYFIST),
  Sacrifice, Spiral Pierce, Piercing Shot, NPC_PIERCINGATT, NPC_CRITICALSLASH…
- Equipment with `bIgnoreDefRace/Class/Ele`, for example Samurai Specter card
  (Normal class only).
- Acid Terror subtracts the target's VitDEF from its base damage instead of
  ignoring it (`:4231-4232`).

**DEF-ratio ("piercing") hits** (`is_attack_piercing`, `:3166-3200`, applied at `:4874-4877`):

    dmg × (DEF + VitDEF) / 100            (×2 for Investigate / Occult Impaction)

This is Ice Pick, Thanatos card and Investigate. **Against low-DEF targets
(DEF + VIT < 100) it *reduces* damage.** It is good only against high-DEF
bosses, and does not apply to critical hits (`:3176`).

### 5.2 MDEF (`battle.cpp:6091-6116`)

    dmg = MATK_roll × skill% × (100 − MDEF)/100 − softMDEF

- softMDEF = INT + ⌊VIT/2⌋ (`status.cpp:2718`).
- MATK = INT + (INT/7)² to INT + (INT/5)² (`status.cpp:2511-2516`).
- A result below 1 becomes 1 (`:6210-6211`), so a monster with MDEF ≥ 100 takes 1 per hit.
- Skills flagged `IgnoreDefense` ignore MDEF: Heal, Sanctuary, Turn Undead,
  Fire Pillar, Aspersio, Benedictio. So do equipment with `bIgnoreMdef*`.
- `bIgnoreMdefRace/Class` (percentage) cuts hard MDEF first (`:6074-6113`).

---

## 6. HIT, FLEE, criticals and status resistance

### 6.1 Formulas (pre-re, `status_calc_misc`, `status.cpp:2700-2740`)

| Stat | Formula | Note |
|---|---|---|
| HIT | BaseLv + DEX (+ bonuses) | Monsters: mob Level + DEX |
| FLEE | BaseLv + AGI (+ bonuses) | Monsters: mob Level + AGI |
| Critical (player) | 1 + 0.3 % per LUK (`cri = 10 + LUK·10/3`, in 0.1 %) | ×2 with a **Katar**, applied after all bonuses (`:6147-6150`) |
| Perfect dodge | 1 + LUK/10 % (`flee2 = LUK + 10`, in 0.1 %) | **Players only** (`enable_perfect_flee: 1`) |

**Chance to hit** (`battle.cpp:3263-3316`):

    hit% = clamp(80 + attackerHIT − targetFLEE, 5, 100)

- **100 % hit needs HIT ≥ FLEE + 20.**
- **95 % dodge needs FLEE ≥ HIT + 75.**
- Crowding: from 3 attackers on, a player's FLEE drops 10 % per attacker beyond
  the second (`agi_penalty_*`, `battle.conf:85-95`, `battle.cpp:3268-3279`).
- Hits that skip the FLEE roll:
  - criticals;
  - targets that are frozen, stunned, asleep or stoned (`tsc->opt1`, `:3250`);
  - `IgnoreFlee` skills: Backstab, Investigate, Asura, Venom Splasher, traps,
    Blitz Beat, Falcon Assault, Pressure, Gravitation;
  - all magic.

**Criticals** (`is_attack_critical`, `:3018-3156`):

- Only normal attacks and `Critical` skills (Sharpshooting +20 %, Auto Counter
  ×2 chance) can crit.
- **Monsters cannot crit**: `enable_critical: 17` = players + mercenaries
  (`battle.conf:21`). The exception is NPC_CRITICALSLASH, which always crits.
- Every point of target LUK cuts crit chance by 0.2 % (`:3062`). A sleeping target doubles it (`:3064`).
- A pre-re critical hit:
  - always lands;
  - **ignores DEF and VitDEF**;
  - takes the **maximum** weapon ATK, without the DEX minimum (`:2541-2563`);
  - adds `bCritAtkRate` (`:4198-4201`);
  - has **no** 1.4× multiplier (that is renewal).
- Perfect dodge is checked *before* the crit roll, so a lucky dodge also stops crits.

### 6.2 Quagmire and Decrease AGI on monsters

| Skill | Effect on a monster | On a player | Boss? | Cite |
|---|---|---|---|---|
| Quagmire | **AGI and DEX −10 per level** (−50 at lv 5), move speed halved, cancels Increase AGI / Improve Concentration | −5 per level | **Works on bosses** (no BossResist flag) | `status.cpp:11643-11645`, `:6850`, `:7058`, `:8082` |
| Decrease AGI | AGI −(2 + lv), speed −25 % | same | **Blocked** (BossResist) | `:10845-10854`, `:8080` |

Quagmire lowers a boss's FLEE by 10·lv, because FLEE = Lv + AGI. It also lowers
its HIT by 10·lv, so the party's FLEE dodges more of its attacks.

### 6.3 Monster buffs to watch

- **Power Up (NPC_POWERUP)**: SC_POWERUP gives **+200 % ATK (×3)** and **HIT ×2**
  (`skills/npc/powerup.cpp:14`, `battle.cpp:4377-4378`, `status.cpp:7567-7568`).
  Most MVPs cast it below 30 % HP (see MVP_TACTICS.md).
- **Assumptio** on a monster halves the damage it takes (`battle.cpp:1821-1826`).

### 6.4 Boss resistance

A status flagged `BossResist: true` in `db/pre-re/status.yml` simply **fails** on
an `MD_STATUSIMMUNE` target (`status.cpp:10191-10193`). Every Class Boss has that
mode (section 3). There are 64 such statuses in pre-re, including:

- Stone, Freeze, Stun, Sleep, Poison, Deadly Poison, Curse, Silence, Confusion, Blind, Bleeding, Coma (Coma is also `MvpResist`)
- **Provoke, Decrease AGI**, Blessing (the curse on enemies)
- Strip Weapon / Shield / Armour / Helm
- Fog Wall, Gravitation, Close Confine

**Statuses that do work on bosses**: Quagmire, **Lex Aeterna**, **Signum Crucis**
(Undead element or Demon race only), and **Ankle Snare**, whose boss exclusion is
`#ifdef RENEWAL` only (`skill.cpp:12200-12203`). Spider Web is [unverified]. Lex Aeterna fails on a frozen
or stoned target (`status.yml:560-568`, `Fail: Stone/Freeze`).

---

## 7. Melee vs ranged, and what blocks what

**How a hit is classified** (`battle_range_type`, `battle.cpp:2672-2748`):

| Attacker / attack | BF_SHORT (melee) | BF_LONG (ranged) |
|---|---|---|
| Player or monster normal attack | everything else | bow/gun ammo attacks; a **monster with AttackRange > 3** (`:2943-2945`, `initialize_weapon_data`) |
| Player skill | skill range **< 4** | range ≥ 4. Spiral Pierce (4) is ranged; Bash, Bowling Bash and Asura are melee. |
| Monster, pet or homunculus skill | target **within 3 cells** | **beyond 3 cells**, regardless of the skill (`skillrange_by_distance: 14`, `conf/battle/skill.conf:78`, `battle.cpp:2735-2742`) |
| Traps | always melee | |
| Arrow Shower or Bomb cast by a monster | always melee | |

The comment in `skill.conf:73-76` says "above 5". **The code's threshold is
< 4** (`:2745`). This file follows the code.

**Blocks** (`battle_status_block_damage`, `battle.cpp:1284-1500`):

| Effect | Stops | Does not stop | Details |
|---|---|---|---|
| **Safety Wall** | BF_SHORT **non-magic**: melee weapon hits, melee misc | magic, ranged | Blocks (lv + 1) hits (`skill.cpp:5803`). Pre-re has no HP pool. `:1441-1474` |
| **Pneuma** | BF_LONG **non-magic**: arrows, ranged monster attacks (range > 3), monster skills from beyond 3 cells, ranged misc | magic, melee | `:1476` |
| **Kyrie Eleison** | **weapon** damage, until the barrier is gone | magic damage passes through, but **still drains the barrier and uses up a hit** (`:1292-1304`) | Barrier = MaxHP × (10 + 2·lv) %, (lv/2 + 5) hits (`status.cpp:10917-10920`). Not on monsters (`status.cpp:10332-10336`). |
| **Assumptio** | — | — | Pre-re: all damage taken ×½ (⅔ in PvP) (`:1821-1826`) |
| Basilica | all attacks from non-boss attackers | | `:1478` |

Kyrie and Assumptio cancel each other (see MVP_TACTICS.md).

---

## 8. Healing

**Heal (AL_HEAL), pre-re** (`skill_calc_heal`, `skill.cpp:521-690`):

    heal = ⌊(BaseLv + INT) / 8⌋ × (4 + 8 × SkillLv)          (:590)
           × (1 + 2 % × Meditatio lv) × (1 + bHealPower %) × target's heal-received buffs

- Example: base 99 and INT 99, Heal 10 → 24 × 84 = **2016** before bonuses.
- **Skill level ≥ `max_heal_lv` (11) → flat `max_heal` = 9999**
  (`skill.cpp:581-582`, `conf/battle/skill.conf:248-249`). Players learn Heal
  up to 10; level 11+ comes only from monster skills or scripts.
- Sanctuary heals lv × 100 per tick, 777 at lv 7-10 (`skill.cpp:543`).
- **Heal on Undead** (`skill.cpp:4433-4443`) works only when a *player* casts it,
  only on an enemy, and only on a target whose **element** is Undead.
  - Damage = heal ÷ 2 (`:610`). It is **Holy** magic that **ignores MDEF**
    (`IgnoreDefense`). Holy deals 150/175/200/200 % to Undead 1/2/3/4. It also
    gets `bMagicAddRace` bonuses and the target's reductions.
  - Heal 10 at 2016 gives 1008 base, so **~2016 damage on an Undead 4 target**
    with no FLEE roll.
- Turn Undead, pre-re: instant-kill chance = (20·lv + LUK + INT + BaseLv + 200 −
  200·HP/MaxHP) ‰, capped at 70 %. It never kills a status-immune target.
  Otherwise it deals BaseLv + INT + 10·lv (`battle.cpp:5902-5925`).
- Berserk (Frenzy) and Saturday Night Fever targets receive 0 healing (`skills/acolyte/heal.cpp:40-43`).

---

## 9. Other multipliers

| Effect | Pre-re value | Where it applies | Cite |
|---|---|---|---|
| **Lex Aeterna** | **×2** on the next damage instance, which is then consumed. A multi-hit skill counts once (its whole damage doubles); with a ground AoE, only the first tick doubles. Not on Soul Burn. Works on bosses. | end of hit, all damage types | `battle.cpp:1744-1752` |
| Provoke (on a monster) | ATK +(2 + 3·lv) %, DEF −(5 + 5·lv) % | ATK% step | `status.cpp:11661-11669` |
| Power-Thrust (BS_OVERTHRUST) | +5 %/lv to the skill ratio on self, +5 % flat on party members | skill-ratio step (additive with Max Power-Thrust, Berserk) | `status.cpp:11588-11600`, `battle.cpp:4426-4427` |
| Max Power-Thrust | +20 %/lv | skill-ratio step | `status.cpp:11585-11586` |
| Spear Dynamo (SC_CONCENTRATION) | ATK +5 %/lv, own DEF −5 %/lv | ATK% step | `status.cpp:11609-11618` |
| Monster Power Up | ATK +200 %, HIT ×2 | ATK% step | 6.3 |
| Curse | ATK −25 % | ATK% step | `battle.cpp:4363` |
| Impositio Manus | WATK +5·lv | flat | `status.cpp:11623` |
| Volcano / Deluge / Violent Gale | +10-20 % to that element's hits | element step | 1.2 |
| Frozen target hit by Wind | 175 % (Water 1) | element | 1.3 |
| Advanced Katar Mastery | +(10 + 2·lv) %, as a card | card step | `battle.cpp:1057-1058` |
| EDP | pre-re damage bonus "+50 + 50·lv %" per the code comment | **[unverified]**: where it applies was not traced | `status.cpp:10892-10895` |

The step a modifier belongs to decides how it stacks:

- **Skill-ratio** effects add together.
- **ATK%** effects add together, then multiply the result of the skill-ratio step.
- **Card** categories multiply each other.
- **Lex Aeterna** multiplies everything.

---

## 10. How to read a boss: checklist

1. **Look up the monster's real element** in `db/pre-re/mob_db.yml`
   (`Element`, `ElementLevel`, `Race`, `Size`, `Class`, `RaceGroups`, `Defense`,
   `MagicDefense`, `Vit`, `Agi`, `Level`). Then grep `mob_skill_db.txt` for
   `NPC_CHANGE*`, because an element change mid-fight resets the plan.
2. **Pick the element** from the table for its element **level**:
   - Level 1-2: the counter element deals 150-175 %.
   - Level 3-4: the counter deals 200 %, and the two neighbouring elements drop
     to **0 %**. Example: Water against Wind 4 = 0 %, Wind against Water 4 = 200 %.
   - Holy 3-4 or Dark 3-4: only the opposite element helps. Everything
     elemental is 0-50 %; Neutral stays 100 %.
   - Ghost: no Neutral hits. Use magic or an element.
   - Undead: Holy (Heal, Aspersio, Silver arrows, Grand Cross) or Fire.
     **Not** Poison or Dark.
3. **Mark the useless spells**: any skill whose fixed element scores ≤ 25 %. For
   a Wind 4 boss this means Cold Bolt, Frost Diver and Storm Gust (0 %), plus
   Jupitel Thunder and Lord of Vermilion (−50 %, clamped to 0).
4. **Weapon for physical attackers.** Use the size table (Daggers lose half
   against Large, Axes against Small). Neutral weapons are fine except against
   Ghost or Holy/Dark 3-4. Endow on demand, and remember a Sage endow below lv 4
   can fail and unequip the weapon.
5. **DEF.**
   - High hard DEF: prefer crits, IgnoreDefense skills, magic, or Ice Pick
     (when DEF + VIT > 100).
   - Low DEF: never use DEF-ratio weapons or cards.
   - Signum Crucis lowers hard DEF on Undead-element and Demon bosses.
6. **HIT.** The party needs HIT ≥ the boss's (Level + AGI) + 20 for 100 % hits.
   Quagmire takes 10·lv off the boss's AGI. Decrease AGI and Provoke do nothing
   to a Class Boss.
7. **Cards and gear.** Stack different categories, because they multiply:
   race + element + size + Boss class. Use Abysmal Knight for any Class Boss and
   the race2 cards for group members.
8. **Incoming damage.**
   - Normal attacks are Neutral and ignore armour element: use Raydric, a race
     shield and Alice.
   - Skills follow the element table: use armour element or garment cards.
   - A melee boss within 3 cells: use **Safety Wall**.
   - Ranged attacks (AttackRange > 3) and any skill from more than 3 cells away: use **Pneuma**.
   - Magic is blocked by neither. Use Horn for long-range magic, or MDEF.
9. **Status plan.** Against a Class Boss, only Lex Aeterna, Quagmire, Signum
   Crucis and damage matter. Every crowd-control status in section 6.4 fails.
10. **Burst windows.**
    - Lex Aeterna goes before the biggest single hit, not before an AoE tick.
      It cannot be cast on a frozen target.
    - Expect ×3 ATK from Power Up at low HP.
