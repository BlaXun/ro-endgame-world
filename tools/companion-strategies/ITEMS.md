# Fight items in pre-renewal rAthena: a reference for strategy plans

What a companion can drink, throw, read or burn in a fight, as **pre-renewal
rAthena** implements it. Plans name items in `UseItem:` (and `Requires: { Items }`,
`item_below`) by **AegisName** or by id. The tables give both, plus the name the
client shows.

**Where the numbers come from.** Item scripts, weights, prices and job or level
limits come from `rathena/db/pre-re/item_db_usable.yml` (`usable` below) and
`item_db_etc.yml` (`etc`). What a status does comes from `db/pre-re/status.yml` and
`src/map/status.cpp`. How potions heal comes from `src/map/pc.cpp`. Which NPC sells
what comes from `npc/merchants/shops.txt` and `npc/pre-re/merchants/shops.txt`,
which are the shop files a pre-re server loads. Line numbers are those of the
fork's `master` at `c8b69e407`. The wikis were used only to explain. Where they
disagree with the source, the source is what the game does.

**Units.**
- **Wt** is in game units, which is the yml `Weight` divided by 10. A Red Potion
  is `Weight: 70` in the yml and 7 in game.
- **Buy** is the item's base NPC price before Discount.
  - **NPC** means a pre-re shop sells it.
  - **drop**: no pre-re shop sells it, so it comes from monsters, crafting or
    quests.
  - **cash** means a cash-shop or event item whose yml price is a placeholder
    (2 or 20).
- **NoTrade**: the item's `Trade:` block forbids trading. A player cannot hand it
  to a companion, so only a script (the rig's `stock`) can put it in the bag.
- "Unverified" means the source was not read far enough, or the behaviour was not
  tested in game.

---

## 0. How item use works (what applies to every table below)

| Rule | Source |
|---|---|
| **Potion heal formula.** HP healed = script amount × (100 + 2·VIT + 10·*Increase HP Recovery* lv + 5·*Learning Potion* lv + gear `bAddItemHealRate`)%. Item-group bonuses (`bAddItemGroupHealRate`) and per-item bonuses (`bAddItemHealRate,<id>`) then multiply on top. SP works the same way with **INT** and *Increase SP Recovery*. VIT and INT are the totals with all bonuses. | `pc.cpp:10744-10795` |
| Critical Wound reduces it by its value, and `SC_NORECOVER_STATE` blocks it entirely. | `pc.cpp:10797-` |
| **`percentheal`** (Yggdrasil Berry/Seed, stat dishes) heals a percentage of max HP/SP. The VIT/INT bonus is **not** applied (`pc_percentheal` → `status_percent_heal`). | `pc.cpp:10841` |
| Who has the recovery skills: *Increase HP Recovery* (`SM_RECOVERY`, +10%/lv): Swordman, Knight, Crusader and their transcendents. *Increase SP Recovery* (`MG_SRECOVERY`, +10%/lv): Mage, Wizard, Sage and their transcendents. *Learning Potion* (`AM_LEARNINGPOTION`, +5%/lv, HP and SP): Alchemist, Creator. | |
| **Item delay.** Plain potions have no delay of their own. The server allows one item every `item_use_interval` = **100 ms** (`conf/battle/items.conf:68`). | `pc.cpp:6570` |
| Some items have their own cooldown in `Delay:` (Yggdrasil Berry 5 s, Seed 3 s). | `pc.cpp:6531` |
| Cash foods share a 60 s interval (`cashfood_use_interval`). | `pc.cpp:6572` |
| On top of that, the engine drinks at most one potion a second, and a `UseItem` rule without `Cooldown` waits 1 s. | |
| **No item works while Stoned, Frozen, Stunned or Asleep.** `pc_useitem` refuses any item while `opt1` is set, except during the *petrifying* phase (`OPT1_STONEWAIT`). No item cures those four statuses, so a plan cannot react to them with an item. | `pc.cpp:6514` |
| **Statuses that forbid all item use** (`NoConsumeItem` in `status.yml`): Hiding, Trick Dead, **Berserk (a Lord Knight's Frenzy)**, Gravitation, Crystalize, Deep Sleep, and some others. **A Frenzied Lord Knight cannot drink.** | `pc.cpp:6456`, `status.yml:1211` |
| **`Delayconsume` items** (Fly Wing, converters, magic scrolls, Yggdrasil Leaf, Anodyne, Aloevera) cast a skill and are used up only when the cast goes through. They cannot be used **while sitting**, while mounted, or during another cast. The engine's `use_item` also refuses during a cast. | `pc.cpp:6518-6526` |
| `itemskill` ignores the skill's own costs (SP, gemstones) unless the item says otherwise, so a Yggdrasil Leaf needs no Blue Gemstone. Silence probably blocks item skills too. rAthena's own FIXME says it does; **unverified**. | `doc/script_commands.txt:5674` |
| **Job and level limits** (`Jobs:`, `EquipLevelMin:`) are checked on every use, by a companion too. A `UseItem` rule for an item the job cannot use never fires. | `pc.cpp:6447-6460` |
| **Weight.** Max weight = the job's base (`db/pre-re/job_stats.yml`) + **30 × STR**, plus 200 per level of Enlarge Weight Limit, plus 1000 on a Peco. | `status.cpp:3663-3683` |
| Above **50 %** of max weight, no natural HP/SP regeneration, which includes the Priest's Meditatio SP. Above **90 %**, no attacking and no skills. | `battle.cpp:8405`, `conf/battle/player.conf:77` |
| An item that would push the carrier past 100 % is refused. | |
| **Monsters' normal attacks are Neutral** in rAthena: a mob's `rhw.ele` is never set from its element (`mob.cpp:5386` sets only `def_ele`). Element-resist potions therefore help only against elemental **skills** (Fire Ball, Storm Gust, Lord of Vermilion…). Against normal hits the answer is gear (Raydric Card −20 % Neutral). | |

Base max weight by job (game units, before STR): Mage 2200; Acolyte, Thief,
Wizard, Sage, Assassin and Rogue 2400; Archer, Priest, Monk and Ninja 2600;
Hunter, Bard and Dancer 2700; Swordman, Merchant, Knight, Crusader, Gunslinger,
Taekwon and Star Gladiator 2800; Blacksmith and Alchemist 3000. Transcendent
classes use their base class's value (`job_stats.yml`).

---

## 1. HP recovery

| AegisName | Name | Id | Effect (script) | Wt | Buy | Notes |
|---|---|---|---|---|---|---|
| `Red_Potion` | Red Potion | 501 | `itemheal rand(45,65),0` | 7 | 50 NPC | usable:92 |
| `Orange_Potion` | Orange Potion | 502 | `itemheal rand(105,145),0` | 10 | 200 NPC | |
| `Yellow_Potion` | Yellow Potion | 503 | `itemheal rand(175,235),0` | 13 | 550 NPC | |
| `White_Potion` | White Potion | 504 | `itemheal rand(325,405),0` | 15 | 1200 NPC | usable:116. Most tool dealers stock it. |
| `Red_Slim_Potion` | Condensed Red Potion | 545 | `itemheal rand(45,65),0` | **1** | 150 drop | Same heal as the normal potion, far lighter. Alchemists brew condensed potions. **Not NPC-sold.** |
| `Yellow_Slim_Potion` | Condensed Yellow Potion | 546 | `itemheal rand(175,235),0` | **2** | 600 drop | |
| `White_Slim_Potion` | Condensed White Potion | 547 | `itemheal rand(325,405),0` | **2** | 1650 drop | Same heal as White at **2/15 of the weight**: the single best change to a kit. |
| `Red_Herb` | Red Herb | 507 | `itemheal rand(18,28),0` | 3 | 18 drop | |
| `Yellow_Herb` | Yellow Herb | 508 | `itemheal rand(38,58),0` | 5 | 40 drop | |
| `White_Herb` | White Herb | 509 | `itemheal rand(75,115),0` | 7 | 120 drop | |
| `Leaflet_Of_Hinal` | Hinalle Leaflet | 520 | `itemheal rand(175,235),0` | **1** | 150 drop | A Yellow Potion at weight 1. Not on the engine's auto-drink list (§8), so it needs a rule. |
| `Leaflet_Of_Aloe` | Aloe Leaflet | 521 | `itemheal rand(325,405),0` | **2** | 360 drop | A White Potion at weight 2. Not auto-drunk. |
| `Fruit_Of_Mastela` | Mastela Fruit | 522 | `itemheal rand(400,600),0` | 3 | 8500 drop | The biggest flat heal per weight among common items. Not auto-drunk. |
| `Royal_Jelly` | Royal Jelly | 526 | `itemheal rand(325,405),rand(40,60)` + cures Poison, Silence, Blind, Confusion, Curse, Hallucination | 15 | 7000 drop | usable:329. White + Blue + Panacea in one. |
| `Yggdrasilberry` | Yggdrasil Berry | 607 | `percentheal 100,100` | 30 | 5000 drop | usable:1098. **Delay 5 s.** Full HP and SP, no VIT bonus. |
| `Seed_Of_Yggdrasil` | Yggdrasil Seed | 608 | `percentheal 50,50` | 30 | 5000 drop | usable:1111. **Delay 3 s.** |
| `Honey` | Honey | 518 | `itemheal rand(70,100),rand(20,40)` | 10 | 500 drop | |
| `Meat` | Meat | 517 | `itemheal rand(70,100),0` | 15 | 50 drop | Poor per weight. |
| `Piece_Of_Cake` | Piece of Cake | 539 | `itemheal rand(270,330),0` | 10 | 3000 drop | |
| `Pecopeco's_Feed` | PecoPeco Food | 541 | `itemheal rand(325,405),0` | 5 | 3000 drop | No job limit in the yml. |
| `Chocolate_Drink` | Chocolate Drink | 573 | as Royal Jelly, slightly more HP (330-410 / 45-65) | 15 | 7000 drop | |
| `Tomyumkung` | Tom Yum Goong | 566 | `itemheal rand(244,350),rand(10,30)` + the Panacea cures | 15 | 10000 drop | |
| `Elixir_Of_Life` | Elixir of Life | 12704 | `percentheal 100,0` | 1 | cash | Base level 85 or more. |
| `Siege_White_Potion` | WoE White Potion | 11503 | `itemheal rand(400,500),0` | 10 | cash | **NoTrade**. |
| `Enrich_White_PotionZ` | Concentrated White Potion Z | 12428 | `heal 1000,0` + a renewal status | 1 | cash | `heal`, not `itemheal`, so no VIT bonus. |

**What a White Potion heals** (the average of 325-405 is 365; the multiplier is
from `pc.cpp:10749`):

| Drinker | Bonus | HP per White |
|---|---|---|
| VIT 1, no skill | 102 % | ≈ 372 |
| VIT 30 | 160 % | ≈ 584 |
| VIT 60 | 220 % | ≈ 803 |
| Knight, VIT 50, Increase HP Recovery 10 | 300 % | ≈ 1095 |
| Alchemist, VIT 30, Learning Potion 10 | 210 % | ≈ 767 |

**Potion-boosting gear (pre-re db).**

| Bonus | Items |
|---|---|
| `bAddItemHealRate` (all healing items) | Sprint Mail +3, Vital Tree Shoes +5, Anubis Helm +10 (`item_db_equip.yml`) |
| `bAddItemGroupHealRate,IG_Potion,20` | Fricco's Shoes |
| +50 % on herbs | Hermit Plant (Wild Ginseng) Card |
| +50 % on juices | Galapago Card |
| +50 % on candy | Dumpling Child Card |
| +50 % on meat | Spring Rabbit Card |
| +50 % on fish | Sea-Otter Card |
| +100 % on single items | Lady Tanee Card on Banana, Hell Poodle Card on Meat, Snowier Card on Ice Cream (`item_db_etc.yml`) |

There is no "Rosary" potion bonus in pre-re.

**Aid Potion (Potion Pitcher, `AM_POTIONPITCHER`).** The Alchemist throws the
potion its level picks, and pays with that potion:

| Level | Potion |
|---|---|
| 1 | Red |
| 2 | Orange |
| 3 | Yellow |
| 4 | White |
| 5 | Blue (SP; players only) |

The heal is potion × (100 + 10·Aid Potion lv + 5·Learning Potion lv)% × (100 +
2·the **target's** VIT)% × the target's Increase HP Recovery. A level-5 Aid Potion
with a White Potion on a VIT-60 Knight is about 365 × 1.5 × 2.2 × 2.0 ≈ 2400 HP
(`skills/merchant/aidpotion.cpp:30-70`). Creators also have Aid Condensed Potion
(`CR_SLIMPITCHER`), which uses Condensed Red/Yellow.

---

## 2. SP recovery

| AegisName | Name | Id | Effect | Wt | Buy | SP per Wt |
|---|---|---|---|---|---|---|
| `Blue_Potion` | Blue Potion | 505 | `itemheal 0,rand(40,60)` | 15 | 5000 drop | 3.3 |
| `Grape_Juice` | Grape Juice | 533 | `itemheal 0,rand(15,25)` | 4 | 250 drop | **5.0** |
| `Blue_Herb` | Blue Herb | 510 | `itemheal 0,rand(15,30)` | 7 | 60 drop | 3.2 |
| `Grape` | Grape | 514 | `itemheal 0,rand(10,15)` | 2 | 200 drop | 6.3 |
| `Lemon` | Lemon | 568 | `itemheal 0,rand(10,20)` | 4 | 60 drop | 3.8 |
| `Strawberry` | Strawberry | 578 | `itemheal 0,rand(16,28)` | 2 | 200 drop | **11** |
| `Honey` | Honey | 518 | 70-100 HP, 20-40 SP | 10 | 500 drop | |
| `Royal_Jelly` | Royal Jelly | 526 | 325-405 HP, 40-60 SP, cures | 15 | 7000 drop | |
| `Yggdrasilberry` | Yggdrasil Berry | 607 | 100 % HP and SP | 30 | drop | 5 s delay |
| `Seed_Of_Yggdrasil` | Yggdrasil Seed | 608 | 50 % HP and SP | 30 | drop | 3 s delay |
| `Magical_Carnation` | Magic Carnation | 680 | `percentheal 0,20` | 100 | drop | Very heavy. |
| `Mora_Mandarin` | Mora Mandar | 11520 | `itemheal 0,rand(50,80)` | 2 | 500 drop | From a renewal-era map. Present in the pre-re db. |
| `Siege_Blue_Potion` | WoE Blue Potion | 11504 | `itemheal 0,rand(50,70)` | 10 | cash | **NoTrade**. |

The SP version of the formula: × (100 + 2·INT + 10·Increase SP Recovery lv + 5·Learning
Potion lv)%. A Wizard with INT 90 and Increase SP Recovery 10 gets 380 % from a Blue
Potion: about 190 SP.

**No pre-re NPC sells Blue Potions.** Only renewal shops do (`npc/re/merchants/`).
In the pre-re world they come from drops and player vendors.

---

## 3. Status cures

**Which item ends which status.** Every cell is from the item's `sc_end` lines.
The status token is the plan's `self_<status>` (see §8).

| Status (`self_…`) | Green Potion 506 | Green Herb 511 | Panacea 525 | Royal Jelly 526 | Holy Water 523 | Other |
|---|---|---|---|---|---|---|
| `poison` | ✔ | ✔ | ✔ | ✔ | | Cure Free 12475; the Panacea foods (566, 573, 583, 591-595) |
| `dpoison` (Deadly Poison) | | | | | | **none**: no item ends `SC_DPOISON` |
| `silence` | ✔ | | ✔ | ✔ | | Cure Free |
| `blind` | ✔ | | ✔ | ✔ | | |
| `confusion` | | | ✔ | ✔ | | |
| `curse` | | | ✔ | ✔ | ✔ | Cure Free; **Blessing Scroll** 12215: Blessing on a cursed player ends the Curse instead of buffing (`status.cpp:10705`) |
| `hallucination` | | | ✔ | ✔ | | |
| `bleeding` | | | | | | **Cure Free** 12475 only (`sc_end SC_BLEEDING`, cash/event). There is no NPC cure in pre-re. |
| `stone` / `stonewait` | | | | | | Items cannot be used once petrified (§0). During `stonewait` items work, but none ends it. Whether a Blessing Scroll used then stops it is **unverified**: Blessing ends `SC_STONE`, not `SC_STONEWAIT`. |
| `freeze`, `stun`, `sleep` | | | | | | **None.** No item can be used while they last. |
| `decreaseagi` | | | | | | Increase AGI ends it (`status.yml` Increaseagi `EndOnStart: Decreaseagi`): `Inc_Agi_10_Scroll` 12216 or `Guarana_Candy` 12414, both cash. A **Speed Potion** 12016 active beforehand makes Decrease AGI and Quagmire fail (`Fail: Speedup1`), but does not end them. |
| `quagmire` | | | | | | none |

The cure items:

| AegisName | Name | Id | Script | Wt | Buy |
|---|---|---|---|---|---|
| `Green_Potion` | Green Potion | 506 | `sc_end` Poison, Silence, Blind | 7 | 40 **NPC** |
| `Green_Herb` | Green Herb | 511 | `sc_end` Poison | 3 | 10 drop |
| `Panacea` | Panacea | 525 | `sc_end` Poison, Silence, Blind, Confusion, Curse, Hallucination | 10 | 500 drop (no pre-re shop) |
| `Royal_Jelly` | Royal Jelly | 526 | the Panacea cures + 325-405 HP + 40-60 SP | 15 | 7000 drop |
| `Holy_Water` | Holy Water | 523 | `sc_end` Curse. Also the catalyst for Aspersio, Basilica and the Aspersio Scroll. | 3 | 20. Made by an Acolyte with Aqua Benedicta. Not sold. |
| `Cure_Free` | Cure Free | 12475 | ends Silence, Bleeding, Poison, Curse, Orcish, Change Undead; `itemheal 500,0` | 5 | cash/event |
| `Blessing_10_Scroll` | LV10 Blessing Scroll | 12215 | `sc_start SC_BLESSING,240000,10`; ends Curse or Stone instead of buffing if present | 1 | cash, **NoTrade** |

---

## 4. Buffs

### 4a. Attack speed potions (they do not stack: the strongest one present counts)

`SC_ASPDPOTION0-3` reduce attack delay by `val2` = 50·(2+n) per mille, which is
**−10 / −15 / −20 / −25 %** (`status.cpp:11131-11135`, `:8476-8481`). Each lasts
30 min, except the Poison Bottle (1 min). Not removed by death.

| AegisName | Name | Id | Status | Wt | Buy | Jobs / level |
|---|---|---|---|---|---|---|
| `Center_Potion` | Concentration Potion | 645 | `aspdpotion0` (−10 %) | 10 | 800 **NPC** | all, any level (usable:1532) |
| `Awakening_Potion` | Awakening Potion | 656 | `aspdpotion1` (−15 %) | 15 | 1500 **NPC** | base ≥ 40; **not** Acolyte, Priest, Bard or Dancer (or their transcendents). Monk may. (usable:1542) |
| `Berserk_Potion` | Berserk Potion | 657 | `aspdpotion2` (−20 %) | 20 | 3000 **NPC** (Comodo, Lighthalzen) | base ≥ **85**; only Swordman, Knight, Crusader, Merchant, Blacksmith, Alchemist, Rogue, Mage, **Wizard**, Gunslinger, Taekwon, Star Gladiator, Soul Linker (and their transcendents). **Not** Sage, Archer, Hunter, Bard, Dancer, Thief, Assassin, Acolyte, Priest, Monk, Ninja or Novice. (usable:1576) |
| `Poison_Bottle` | Poison Bottle | 678 | Assassin Cross: Deadly Poison (`dpoison`) + `aspdpotion3` (−25 %) for 60 s. **Anyone else: `percentheal -100,-100`, which kills.** | 10 | 5000 drop | Also the catalyst for Enchant Deadly Poison (`ASC_EDP`). |
| `Guarana_Candy` | Guarana Candy | 12414 | `aspdpotion0` 30 min + Increase AGI lv5 (140 s) | 1 | cash | |
| `Light_Center_Pot` / `Light_Awakening_Pot` / `Light_Berserk_Pot` | Light potions | 14509-14511 | as 645 / 656 / 657 | 2 | cash | The yml sets no job limits on the light versions. |

The Mercenary versions (12xxx `M_*`) are for mercenaries only (`pc.cpp`
`pc_isUseitem`).

### 4b. Stat foods, ATK/MATK and HIT/FLEE

| AegisName | Name | Id | Effect | Wt | Buy |
|---|---|---|---|---|---|
| `Str_Dish01..10` | STR dishes | 12041-12045, 12071-12075 | `sc_start SC_STRFOOD,1200000,N` (+N STR for 20 min) + 5-20 % HP | 6-100 | 2k-100k, drop/cooked |
| `Int_Dish01..10` | INT dishes | 12046-12050, 12076-12080 | +N INT, 20 min, + some SP | | |
| `Vit_Dish01..10` | VIT dishes | 12051-12055, 12081-12085 | +N VIT, 20 min | | |
| `Agi_Dish01..10` | AGI dishes | 12056-12060, 12086-12090 | +N AGI, 20 min | | |
| `Dex_Dish01..10` | DEX dishes | 12061-12065, 12091-12095 | +N DEX, 20 min | | |
| `Luk_Dish01..10` | LUK dishes | 12066-12070, 12096-12100 | +N LUK, 20 min | | |
| `Str_Dish10_`, `Agi_Dish10_`, `Int_Dish10_` | cash +10 dishes | 12202-12204 (and others) | `SC_FOOD_*_CASH` +10, 30 min; it **replaces** the normal dish of that stat (`EndOnStart`) | 1 | cash, **NoTrade**, 60 s shared cash-food interval |
| `Box_Of_Grudge` | Box of Resentment | 12030 | `sc_start SC_ATKPOTION,60000,20`: +20 ATK, 60 s | 20 | 1000 drop |
| `Sleepy_Box` | Box of Drowsiness | 12031 | +20 MATK, 60 s | 20 | 1000 drop |
| `Realgar_Wine` | Distilled Fighting Spirit | 682 | +30 ATK, 60 s | 10 | drop |
| `Exorcize_Herb` | Herb of Incantation | 683 | +30 MATK, 60 s | 5 | drop |
| `Durian` | Durian | 684 | +10 ATK and +10 MATK, 60 s | 30 | 15000 drop |
| `Tasty_Colonel` / `Tasty_Major` | Pink / White Ration | 12269 / 12270 | +15 ATK / +15 MATK, 10 min | 7 | cash |
| `Rainbow_Cake` | Rainbow Cake | 12124 | +10 ATK and +10 MATK, 60 s | 7 | cash |
| `Sesame_Pastry` | Sesame Pastry | 12122 | +30 HIT, 30 min | 7 | cash |
| `Honey_Pastry` | Honey Pastry | 12123 | +30 FLEE, 30 min | 7 | cash |
| `Accuracy_30_Scroll` / `Flee_30_Scroll` | Concentration / Evasion Scroll | 14531 / 14530 | +30 HIT / +30 FLEE, 30 min | 1 | cash |
| `Tyr's_Blessing` | Tyr's Blessing | 14601 | +30 HIT, +30 FLEE, +20 ATK, +20 MATK, 5 min | 1 | cash |
| `Mental_Potion` | Mental Potion | 14600 | **its script is empty in the pre-re db**, so it does nothing | 1 | cash |

ATK and MATK potions do not stack with each other: `SC_ATKPOTION` is one status,
and the higher value wins (`OverlapIgnoreLevel`).

### 4c. Weapon element: converters, Sage catalysts, holy water, cursed water

| AegisName | Name | Id | Effect | Wt | Buy | Who |
|---|---|---|---|---|---|---|
| `Elemental_Fire` | Elemental Converter (Fire) | 12114 | `itemskill "ITEM_ENCHANTARMS",4`: **Fire** weapon, 3 min | 1 | drop | anyone (no `Jobs:`); usable:3649 |
| `Elemental_Water` | Elemental Converter (Water) | 12115 | `ITEM_ENCHANTARMS` 2: **Water**, 3 min | 1 | drop | anyone |
| `Elemental_Earth` | Elemental Converter (Earth) | 12116 | lv 3: **Earth**, 3 min | 1 | drop | anyone |
| `Elemental_Wind` | Elemental Converter (Wind) | 12117 | lv 5: **Wind**, 3 min | 1 | drop | anyone |
| `Water_Of_Darkness` | Cursed Water | 12020 | lv 8: **Shadow (Dark)**, 3 min | 3 | drop | anyone |
| `Box_Of_Storm` | Box of Storms | 12032 | lv 2: **Water**, 3 min (as rAthena has it) | 20 | drop | anyone |
| `Aspersio_5_Scroll` | LV5 Aspersio Scroll | 12217 | Holy weapon, 180 s, **only if a Holy Water is in the bag** (it uses one) | 1 | cash, **NoTrade** | anyone |
| `J_Aspersio_5_Scroll` | Sacred Scroll | 12928 | `itemskill "PR_ASPERSIO",5` | 1 | cash | anyone |
| `Tiny_Waterbottle` | Small Bottle | 12353 | `SC_WATERWEAPON` 90 s | 1 | 800 drop | anyone |

`ITEM_ENCHANTARMS` takes its element from the level (`skill_db.yml:13360-13381`),
so lv 2 is Water and lv 8 is Dark. The duration is 180 s.

**Which weapon element wins** (`battle.cpp:3468-3485`, `status.cpp:8836-`), from
strongest to weakest:
1. A **converter** (`SC_ENCHANTARMS`) beats everything.
2. An **elemental arrow or bullet** beats a Sage endow, but not a converter.
3. A **Sage endow** (Fire/Frost/Lightning/Seismic Weapon), Aspersio, or Enchant
   Poison.

A Hunter given Flame Launcher and then a Crystal Arrow therefore shoots Water.

A converter and Aspersio end each other. Sage endows end Aspersio, but do not end
a converter (`status.yml` `EndOnStart`). Every endow ends when the weapon is
unequipped. Endows are **not** `NoRemoveOnDead`, so they end on death.

Sage catalysts (etc items, consumed by the Sage's skill, 1 each):

| AegisName | Name | Id | Skill | Wt | Buy |
|---|---|---|---|---|---|
| `Boody_Red` | Red Blood | 990 | `SA_FLAMELAUNCHER` (Fire endow) | 5 | 1000 drop |
| `Crystal_Blue` | Crystal Blue | 991 | `SA_FROSTWEAPON` (Water) | 5 | 1000 drop |
| `Wind_Of_Verdure` | Wind of Verdure | 992 | `SA_LIGHTNINGLOADER` (Wind) | 5 | 1000 drop |
| `Yellow_Live` | Green Live | 993 | `SA_SEISMICWEAPON` (Earth) | 5 | 1000 drop |

Endow duration is 20 min at lv 1-4 and **30 min at lv 5**
(`skill_db.yml:7586-7596`). One catalyst per party member per 30 min, plus one
for each death, is all a fight uses.

### 4d. Elemental armour and resistance

| AegisName | Name | Id | Effect (`SC_ARMOR_ELEMENT_*`: water, earth, fire, wind) | Wt | Buy |
|---|---|---|---|---|---|
| `Resist_Fire` | Fireproof Potion | 12118 | **+20 % Fire** resist, −15 % Water, 20 min | 1 | drop |
| `Resist_Water` | Coldproof Potion | 12119 | **+20 % Water**, −15 % Wind, 20 min | 1 | drop |
| `Resist_Earth` | Earthproof Potion | 12120 | **+20 % Earth**, −15 % Fire, 20 min | 1 | drop |
| `Resist_Wind` | Thunderproof Potion | 12121 | **+20 % Wind**, −15 % Earth, 20 min | 1 | drop |
| `Undead_Element_Scroll` | Undead Elemental Scroll | 12279 | `SC_ARMOR_RESIST` +20 % to all four, 5 min | 1 | cash |
| `Holy_Element_Scroll` | Holy Elemental Scroll | 12280 | `SC_BENEDICTIO`: **Holy armour**, 5 min | 1 | cash |
| `Holy_Armor_S` | Holy Armor Scroll | 14540 | `SC_ELEMENTALCHANGE` Holy 1, 30 min | 1 | cash, **NoTrade** |
| `Shadow_Armor_S` | Shadow Armor Scroll | 14539 | Shadow armour 1, 30 min | 1 | cash, **NoTrade** |
| `GhostringS` | Ghostring Scroll | 14598 | the Ghostring Card's script (Ghost armour) for 60 s | 1 | cash, **NoTrade** |

The value order comes from `status.yml` `Armor_Element_Fire`: val1 = water, val2 =
earth, val3 = fire, val4 = wind. Remember §0: normal monster hits are Neutral,
so these help only against elemental skills.

### 4e. Other fight buffs

| AegisName | Name | Id | Effect | Wt | Buy |
|---|---|---|---|---|---|
| `Anodyne` | Anodyne | 605 | `itemskill "SM_ENDURE",1`: no flinch for 7 hits, +1 MDEF, 10 s | 10 | 2000 drop |
| `Aloebera` | Aloevera | 606 | `SM_SELFPROVOKE` 1: Provoke on self, **+5 % ATK, −10 % DEF**, 30 s (`status.cpp:11667`). Not while sitting. | 10 | 1500 drop |
| `Speed_Up_Potion` | Speed Potion | 12016 | `SC_SPEEDUP1` +50 % move speed, **5 s** | 10 | cash |
| `Box_Of_Thunder` | Box of Thunder | 12028 | `SC_SPEEDUP0` +25 % move speed, 20 s | 20 | 1000 drop |
| `Inspector_Certificate` | Authoritative Badge | 662 | `SC_SPEEDUP0` +25 % move speed, 180 s | 3 | 1450 drop |
| `Gloomy_Box` | Box of Gloom | 12029 | `AC_CONCENTRATION` 1: +3 % AGI/DEX, reveals hidden, 60 s | 20 | 1000 drop |
| `Box_Of_Sunlight` | Box of Sunlight | 12033 | `SC_INTRAVISION`: see hidden/cloaked, 30 s | 20 | 1000 drop |
| `Inc_Agi_10_Scroll` | LV10 Agil Scroll | 12216 | Increase AGI 10 (AGI +12, faster walk) for 240 s; costs 15 HP | 1 | cash, **NoTrade** |
| `Assumptio_5_Scroll` | LV5 Assumptio Scroll | 12218 | Assumptio 5, 100 s (ends Kyrie) | 1 | cash, **NoTrade** |
| `Wind_Walk_10_Scroll` | LV10 Wind Walker Scroll | 12219 | Wind Walk lv5 status, 250 s | 1 | cash, **NoTrade** |
| `Adrenaline_Scroll` | LV5 Adrenaline Scroll | 12220 | Adrenaline Rush 5, 150 s, **only with an axe or mace** in hand | 1 | cash, **NoTrade** |
| `Pty_Blessing_Scroll` / `Pty_Inc_Agi_Scroll` / `Pty_Assumptio_Scroll` | Party scrolls | 14588-14590 | `CASH_BLESSING` 10 / `CASH_INCAGI` 10 / `CASH_ASSUMPTIO` 5 on the party | 1 | cash, **NoTrade** |
| `Regeneration_Potion` | Regeneration Potion | 14537 | `SC_INCHEALRATE` +20 % to potion heals, 30 min (`pc.cpp:10771`) | 1 | cash, **NoTrade** |
| `Small_Life_Potion` / `Med_Life_Potion` | Life Potions | 14534 / 14535 | HP regeneration over 10 min | 1 | cash, **NoTrade** |
| `S_Def_Potion` / `B_Def_Potion` | Defense Potions | 14541 / 14542 | `SC_DEF_RATE` 3, 1 / 3 min | 1 | cash, **NoTrade** |
| `S_Mdef_Potion` / `B_Mdef_Potion` | Magic Defense Potions | 14543 / 14544 | `SC_MDEF_RATE` 3, 1 / 3 min | 1 | cash, **NoTrade** |

**Pre-re has no Kyrie Eleison scroll.** The `Box_Of_*` debuff boxes (Giggling Box
12027, Box of Panting 12034) curse or silence the **user**.

### 4f. Magic scrolls (cast a skill with the user's own stats)

`itemskill` makes the user cast the skill, at its normal cast time, using the
user's MATK. The engine aims a harmful one at the rule's monster, and a helpful
one at the rule's target or at itself (`population_strategy.cpp` `use_item`).

| AegisName | Name | Id | Skill | Wt | Buy |
|---|---|---|---|---|---|
| `Fire_Scroll_1_3` / `_1_5` | Fire Bolt 3 / 5 | 690 / 691 | `MG_FIREBOLT` | 1 | 1000 / 2000 drop |
| `Cold_Scroll_1_3` / `_1_5` | Cold Bolt 3 / 5 | 688 / 689 | `MG_COLDBOLT` | 1 | drop |
| `Wind_Scroll_1_3` / `_1_5` | Lightning Bolt 3 / 5 | 692 / 693 | `MG_LIGHTNINGBOLT` | 1 | drop |
| `Earth_Scroll_1_3` / `_1_5` | Earth Spike 3 / 5 | 686 / 687 | `WZ_EARTHSPIKE` | 1 | drop |
| `Ghost_Scroll_1_3` / `_1_5` | Soul Strike 3 / 5 | 694 / 695 | `MG_SOULSTRIKE` | 1 | drop |
| `Fire_Scroll_2_1` / `_2_5` | Fire Ball 1 / 5 | 696 / 697 | `MG_FIREBALL` | 1 | drop |
| `Fire_Scroll_3_1` / `_3_5` | Fire Wall 1 / 5 | 698 / 699 | `MG_FIREWALL` | 1 | drop |
| `Cold_Scroll_2_1` / `Cold_Scroll_2_5` | Frost Diver 1 / 5 | 700 / 12000 | `MG_FROSTDIVER` | 1 | drop |
| `Holy_Scroll_1_3` / `_1_5` | Heal 3 / 5 | 12001 / 12002 | `AL_HEAL`: give it `Target: ally_lowest_hp` | 1 | 2000 drop |
| `Holy_Scroll_2_1` | Teleport 1 | 12003 | `AL_TELEPORT` 1 (random warp) | 1 | 1000 drop |
| `Lex_Aeterna_Scroll` | Lex Aeterna | 14515 | `PR_LEXAETERNA` | 1 | cash |
| `Magnificat_5_Scroll` | Magnificat 5 | 14516 | `PR_MAGNIFICAT` | 1 | cash |
| `Meteor_10_Scroll` / `Storm_10_Scroll` / `Vermilion_10_Scroll` | Meteor Storm / Storm Gust / Lord of Vermilion 10 | 14512-14514 | the Wizard spells | 1 | cash |
| `Quagmire_Scroll` | Quagmire 5 | 14594 | `WZ_QUAGMIRE` | 1 | cash, **NoTrade** |
| `Magic_Power_Scroll` | Mystical Amplification 10 | 14593 | `HW_MAGICPOWER` | 1 | cash, **NoTrade** |
| `CP_Weapon_Scroll` (…`Helm`/`Shield`/`Armor`) | Chemical Protection 5 | 14517-14520 | `AM_CP_*` on self | 1 | cash |
| `Wurst` / `Event_Cake` | Brusti / X-mas Cake | 585 / 12200 | Magnificat 3 (+ a small heal) | 4 / 5 | drop / event |
| `Choco_Tart` | Chocolate Tart | 12236 | 5 % HP + Angelus 5 | 10 | event |

---

## 5. Revive and escape

| AegisName | Name | Id | Effect | Wt | Buy | For a companion |
|---|---|---|---|---|---|---|
| `Leaf_Of_Yggdrasil` | Yggdrasil Leaf | 610 | `itemskill "ALL_RESURRECTION",1`: revives with 10 % HP. **No Blue Gemstone needed** (itemskill skips costs). | 10 | 4000 **NPC** in rAthena (Aldebaran, Rachel, Veins, Umbala, Lighthalzen, Brasilis and Lutie tool dealers, `merchants/shops.txt:62,81,176,193,265,278,287`) | A companion's `UseItem: Leaf_Of_Yggdrasil` with `Target: dead_ally` (or `{ Ally: dead }`) casts it on that ally, because Resurrection is a support skill (`use_item`). **Unverified in game.** A dead companion cannot use one itself. |
| `Wing_Of_Fly` | Fly Wing | 601 | `itemskill "AL_TELEPORT",1`: a **random cell on the same map**, with no menu (`skills/acolyte/teleport.cpp:30-33`). Refused on `noteleport` maps, which include many MVP maps. | 5 | 60 NPC | Takes the companion out of the fight. Its follow logic brings it back once the owner is out of sight (reference.md). |
| `Wing_Of_Butterfly` | Butterfly Wing | 602 | `AL_TELEPORT` 3: to the **user's save point**. Refused on `noreturn` maps. | 5 | 300 NPC | Sends the companion to *its own* save point. How it rejoins is **unverified**; avoid it in plans. |
| `Spectacles` | Magnifier | 611 | `MC_IDENTIFY`: identifies an item | 5 | 40 NPC | Useless in a fight. |
| `Holy_Egg` | Holy Egg | 12019 | `ALL_RESURRECTION` 2 | 15 | drop | as the Leaf |
| `Giant_Fly_Wing` | Giant Fly Wing | 12212 | the party leader calls the party | 1 | cash | leader only |

Gemstone revives: the Priest's Resurrection costs 1 `Blue_Gemstone` for the
skill (`skill_db.yml` `ALL_RESURRECTION`). With Companion inventory on, a Priest
with no gem cannot revive (COMPANIONS.md "Death and resurrection").

---

## 6. Ammunition and catalysts

### 6a. Arrows (Archer, Hunter, Bard, Dancer, and Rogue/Thief/Assassin with a bow)

The arrow's ATK is added to the bow's in pre-re. Its element replaces the bow's
for shots and arrow skills (§4c). `etc` lines 2093-2520.

| AegisName | Name | Id | ATK | Element / effect | Wt | Buy |
|---|---|---|---|---|---|---|
| `Arrow` | Arrow | 1750 | 25 | Neutral | 0.1 | 1 NPC (every tool dealer) |
| `Iron_Arrow` | Iron Arrow | 1770 | 30 | Neutral | 0.1 | 2 NPC (Amatsu, Ayothaya, Comodo, Gonryun, Louyang, Lighthalzen) |
| `Steel_Arrow` | Steel Arrow | 1753 | 40 | Neutral | 0.2 | 4 drop |
| `Oridecon_Arrow` | Oridecon Arrow | 1765 | **50** | Neutral | 0.3 | 30 drop |
| `Silver_Arrow` | Silver Arrow | 1751 | 30 | **Holy** | 0.2 | 3 NPC (Alberta, Einbroch, Lighthalzen, weapon dealers) |
| `Holy_Arrow` | Holy Arrow | 1772 | 50 | Holy, +5 % vs Demon | 0.2 | 3 drop |
| `Arrow_Of_Counter_Evil` | Arrow of Counter Evil | 1766 | 50 | Holy | 0.3 | 40 drop |
| `Fire_Arrow` | Fire Arrow | 1752 | 30 | **Fire** | 0.2 | 3 NPC (Alberta, Einbroch, Lighthalzen) |
| `Crystal_Arrow` | Crystal Arrow | 1754 | 30 | **Water** | 0.2 | 3 drop/craft |
| `Arrow_Of_Wind` | Arrow of Wind | 1755 | 30 | **Wind** | 0.2 | 3 drop/craft |
| `Stone_Arrow` | Stone Arrow | 1756 | 30 | **Earth** | 0.2 | 3 drop/craft |
| `Immatrial_Arrow` | Immaterial Arrow | 1757 | 30 | **Ghost** | 0.1 | 3 drop/craft |
| `Arrow_Of_Shadow` | Arrow of Shadow | 1767 | 30 | **Shadow** | 0.2 | 3 drop/craft |
| `Rusty_Arrow` | Rusty Arrow | 1762 | 30 | **Poison** | 0.2 | 3 drop/craft |
| `Poison_Arrow` | Poison Arrow | 1763 | 1 | Poison, 20 % poison chance | 0.3 | 10 |
| `Incisive_Arrow` | Sharp Arrow | 1764 | 10 | +20 crit | 0.3 | 20 |
| `Stun_Arrow` / `Freezing_Arrow` / `Flash_Arrow` / `Curse_Arrow` / `Sleep_Arrow` / `Silence_Arrow` | status arrows | 1758-1761, 1768, 1769 | 1 | 10-20 % chance of Stun / Freeze (Water) / Blind / Curse / Sleep / Silence | 0.3 | 10 |

Arrow Crafting (`AC_MAKINGARROW`) turns items into elemental arrows. The quivers
(12004-12015, 500 arrows each) are cash.

### 6b. Gunslinger and Ninja ammunition

| AegisName | Name | Id | ATK | Element / effect | Wt | Buy | Limit |
|---|---|---|---|---|---|---|---|
| `Bullet` | Bullet | 13200 | 10 | Neutral | **0.2** | 1 NPC (Alberta and Izlude traders, the Gunslinger guild) | Gunslinger |
| `Silver_Bullet` | Silver Bullet | 13201 | 15 | **Holy** | 0.2 | 15 NPC | Gunslinger |
| `Shell_Of_Blood` | Bloody Shell | 13202 | 30 | Neutral, 1 % Bleeding | 0.2 | 30 NPC | Gunslinger |
| `Flare_Sphere` … `Freezing_Sphere` | spheres | 13203-13207 | 50 | Fire / Wind / Poison / Shadow (+Blind) / Water | 0.5 | 80 drop | Grenade Launcher |
| `Shuriken` | Shuriken | 13250 | 10 | | 0.5 | 4 NPC (Ninja Guild, `que_ng`) | Ninja |
| `Nimbus_Shuriken` | Nimbus Shuriken | 13251 | 30 | | 0.5 | 10 NPC | base ≥ 20 |
| `Flash_Shuriken` | Flash Shuriken | 13252 | 45 | | 0.5 | 20 NPC | base ≥ 40 |
| `Sharp_Leaf_Shuriken` | Sharp Leaf Shuriken | 13253 | 70 | | 0.5 | 40 NPC | base ≥ 60 |
| `Thorn_Needle_Shuriken` | Thorn Needle Shuriken | 13254 | 100 | | 0.5 | 100 NPC | base ≥ 80 |
| `Kunai_Of_Icicle` / `_Black_Soil` / `_Furious_Wind` / `_Fierce_Flame` / `_Deadly_Poison` | kunai | 13255-13259 | 30 | Water / Earth / Wind / Fire / Poison | **2** | 10 drop | Ninja (`NJ_KUNAI`) |
| `Venom_Knife` | Venom Knife | 1771 | 30 | | 0.5 | 50 | Assassin (`AS_VENOMKNIFE`) |

Bullets per cast (`skill_db.yml` `AmmoAmount`):

| Skill | Bullets |
|---|---|
| Rapid Shower | 5 |
| Spread Attack | 5 |
| Desperado | **10** |
| Tracking, Piercing Shot, Disarm, Dust, Triple Action, Bull's Eye, Cracker | 1 |
| Ground Drift | 1 grenade |
| Full Buster | 1 (no `AmmoAmount` in the yml, so the default of 1; **unverified**) |

### 6c. Gemstones and skill catalysts

| AegisName | Name | Id | Wt | Buy | Used by (pre-re `skill_db.yml` `ItemCost`) |
|---|---|---|---|---|---|
| `Blue_Gemstone` | Blue Gemstone | 717 | 3 | 600 **NPC** (Geffen, Juno, Veins and Hugel magic shops) | Safety Wall, Warp Portal, **Sanctuary**, **Magnus Exorcismus**, **Resurrection**, Fire Pillar lv 6-10, Land Protector, Gravitation Field, Basilica |
| `Yellow_Gemstone` | Yellow Gemstone | 715 | 3 | 600 drop (no pre-re shop) | Volcano, Deluge, Violent Gale, Land Protector, **Dispell**, Abracadabra (2), Ganbantein, Basilica |
| `Red_Gemstone` | Red Gemstone | 716 | 3 | 600 drop (no pre-re shop) | Stone Curse, Venom Dust, Venom Splasher, Graffiti, Basilica |
| `Holy_Water` | Holy Water | 523 | 3 | made | Aspersio, Basilica, Aspersio Scroll |
| `Booby_Trap` | Trap | 1065 | 1 | 100 NPC | every Hunter trap: 1 each, **Shockwave and Claymore 2** |
| `Fire_Bottle` | Bottle Grenade | 7135 | 1 | brewed | Demonstration; Acid Demonstration (with an Acid Bottle) |
| `Acid_Bottle` | Acid Bottle | 7136 | 1 | brewed | Acid Terror; Acid Demonstration |
| `MenEater_Plant_Bottle` | Plant Bottle | 7137 | 1 | brewed | Bio Cannibalize |
| `Mini_Bottle` | Marine Sphere Bottle | 7138 | 1 | brewed | Sphere Mine |
| `Coating_Bottle` | Glistening Coat | 7139 | 1 | brewed | Chemical Protection ×4, Full Chemical Protection |
| `Poison_Bottle` | Poison Bottle | 678 | 10 | drop | Enchant Deadly Poison |
| `Spiderweb` | Cobweb | 1025 | 1 | drop | Spider Web (Professor) |
| `Flame_Stone` / `Ice_Stone` / `Wind_Stone` | ninja stones | 7521-7523 | 1 | 150 NPC (Ninja Guild) | Flaming Petals and Blaze Shield / Watery Evasion and Freezing Spear / Lightning Spear and Wind Blade |
| `Shadow_Orb` | Shadow Orb | 7524 | 2 | 300 NPC | Mirror Image |
| `Berserk_Potion` | Berserk Potion | 657 | 20 | NPC | Aid Berserk Potion |
| Red/Orange/Yellow/White/Blue Potion | | 501-505 | | | Aid Potion lv 1-5 |
| `Red_Slim_Potion` / `Yellow_Slim_Potion` | | 545 / 546 | | | Aid Condensed Potion |

There are no spirit-sphere items in pre-re.

---

## 7. A boss kit per job

**What the rig gives now** (`harness/rwparty.py` `KIT_ALL` + `KITS`), with the
weight it comes to:

| Who | Kit | Kit Wt |
|---|---|---|
| everyone | White_Potion 50 (750), Blue_Potion 20 (300), Green_Potion 20 (140), Panacea 10 (100) | **1290** |
| Priest | + Blue_Gemstone 100 (300) | 1590 |
| Wizard | + Blue_Gemstone 20 (60) | 1350 |
| Sage | + Blue/Yellow Gemstone 30+30 (180), Yellow_Live 30 + Boody_Red 30 + Crystal_Blue 15 + Wind_Of_Verdure 15 (450) | 1920 |
| Hunter | + Arrow 3000 (300), Silver_Arrow 1000 (200), Fire_Arrow 1000 (200), Booby_Trap 100 (100) | **2090** |
| Bard, Dancer | + Arrow 2000 (200) | 1490 |
| Gunslinger | + Bullet 3000 (**600**), Silver_Bullet 1000 (200) | **2090** |

**Against the limits** (§0). These figures leave out gear: the rig's Arbalest
weighs 100, a Claymore 250, an Arc Wand 40, a Muffler 40.

| Job | Max Wt at STR 1 / 30 | 50 % (regen stops) | 90 % (no attacks) | Rig kit | Kit as a share of max |
|---|---|---|---|---|---|
| Wizard | 2430 / 3300 | 1215 / 1650 | 2187 / 2970 | 1350 | **56 %** at STR 1: no natural SP regen |
| Priest | 2630 / 3500 | 1315 / 1750 | 2367 / 3150 | 1590 | **60 %**: no Meditatio regen |
| Sage | 2430 / 3300 | 1215 / 1650 | 2187 / 2970 | 1920 | **79 %** |
| Hunter | 2730 / 3600 | 1365 / 1800 | 2457 / 3240 | 2090 | **77 %**; with bow and armour about 85-90 % → attacks stop |
| Gunslinger | 2830 / 3700 | 1415 / 1850 | 2547 / 3330 | 2090 | 74 % |
| Knight | 2830 (STR 1); typically 4500+ at 60+ STR | | | 1290 | fine |

So the Hunter top-up failing on weight is expected: the kit alone is 77 % of a
low-STR Hunter's limit. Worse, every caster in the reference party is past 50 %
**before** the fight, so none of them regenerates SP on its own.

**Suggested kits** (base 80-99, a 10-15 min MVP fight):

| Job | Suggested kit | Wt | Why |
|---|---|---|---|
| **everyone (base)** | `White_Slim_Potion` 40 if you have them (80), else `White_Potion` 25 (375); `Green_Potion` 10 (70); `Panacea` 3 (30), or `Holy_Water` 5 (15) against a curser; `Yggdrasilberry` 1-2 for tank and healer (30-60) | 150-500 | Condensed Whites heal the same at 2/15 of the weight. 20 Green Potions is more than a fight uses; carry what the boss inflicts (§3). |
| Knight / Lord Knight / Crusader / Paladin (tank) | White 50 (750) **or** Condensed 50 (100); `Berserk_Potion` 1 (base ≥ 85) or `Awakening_Potion` 1; Ygg Berry 3; a converter set for the boss (4 × 1 Wt) | 800-1000 | High STR and a Peco carry it. Increase HP Recovery makes each White about 1100 HP. A Frenzied LK cannot drink (§0), so put the potion rule **before** Frenzy. |
| Priest / High Priest | `Blue_Gemstone` 60-80 (180-240); `Blue_Potion` 15 (225); White 10 (150) or Condensed 15 (30); `Holy_Water` 10 (30) | 600-650 | **Add Holy Water**: the rig gives none, so Aspersio (`PR_ASPERSIO` costs 1) can never be cast with Companion inventory on. Stay under 50 % so Meditatio and natural SP regen work. Gems: Resurrection, Sanctuary and Magnus each cost 1. |
| Wizard / High Wizard | `Blue_Gemstone` 20 (60); `Blue_Potion` 25 (375), or `Grape_Juice` 60 (240) for the same SP at less weight; White 10 (150); `Green_Potion` 10 (70) | ≈ 650 | Under 50 % at STR 1. Silence is a caster's real threat: Green Potion first. |
| Sage / Professor | `Yellow_Gemstone` 30 (90); `Blue_Gemstone` 10 (30, Land Protector); 5 of each **needed** catalyst (25 each); Blue 20 (300); White 10 (150); Green 10 (70) | ≈ 700 | An endow lasts 30 min at lv 5, so 30 catalysts is a day's supply, not a fight's. Carry the element the boss is weak to. |
| Hunter / Sniper | **one** elemental arrow the boss is weak to × 1500 (300) + `Arrow` or `Iron_Arrow` 1000 (100); `Booby_Trap` 40 (40); `Awakening_Potion` 1 (Berserk is not allowed for Hunters); White 15 (225) | ≈ 700 | Arrows run fast, but elemental ones weigh 0.2. Three kinds is 700 Wt, and only one is used per boss. Traps: Ankle Snare and Claymore are what a fight uses (Claymore costs 2). |
| Bard / Dancer / Clown / Gypsy | Arrow 1000 (100); `Center_Potion` 1 (Awakening is **not** allowed for them) | ≈ 120 + base | |
| Gunslinger | the boss's element × 1500 (Silver for Undead/Shadow; 300) + `Bullet` 1000 (200); `Awakening_Potion` or `Berserk_Potion` (base ≥ 85: Gunslinger may) | ≈ 550 + base | Bullets weigh 0.2, so 3000 plain is 600 Wt. Desperado burns 10 a cast. |
| Assassin / Assassin Cross | `Awakening_Potion` (Berserk not allowed); Assassin Cross: `Poison_Bottle` 5-10 (EDP and the −25 % ASPD; **deadly to anyone else**); `Red_Gemstone` for Venom Splasher/Dust | small | Plans must never give a Poison Bottle rule to a non-Assassin-Cross. |
| Alchemist / Creator | `Fire_Bottle` + `Acid_Bottle` 30 each for Acid Demonstration (60); `Coating_Bottle` 4-8; the potions it throws (Aid Potion uses them from the bag) | small | |
| Ninja | `Thorn_Needle_Shuriken` 300 (150, base ≥ 80); `Flame_Stone`/`Ice_Stone`/`Wind_Stone` 20 of the one needed (20); `Shadow_Orb` 10 (20); kunai only if Throw Kunai is used (2 Wt each) | ≈ 200 | |
| Monk / Champion | `Awakening_Potion`; Blue 20 for Asura | | Berserk is not allowed. |

Notes on the counts: `itemuse.py`'s record says 30 White, 10 Blue and 40 Blue
Gemstones ran dry within 9 minutes of Mistress for a level-80 Knight and Priest.
For a 15-minute fight, plan on about 4 Whites a minute for the tank and 4 gems a
minute for the Priest.

---

## 8. Notes for plans

### What the engine already does without a plan

COMPANIONS.md "Its bag", and `population_engine.cpp:2363-2420` and
`population_shell_inventory.cpp:34-38`:

- **HP below 40 %** (`POP_POTION_HP_PCT`): it drinks its **level's potion first**
  (Red below level 30, Orange 30-54, Yellow 55-79, White 80+). Without that one,
  it drinks the strongest it carries, in this order: `White_Slim_Potion`,
  `Yellow_Slim_Potion`, `Red_Slim_Potion`, `White_Potion`, `Yellow_Potion`,
  `Orange_Potion`, `Red_Potion`, `White_Herb`, `Yellow_Herb`, `Red_Herb`.
- **SP below 20 %**: Blue Potion at 55+ (Grape Juice below), then `Blue_Potion`,
  `Grape_Juice`, `Blue_Herb`.
- At most one potion a second. Never while sitting. Only "while it is needed".
  Out of a fight it rests instead.
- So **a plan need not** drink the potions on those two lists at those
  thresholds. It needs a rule for anything else: cures, Yggdrasil items, Royal
  Jelly, Mastela, the leaflets, ASPD potions, converters, scrolls, Yggdrasil Leaf.
  It also needs one to drink **earlier** than 40 %, e.g. a tank at 60 %.
- A level-80+ companion carrying both White and Condensed White drinks the
  White first, because its level potion comes before the fallbacks.

### Conditions to pair with items

A status token is the SC name, lowercase, without `SC_`. `not_` inverts it.

| Item | `When:` | Note |
|---|---|---|
| `Green_Potion` | `self_poison`, `self_silence`, `self_blind` | Give each cure its own rule, or a list whose every member cures the status in the `When`. |
| `Panacea` | `self_confusion`, `self_hallucination`, `self_curse` (also poison, silence, blind) | |
| `Holy_Water` | `self_curse` | the cheapest curse cure |
| `Royal_Jelly` | `{ OR: [self_poison, self_silence, self_curse, self_confusion] }` with `self_hp_pct_lt60` | |
| `Green_Herb` | `self_poison` | |
| `Cure_Free` | `self_bleeding` | |
| `Yggdrasilberry` | `self_hp_pct_lt25` (+ a `Cooldown`, or rely on its 5 s delay) | Not auto-drunk. |
| `Fruit_Of_Mastela`, `Leaflet_Of_Aloe` | `self_hp_pct_lt50` | Not auto-drunk. |
| `Awakening_Potion` | `[not_self_aspdpotion1, not_self_aspdpotion2]` | Don't drink Awakening over an active Berserk. |
| `Berserk_Potion` | `not_self_aspdpotion2` | |
| `Center_Potion` | `[not_self_aspdpotion0, not_self_aspdpotion1, not_self_aspdpotion2]` | |
| `Elemental_Wind` etc. | `not_self_enchantarms` + `Enemy: { Element: Water }` | Also needs `Enemy` for the right element. A converter ends Aspersio. |
| `Resist_Fire` etc. | `not_self_armor_element_fire` | Only against fire **skills** (§0). |
| `Anodyne` | `[not_self_endure, self_targeted]` | |
| `Aloebera` | `not_self_provoke` | Costs DEF: not for a tank. |
| `Box_Of_Grudge` / `Sleepy_Box` | `not_self_atkpotion` / `not_self_matkpotion` | 60 s only: pair with `Enemy: { Boss: true }`. |
| `Str_Dish05` etc. | `not_self_strfood` | Lasts 20 min. Survives death? **unverified** (no `NoRemoveOnDead` flag, so probably not). |
| `Blessing_10_Scroll` | `self_curse` (it cures instead of buffing) or `not_self_blessing` | NoTrade. |
| `Inc_Agi_10_Scroll` | `self_decreaseagi` or `not_self_increaseagi` | NoTrade, costs 15 HP. |
| `Leaf_Of_Yggdrasil` | `Target: dead_ally` / `Present: { Ally: dead, Range: 9 }` | Range as Resurrection. Unverified in game. |
| `Poison_Bottle` | `Requires` the job to be Assassin Cross, + `not_self_aspdpotion3` | Kills anyone else. |

### Pitfalls

- **A list is a preference, not a match.** `UseItem: [Panacea, Green_Potion]`
  with `When: { OR: [self_curse, …] }` drinks a Green Potion against a curse once
  the Panaceas are gone, and keeps doing so every second. That is what
  `mvp-leak.party.yml:34-35` does. Write the curse case as its own rule:
  `self_curse` → `[Holy_Water, Panacea]`.
- **Stun, freeze, sleep and stone cannot be answered with an item.** Plan to
  prevent them instead: Marc Card, Stalactic Golem Card, `Equip:`, or standing
  off.
- **Frenzy (`SC_BERSERK`) forbids items.** A Lord Knight plan that Frenzies
  must drink before it, and can't heal itself after.
- **Job limits are silent.** A Berserk Potion rule on a Sage or a Hunter, or an
  Awakening Potion rule on a Priest or Bard, never fires. A Poison Bottle on
  anyone but an Assassin Cross **kills** them (usable:1730).
- **NoTrade items can't be handed over.** Most cash scrolls (Blessing, AGI,
  Aspersio, Assumptio, Wind Walk, Adrenaline, Quagmire, the Life and Def potions,
  Ghostring Scroll) cannot reach a companion by trade. Only the rig's `stock`
  script can give them.
- **Weight decides more than counts.** Past 50 %, no natural regen. Past 90 %,
  no attacks or skills. And an item that would push the carrier over 100 % is
  refused. Use `On: weight_above` (reference.md Events) to watch it.
- **Delayconsume items fail while sitting or casting.** The engine stands the
  companion up before a rule acts. A rule that fires during a cast simply
  passes.
- The engine's auto-drink and a plan rule both go through `pc_useitem`. Together
  they can drink two items in one second; the 100 ms server interval is the only
  limit between them.

### Unverified / to test

- A companion's Yggdrasil Leaf on a dead companion or player (the code path says
  yes).
- Butterfly Wing on a companion: where it goes and how it comes back.
- Item skills under Silence.
- Whether `SC_STONEWAIT` can be stopped by an item.
- Box of Storms giving Water: that is the rAthena db value, not checked against
  official data.
- Whether a +N stat dish ends on death.
