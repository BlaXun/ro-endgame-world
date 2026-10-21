# Pre-renewal character builds: reference for monster balancing

This is a reference of the PvE builds that pre-renewal (classic) Ragnarok Online
players commonly run at base level 99, and what each one is good or bad against.
It is meant for tuning monsters for companions that are given one of these
builds. It covers the transcendent second classes plus Star Gladiator, Soul
Linker, Ninja and Gunslinger. Renewal and third classes are out of scope.

How to read it:

- **Stats** are the ranges the sources give at 99. Many sources quote *final*
  values (base + job bonus + gear + buffs), which is why some exceed 99. "9x"
  means "some value in the nineties", as the sources write it.
- **Skills** use rAthena AegisNames from `db/pre-re/skill_db.yml` in the fork.
  Every name below was checked against that file. iRO uses different English
  names from the original ones; both are given where they differ (for example
  Guillotine Fist / Asura Strike = `MO_EXTREMITYFIST`).
- **Hit/DEF notes** marked "(rAthena)" come from the skill's `DamageFlags` in
  the pre-re `skill_db.yml`, not from a guide. They describe how this server
  computes the skill, which matters more for balancing than wiki wording.
- **Confidence.** iRO Wiki Classic was the main source. Most of its class pages
  were last edited in 2010–2013, several are flagged "needs expert attention",
  and some cite iRO-only items (Valkyrja's Shield, Medal of Honor, Brave/BG
  weapons) that a plain rAthena pre-re server may not have. A build marked
  **[community, unconfirmed]** is well known in the player community but was not
  found in a fetched source during this research. A build marked **[one source]**
  appeared in only one source.

---

## Party setups

Pre-renewal party guides that name exact compositions were hard to find; most
web results were renewal or other Ragnarok games. What the fetched sources say:

| Setup | What it relies on | Source |
|---|---|---|
| Puller + AoE damage + support (generic) | One character gathers a mob, an AoE class kills it, a Priest keeps everyone alive. The general shape behind most of the setups below. | General leveling guide (renewal-era blog); also implied by iRO Wiki Classic leveling spots ("Sacrifice [Paladin]: partying, generally as a puller"). |
| Priest + Grand Cross Crusader/Paladin (Sphinx 4F, undead/demon areas) | Turn Undead and Grand Cross on Anubis-type undead; the Priest heals the Paladin's self-damage. "Turn Undead highly suggested, Grand Cross Crusader highly suggested." | iRO Wiki Classic, Leveling Spots |
| High Priest tank + Minstrel/Gypsy (Thor's Volcano, Kasa) | Arrow Vulcan with Crystal arrows, the High Priest uses Lex Aeterna and buffs. "Of course have a high priest tank to Lex Aeterna and buffs." | iRO Wiki Classic, Leveling Spots |
| Two Bard/Dancer couples (Juperos ruins) | "Usually a party needs two couples to raid the place": ensembles plus Gypsy's Kiss/Magic Strings and Mental Sensing (EXP song). | iRO Wiki Classic, Leveling Spots |
| Hunter/Sniper + INT Priest (Turtle Island) | Party splits EXP; the Priest supports and Lex/heals. | iRO Wiki Classic, Leveling Spots |
| Creator (Acid Demonstration) + High Priest (Thor's Volcano, Biolab 3) | Acid Demonstration ignores DEF and FLEE; the Priest's Lex Aeterna doubles it, so fewer bombs are spent. Sword Guardians in Thor's 3 named as an easy target. | iRO Wiki Classic, Creator (Biochemist) page |
| Asura Champion + High Priest with Lex Aeterna (MVP) | One Lex-doubled Asura Strike kills MVPs below roughly 300–400k HP. | iRO Wiki Classic, Champion page |
| Professor (Hindsight) + Soul Linker | The Hindsight build needs a constant Sage Spirit link. | iRO Wiki Classic, Professor (Scholar) page |
| Star Gladiator + Soul Linker | Star Gladiator Spirit removes the HP drain of Union (`SG_FUSION`). The pairing is standard but the fetched SG page only describes Union, not the link. **[community, unconfirmed]** | iRO Wiki Classic, Star Gladiator page (Union); link pairing from general knowledge |
| Stalker (DEX/INT caster) as Wizard substitute (Biolab 3) | Plagiarized Storm Gust; "can replace a Wizard in parties or in Biolabs Level 3." | iRO Wiki Classic, Stalker page |
| "LK / HP / HW / Sniper" core, Champion + HP duo, Soul Change Professor feeding an Asura Champion, Gospel Paladin in Biolab/Thanatos | Widely described in forums and on servers, but no fetched source described any of these as a setup. Treat as **[community, unconfirmed]**. Thanatos Tower and Biolab 3 are listed as "Party" spots for 70–99 and 95–99 on iRO Wiki Classic, without a composition. | — |

---

## Lord Knight

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Bowling Bash / "SVD" LK | STR 85–95, AGI 1–25, VIT ~100 (final), DEX 60–70, INT/LUK 1 | `KN_BOWLINGBASH`, `KN_TWOHANDQUICKEN`, `LK_AURABLADE`, `LK_CONCENTRATION` (Spear Dynamo), `SM_PROVOKE` | Two-handed sword or spear; status-element weapon in WoE | Melee AoE damage, off-tank |
| Spear / Brandish LK | STR/VIT/DEX as above | `KN_BRANDISHSPEAR` (frontal AoE, needs Peco + spear), `KN_PIERCE`, `KN_SPEARBOOMERANG` | Spear (Pike, Hunting Spear, Cardo/Brionac/Halberd for two-hand) | Melee AoE, packs |
| Pierce / Clashing Spiral MVP LK | STR-heavy, DEX for hit | `KN_PIERCE` + `LK_CONCENTRATION` (+50 HIT, +25% dmg per iRO Wiki), `LK_SPIRALPIERCE` | Heaviest spear available (Spiral damage scales with weapon weight) | Single-target damage |
| ASPD / Frenzy LK | STR 100–110, AGI 80–100+, VIT 40–60, DEX 40–60 | `KN_TWOHANDQUICKEN`, `LK_PARRYING`, `LK_BERSERK` (Frenzy) | Two-handed sword | Single-target auto-attack |

- **Bowling Bash LK.** The standard leveling build on iRO Wiki Classic, with
  very high HP (25k+ claimed with WoE gear). Bowling Bash hits the target and
  its neighbours (rAthena: splash 1) with knockback.
  - *Good against:* packs of medium-HP melee mobs that can be gathered; stun
    and status pressure (high VIT).
  - *Bad against:* average single-target DPS; knockback scatters mobs other
    party members are holding in place; high-FLEE mobs need DEX.
- **Spear / Brandish LK.** iRO Wiki Classic lists Brandish Spear or Two-Hand
  Quicken for Pyramids 4 with a Priest's Aspersio. Pierce hits once per size
  step (small 1, medium 2, large 3).
  - *Good against:* lines/clumps in front of the LK; Pierce is best on large
    monsters.
  - *Bad against:* spread-out mobs (Brandish is a frontal cone); small monsters
    (Pierce hits once).
- **Pierce / Clashing Spiral LK.** "MVP: Pierce with Spear Dynamo" (iRO Wiki
  Classic). Clashing Spiral ignores DEF (rAthena). **[one source]** as a named
  build; the skill use is from the LK page's tactics section.
  - *Good against:* high-DEF single targets and large bosses.
  - *Bad against:* crowds; it does nothing to a pack.
- **ASPD / Frenzy LK.** Frenzy greatly raises ATK/ASPD/HP but blocks skills and
  items while active (common knowledge; the wiki only says it "removes
  self-healing"). iRO Wiki Classic: Frenzy "with a good two-handed sword on
  weaker MVPs."
  - *Good against:* single targets with low DEF; Parry and FLEE help vs melee.
  - *Bad against:* high-DEF targets; magic and ranged damage; can't heal itself
    during Frenzy, so it needs a healer.

---

## Paladin

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Grand Cross Paladin | STR 1–20, AGI 1, VIT 80–99, INT 80–99, DEX 30–60, LUK 1 | `CR_GRANDCROSS`, `AL_HEAL`, `CR_AUTOGUARD`, `PA_SACRIFICE` | Holy/DEF gear, MATK weapon | Holy AoE, puller/tank |
| Shield Chain / Battle tank | STR 60–80, AGI 1–50, VIT 90–99, INT 20–30, DEX 30–70 | `PA_SHIELDCHAIN` (Rapid Smiting), `CR_SHIELDBOOMERANG`, `CR_REFLECTSHIELD`, `CR_AUTOGUARD`, `PA_PRESSURE` (Martyr's Reckoning) | Heavy, refined shield; 4-slot 1H weapon | Tank, single-target ranged damage |
| Devotion / Sacrifice support tank | STR 1–60, VIT 80–99, INT 1–60, DEX 80–90+ | `CR_DEVOTION`, `PA_SACRIFICE`, `CR_AUTOGUARD`, `CR_REFLECTSHIELD`, `PA_GOSPEL` (Battle Chant) | Tank set, +7 or higher | Tank, party protection |

- **Grand Cross.** Damage (ATK+MATK) × (100% + 40% × level), holy, cross-shaped
  area around the caster, 1–5 hits depending on how many mobs share a cell;
  costs 20% of current HP per cast and also damages the caster (iRO Wiki
  Classic). rAthena types it as a holy *Magic* skill, so it does not care about
  the target's FLEE.
  - *Good against:* gathered packs of Undead- or Shadow-element mobs (holy
    element bonus); Anubis/Sphinx-type dungeons with a Priest.
  - *Bad against:* Holy-element mobs; stacked mobs on one cell (fewer hits);
    sustained fights without a healer (self-damage); silence.
- **Shield Chain tank.** 5 hits at up to 250% each, range 4, always Neutral,
  ignores size penalty, can miss (+20 HIT); damage from STR, shield weight and
  refine; Lex Aeterna doubles all five hits (iRO Wiki Classic).
  - *Good against:* single targets that need holding; ranged pressure on a
    target the Paladin is tanking.
  - *Bad against:* Pneuma-like ranged blocks; high DEF (DEF still applies);
    elemental weaknesses (always Neutral).
- **Devotion/Sacrifice tank.** iRO Wiki Classic lists several Sacrifice/Battle
  Chant variants, "strong as a tank in places like Nameless or Thors". Devotion
  redirects damage from up to five party members to the Paladin.
  - *Good against:* spike damage aimed at fragile party members (keeps a
    Wizard alive); bosses with heavy single-target hits.
  - *Bad against:* low personal damage; AoE that hits the Paladin plus everyone
    it devotes; Dispel-style effects.
- PvP/WoE-only variants (GC/Gloria Domini/Sac, MR/GD) exist on the same page.

---

## High Wizard

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| INT/DEX AoE (Storm Gust / Meteor / LoV) | STR 1, AGI 1, VIT 25–40, INT 93–99, DEX 99 | `WZ_STORMGUST`, `WZ_METEOR`, `WZ_VERMILION`, `HW_MAGICPOWER` (Mystical Amplification), `WZ_QUAGMIRE`, `MG_SAFETYWALL`, `WZ_FIREPILLAR`, `HW_GRAVITATION` | Staff/rod with INT, DEX gear | Area damage, crowd control |
| Bolter / Jupitel single-target | Same stats | `MG_FIREBOLT`/`MG_COLDBOLT`/`MG_LIGHTNINGBOLT`, `WZ_JUPITEL`, `WZ_EARTHSPIKE`, `WZ_HEAVENDRIVE`, `HW_NAPALMVULCAN` | Same | Single-target magic |

- iRO Wiki Classic gives only "Pure PvM" (INT 99/DEX 99/VIT 25) and "PvM/WoE"
  (VIT 40/INT 93/DEX 99) stat lines; the AoE/bolter split is the same build used
  two ways. Storm Gust freezes and pushes, Meteor Storm stuns, Quagmire slows,
  Safety Wall blocks melee hits on one cell.
  - *Good against:* gathered packs (Storm Gust is the classic mob killer);
    monsters weak to a chosen element; high-DEF/high-FLEE mobs (magic ignores
    FLEE and armour DEF).
  - *Bad against:* high-MDEF or element-immune mobs; Undead mobs can't be
    frozen; boss-protocol monsters ignore freeze/stun; fragile vs melee packs
    and ranged/magic hits (low VIT); cast interruption without Phen/instant cast.
- WoE glass-cannon (INT/DEX up to 150) and PvP bolt builds exist on the same page.

---

## Professor

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Hindsight (auto-cast) | STR 1, AGI 99+, VIT 20–30, INT 99+, DEX 1–20 | `SA_AUTOSPELL` (Hindsight), `PF_DOUBLECASTING` (Double Bolt), `SA_FLAMELAUNCHER`/`SA_FROSTWEAPON` etc. | Fast weapon; Thorny Buckler suggested | Single-target damage (needs Sage link) |
| INT/DEX Bolter | STR 1, AGI 1, VIT 1–60, INT 120+, DEX 110–130 | `PF_DOUBLECASTING`, `PF_MEMORIZE`, `PF_SPIDERWEB` (Fiber Lock), `PF_MINDBREAKER` | INT/DEX gear | Single-target magic, control |
| VIT/DEX Support (Soul Change, Land Protector, ground elements) | STR 1, AGI 1–25, VIT 99–100, INT 1–40, DEX 140–150 | `PF_SOULCHANGE`, `PF_HPCONVERSION` (Indulge), `SA_LANDPROTECTOR`, `SA_DISPELL`, `SA_VOLCANO`/`SA_DELUGE`/`SA_VIOLENTGALE`, `PF_FOGWALL`, `SA_MAGICROD` | Tank-ish DEX gear | Utility, SP support, zone control |

- **Hindsight.** Needs a constant Sage Spirit link from a Soul Linker (iRO Wiki
  Classic); less hurt by silence because the spells auto-cast.
  - *Good against:* single mobs weak to the bolt element; can keep fighting
    while silenced.
  - *Bad against:* anything that removes the link; packs.
- **Bolter.** Called a PvP build on iRO Wiki Classic, but Double Bolt is plain
  magic damage that also works in PvE.
  - *Good against:* single high-DEF targets; Fiber Lock holds a runner.
  - *Bad against:* fragile vs stun/silence (low VIT).
- **Support.** "Most common Scholar build" (iRO Wiki Classic): SP support via
  Soul Change (`PF_SOULCHANGE`, swaps SP with a target) and Indulge. Land
  Protector deletes ground effects in its area and stops new ones; Dispel strips
  buffs; Volcano/Deluge/Violent Gale boost one element; Fog Wall cuts ranged hits.
  - *Good against:* monsters whose threat is ground spells (Land Protector),
    casters (Dispel, Magic Rod, Soul Change can drain an enemy's SP); long
    fights where an SP-hungry partner (Asura Champion, Wizard) runs dry.
  - *Bad against:* has almost no damage of its own; "almost impossible to
    level solo".
- The INT/AGI/STR melee hybrid also exists; the source calls it rarely optimal.

---

## High Priest

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Full Support (INT/VIT or INT/DEX) | STR 1, AGI 1, VIT 40–100, INT 100+, DEX 40–100 | `AL_HEAL`, `PR_SANCTUARY`, `PR_KYRIE`, `PR_IMPOSITIO`, `PR_SUFFRAGIUM`, `PR_ASPERSIO`, `PR_MAGNIFICAT`, `PR_GLORIA`, `PR_LEXAETERNA`, `HP_ASSUMPTIO`, `HP_MEDITATIO`, `MG_SAFETYWALL`, `PR_STRECOVERY`, `ALL_RESURRECTION` | Rod/staff, INT gear | Healer, buffer |
| ME (Magnus Exorcismus) | STR 1, AGI 1, VIT 1–40, INT 105–125, DEX 110–120 | `PR_MAGNUS`, `PR_TURNUNDEAD`, `HP_ASSUMPTIO`, `PR_LEXAETERNA` | INT/DEX gear, Blue Gemstones | Holy AoE vs undead/demon |
| Battle Priest (AGI/STR) | STR 70–100+, AGI 80–100+, VIT 20–50+, INT 1–20, DEX 40–75+ | `PR_ASPERSIO`, `AL_DEMONBANE`, `PR_MACEMASTERY`, `AL_INCAGI`, `AL_BLESSING`, `AL_HEAL` | Mace, shield | Melee damage + self/party buffs |

- **Full Support.** Heal 3000+ with 100+ INT; Sanctuary heals an area; Kyrie
  absorbs hits; Assumptio halves damage taken (pre-re, common knowledge);
  Lex Aeterna doubles the next damage instance on a target.
  - *Good against:* sustained damage of any kind; status-heavy mobs (Status
    Recovery, Cure); boosts any partner's burst via Lex.
  - *Bad against:* no damage of its own except `PR_TURNUNDEAD`/`AL_HOLYLIGHT`;
    stun-locks if VIT is low; Dispel strips its buffs from the party.
- **ME Priest.** Magnus Exorcismus "damages Undead element and Demon race
  enemies" only; 7x7 ground area, 1 Blue Gemstone, 15 s cast reduced by DEX,
  each target is immune to it for 3 s after a hit (iRO Wiki Classic). "Can solo
  well in areas full of Demon or Undead monsters."
  - *Good against:* undead/demon packs that stand in the area (Glast Heim,
    Niflheim, Sphinx); stacks with Lex.
  - *Bad against:* everything that is neither Undead element nor Demon race
    (does zero damage); fast mobs that walk out; fragile (low VIT).
- **Battle Priest.** "Often oriented toward Demon-race monsters" (Demon Bane,
  Aspersio holy weapon).
  - *Good against:* Demon/Undead melee mobs; can heal itself while fighting.
  - *Bad against:* no attack-boosting skills; low damage vs anything else;
    smaller SP pool than support builds.
- A DEX/VIT WoE support build is also listed.

---

## Champion

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Combo Champion | STR 100–120, AGI 80–100, VIT 20–60, INT 30–60, DEX 40–75 | `MO_TRIPLEATTACK`, `MO_CHAINCOMBO`, `MO_COMBOFINISH`, `CH_TIGERFIST`, `CH_CHAINCRUSH`, `MO_EXTREMITYFIST` (as finisher), `MO_EXPLOSIONSPIRITS`, `MO_CALLSPIRITS`/`CH_SOULCOLLECT` | Knuckle/fist weapon; Berserk potion | Single-target melee DPS |
| Asura (STR/INT) Champion | STR 110–130, AGI 1, VIT 1–50, INT 50–90+, DEX 1–100 | `MO_EXTREMITYFIST` (Asura Strike / Guillotine Fist), `MO_EXPLOSIONSPIRITS` (Fury), `CH_SOULCOLLECT` (Zen), `MO_BODYRELOCATION` (Snap) | Carded mace or Lich's Bone Wand; Phen card / Morpheus set (SP) | Single-target burst |
| STR/DEX/VIT "Brawler" | STR 100–110, VIT 80–90, DEX 110–150, INT ~30 | `MO_EXTREMITYFIST`, `MO_BODYRELOCATION`, `MO_INVESTIGATE` (Occult Impact), `MO_FINGEROFFENSIVE` | Mace, stun-resist gear | Burst + survivability (mostly PvP/WoE) |

- **Asura Strike** (rAthena: ignores DEF and FLEE). Damage ATK × (8 + SP/10) +
  bonus, always Neutral, uses all remaining SP, then no natural SP regen for 5
  minutes; needs 5 spheres + Fury, or 1 sphere at the end of a Chain Crush combo
  with no cast time (iRO Wiki Classic). "MVPs with under roughly 300–400k HP"
  die to a Lex-doubled Asura (Champion page).
  - *Good against:* one high-HP, high-DEF or high-FLEE target (ignores both);
    a single big monster with a Priest lexing it.
  - *Bad against:* packs (single target, then out of SP); Ghost-element
    monsters (Neutral does nothing to high Ghost levels); long fights (one
    shot, then a long SP recovery unless fed by Soul Change/potions); casts can
    be interrupted when not comboed.
- **Combo Champion.** "Mostly made for solo leveling fun" and the highest
  sustained melee DPS of the class (iRO Wiki Classic). Combo hits are normal
  weapon damage, so they need HIT and suffer from DEF.
  - *Good against:* single low/medium-DEF mobs one after another.
  - *Bad against:* packs; high-DEF targets; SP drain over long fights.
- Investigate / Occult Impact (`MO_INVESTIGATE`) scales with the target's DEF,
  so it does more against high-DEF targets (common knowledge).

---

## Sniper

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| AGI/DEX Double Strafe / Sharp Shooting | STR 1, AGI 90+, VIT 20+, INT 9, DEX 99 | `AC_DOUBLE`, `SN_SHARPSHOOTING` (Focused Arrow Strike), `AC_SHOWER`, `AC_CONCENTRATION`, `SN_SIGHT` (True Sight), `SN_WINDWALK` | Bow, elemental arrows | Ranged single-target, line AoE |
| Falcon / Blitz Sniper | STR 1, AGI 1, VIT 60+, INT 60+, DEX 99 (LUK for auto-blitz) | `HT_BLITZBEAT`, `SN_FALCONASSAULT`, `HT_STEELCROW`, `HT_ANKLESNARE`, `HT_LANDMINE` | Bow or dagger+guard | Ranged damage that never misses |
| Trap Sniper | DEX/INT; no dedicated source | `HT_ANKLESNARE`, `HT_CLAYMORETRAP`, `HT_LANDMINE`, `HT_BLASTMINE`, `HT_FREEZINGTRAP`, `HT_SANDMAN`, `HT_REMOVETRAP` | Traps (Trap item) | Crowd control, area damage **[community, unconfirmed]** |

- **DS/Sharp Shooting.** "Power House" on iRO Wiki Classic. Sharp Shooting hits a
  ~3x12 line for up to 350% extra, with a (CRIT+20)−(mob LUK/5)% chance to
  bypass DEF and FLEE; 2 s cast.
  - *Good against:* single targets that stay at range; lines of mobs; kiting
    slow melee mobs; elemental arrows exploit weaknesses.
  - *Bad against:* high-FLEE mobs without enough DEX; fragile vs fast melee and
    magic; Pneuma/ranged blocks; mobs that close the gap fast.
- **Falcon / Blitz.** Blitz Beat damage 80 + 6×Steel Crow + 2×(INT/2) +
  2×(DEX/10) per hit, 3x3 around the target; auto-blitz gains +1% chance per
  3 LUK and splits damage between targets (iRO Wiki Classic). rAthena: Blitz
  Beat and Falcon Assault are *Misc* damage and ignore FLEE (and DEF).
  The source calls the pure falconer "mostly PvP/WoE" and hard to level.
  - *Good against:* high-DEF and high-FLEE targets (damage is fixed-ish and
    always lands); small groups (3x3 splash).
  - *Bad against:* very high-HP targets (damage does not scale with weapon or
    ATK); SP cost.
- **Traps.** Ankle Snare roots, Claymore/Land Mine/Blast Mine deal area damage,
  Freezing/Sandman freeze or sleep. Trap use appears as a secondary kit in all
  iRO Wiki builds, but no fetched source described a dedicated PvE trap build.
  - *Good against:* mobs that walk over a fixed point (pulled to the trapper);
    boss-protocol monsters escape snares quickly.
  - *Bad against:* stationary or flying-over mobs; boss monsters (status
    immunity).
- FAS WoE and PvP builds exist on the same page.

---

## Clown (Minstrel)

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| AGI/DEX Arrow Vulcan ("Mad Musician") | STR 1, AGI 80+, VIT 20+, INT 20, DEX 99 | `CG_ARROWVULCAN`, `AC_DOUBLE`, `AC_CONCENTRATION`, `BA_MUSICALSTRIKE`, songs | Violin/instrument, elemental arrows | Ranged damage + songs |
| Support / song Clown (DEX/VIT/INT) | STR 1, AGI 1, VIT 60–100, INT 35–80, DEX 99 (150 final) | `BA_POEMBRAGI` (Magic Strings), `BA_ASSASSINCROSS` (Impressive Riff), `BA_APPLEIDUN` (Classical Pluck), `BA_WHISTLE` (Perfect Tablature), `CG_TAROTCARD`, `CG_MARIONETTE`, `CG_LONGINGFREEDOM` | Instrument | Buffs/songs |

- Song effects (common knowledge, consistent with the wiki): Bragi cuts cast
  time and after-cast delay, Impressive Riff raises ASPD, Classical Pluck raises
  max HP and healing, Perfect Tablature raises FLEE and Perfect Dodge.
  Ensembles with a Gypsy: `BD_LULLABY` (sleep), `BD_ROKISWEIL` (blocks skills),
  `BD_SIEGFRIED` (element resist), `BD_RICHMANKIM` (Mental Sensing, EXP), `BD_DRUMBATTLEFIELD`,
  `BD_RINGNIBELUNGEN`, `BD_ETERNALCHAOS` (removes DEF), `BD_INTOABYSS`.
  - *Good against:* anything a party fights for a long time; Bragi makes
    casters (Wizard, Priest) much stronger.
  - *Bad against:* songs are area effects around the bard; mobs that scatter
    the party; Clown is fragile and immobile-ish while playing. Arrow Vulcan
    variant: good single-target ranged, bad vs high FLEE (physical, can miss).
- WoE build (VIT 100) also listed; "Mad Musician" is "highly discouraged" for WoE.

---

## Gypsy

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| DEX/VIT Arrow Vulcan (PvM/WoE) | STR 1, AGI 1, VIT 80–100, INT 2x–5x, DEX 99 | `CG_ARROWVULCAN`, `DC_FORTUNEKISS`, `DC_SERVICEFORYOU`, `CG_TAROTCARD` | Whip/instrument, elemental arrows | Ranged damage + dances |
| Full Support dancer | STR 50+, AGI 1, VIT 90–100, INT 60–90, DEX 1–4 | `DC_SERVICEFORYOU` (Gypsy's Kiss), `DC_HUMMING`, `DC_FORTUNEKISS`, `DC_DONTFORGETME` (Slow Grace), `CG_TAROTCARD`, `CG_MOONLIT`, ensembles | Whip | Buffs, debuffs |
| AGI Arrow Vulcan (PvM) | STR 1, AGI 7x–9x, VIT 1x–5x, INT 2x–5x, DEX 99 | `CG_ARROWVULCAN`, `DC_THROWARROW` | Whip/bow | Solo/leveling damage ("rarely used") |

- Dance effects (common knowledge): Gypsy's Kiss (Service for You) raises max SP
  and lowers SP cost, Humming raises HIT, Fortune's Kiss raises CRIT, Slow Grace
  lowers enemy ASPD and move speed. Tarot Card of Fate rolls a random effect
  (needs Magic Strings for the cast time).
  - *Good against:* long fights where SP runs short (Gypsy's Kiss); Slow Grace
    is a debuff on fast melee mobs. Arrow Vulcan: single targets at range.
  - *Bad against:* low personal durability in AGI version; dancing in place
    can't follow a moving fight.
- Pure WoE (Dazzler) and Marionette Control "slave" builds also listed.

---

## Assassin Cross

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Sonic Blow / EDP Katar | STR 110–130, AGI 80–100, VIT 40–60, INT 1–30, DEX 50–70 | `AS_SONICBLOW`, `ASC_EDP`, `ASC_CDP`, `AS_GRIMTOOTH`, `AS_CLOAKING` | Katar | Single-target burst |
| Soul Breaker (Soul Destroyer) | STR 90–100+, AGI 1–10, VIT 20–50, INT 100–110+, DEX 30–50 | `ASC_BREAKER`, `ASC_METEORASSAULT`, `AS_SONICBLOW` | Dual Zipper Bear daggers or Ice Pick; Mummy cards for HIT | Ranged single-target |
| Katar Crit | STR 70–110, AGI 80–100+, VIT 1–50, LUK 40–60 | Auto-attack crits, `AS_GRIMTOOTH`/`AS_SONICBLOW` to level | Katar (double crit from katar), Soldier Skeleton / race crit cards | Single-target DPS |
| Grimtooth (variant of SB/Crit) | Katar STR/AGI | `AS_GRIMTOOTH` from Hiding/Cloaking | +8 katar with race cards (source names Triple Beholder Jur for Juperos) | Ranged AoE from stealth |
| Meteor Assault (variant) | STR/INT as Soul Breaker | `ASC_METEORASSAULT` | Weapon element matters | Melee AoE + status |

- **Sonic Blow.** 8 hits; the STR/AGI build gets "highest Sonic Blow and
  Grimtooth damage" (iRO Wiki Classic). EDP multiplies normal and Sonic Blow
  damage but, per the same wiki, does not affect Soul Breaker or Meteor Assault.
  - *Good against:* single targets with moderate FLEE; stun chance.
  - *Bad against:* high-FLEE mobs (hit-dependent); packs; Ghost-element
    mobs with Neutral katars.
- **Soul Breaker.** Range 10. INT part = INT × 5 × level + 500–1000 and *never
  misses*; the ATK part is reduced by DEF/VIT and can miss; ~1–2.8 s cast delay
  (iRO Wiki Classic). "Highest ranged damage for the lowest SP cost."
  - *Good against:* single targets from range, including high-FLEE ones (the
    INT half always lands); MVPs.
  - *Bad against:* packs; after-cast delay limits burst.
- **Meteor Assault.** 5x5 around the caster, 80–440%, 10–55% chance of stun,
  blind, bleeding (iRO Wiki Classic). Physical, so it can miss.
  - *Good against:* packs that surround the assassin; status pressure on
    non-bosses.
  - *Bad against:* boss monsters (immune to the statuses); high FLEE.
- **Grimtooth.** Katar attack at range from Hiding/Cloaking with a 3x3 splash
  (rAthena splash 1).
  - *Good against:* mobs that can't detect hidden players; small groups.
  - *Bad against:* Insect/Demon/boss monsters that detect Hiding (common
    knowledge).
- **Crit.** "Bypasses defense... about 80% crit rate is reachable on most
  monsters."
  - *Good against:* high-DEF targets (crits ignore DEF) with low LUK; high-FLEE
    targets (crits always hit).
  - *Bad against:* high-LUK mobs (reduce crit); bosses with crit-reducing
    traits; "tedious" leveling below 80.
- STR/VIT Sonic Blow is the WoE/PvP version.

---

## Stalker

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| STR/AGI/DEX melee | STR 100–120, AGI 50–90, VIT 30–50, DEX 50–70 | Plagiarized `KN_BOWLINGBASH`, `RG_INTIMIDATE`, `RG_RAID`, `ST_REJECTSWORD`, `ST_PRESERVE`, `RG_PLAGIARISM` | Triple-carded Saber/Gladius, Ice Pick | Melee damage |
| DEX bow / Full Strip | STR 1–50, VIT 50–90, INT 10–50, DEX 110–130 | `AC_DOUBLE`, `ST_FULLSTRIP`, `RG_STRIPWEAPON`/`RG_STRIPARMOR`, `RG_CLOSECONFINE` | Bow with elemental arrows | Ranged damage, debuff (mostly WoE) |
| DEX/INT caster (Plagiarized magic) | STR 1–20, VIT 40–60, INT 70–110, DEX 110–130 | Plagiarized `WZ_STORMGUST` (or `CR_GRANDCROSS`), `ST_FULLSTRIP`, `RG_CLOSECONFINE` | Bow or Bazerald | AoE magic, Wizard stand-in |

- Plagiarism (`RG_PLAGIARISM`) copies the last skill that hit the Stalker;
  Preserve (`ST_PRESERVE`) keeps it. iRO Wiki Classic names "Intimidated Bowling
  Bash" and "Raging Trifecta Blow" for melee and Storm Gust for the caster
  ("can replace a Wizard in parties or in Biolabs Level 3"). Reject Sword
  reflects part of melee damage. Full Strip removes all equipment from a target;
  against monsters, stripping lowers their ATK/DEF (common knowledge).
  - *Good against:* whatever its copied skill is good against; Full Strip
    weakens a boss's ATK/DEF.
  - *Bad against:* a copied skill is at most the copied level (capped by
    Plagiarism level); fragile caster variant; strip fails on boss protocol on
    some servers **[unconfirmed]**.
- DEX/INT WoE "DD" caster (Rogue Spirit North Wind/Jupitel) and Reflect PvP
  builds exist; not PvE.

---

## Whitesmith (Mastersmith)

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Cart Termination (STR hybrid) | STR 110–130, AGI 50–80, VIT 50–80, DEX 50–70 | `WS_CARTTERMINATION` (High Speed Cart Ram), `WS_CARTBOOST`, `BS_OVERTHRUST`/`WS_OVERTHRUSTMAX`, `BS_ADRENALINE` | Mace/axe, Ice Pick or Combat Knife; heavy cart | Single-target burst |
| STR/AGI Melee (Meltdown) | STR 100–120, AGI 70–80+, VIT 40–60, DEX 50–70 | `WS_MELTDOWN` (Shattering Strike), `BS_ADRENALINE`, `BS_WEAPONPERFECT`, `WS_OVERTHRUSTMAX` | Axe/mace | Auto-attack DPS |
| Mammonite / Weapon Perfection support | No source with stats **[community, unconfirmed]** | `MC_MAMMONITE`, `BS_WEAPONPERFECT`, `BS_OVERTHRUST` (party ATK), `BS_ADRENALINE` (party ASPD for axes/maces) | Axe/mace | Party buffs + zeny-for-damage |

- **Cart Termination.** ATK × (cart weight / (16 − level))%, up to 50% stun,
  costs 600–1500 zeny, needs Cart Boost, can miss, reduced by DEF/VIT unless
  using Ice Pick/Combat Knife; race/size cards do not apply (iRO Wiki Classic).
  - *Good against:* single high-HP targets; stun on non-bosses; with Ice Pick,
    high-DEF targets.
  - *Bad against:* packs; high FLEE; zeny cost limits spam.
- **Meltdown.** The STR/AGI build is "built mainly around Shattering Strike"
  (Meltdown can break weapon/armor; common knowledge). Hits single targets.
  - *Good against:* sustained melee on single mobs.
  - *Bad against:* crowds; high FLEE.
- **Weapon Perfection support.** Weapon Perfection removes the size penalty;
  Overthrust and Adrenaline Rush also apply to party members (common knowledge).
  Not described as a build in a fetched source.
- The iRO Wiki Classic page lists only two builds and has an empty equipment
  section.

---

## Creator (Biochemist)

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Acid Demonstration ("Acid Bomb", INT/DEX) | STR 1, AGI 25, VIT 1, INT 99, DEX 99 | `CR_ACIDDEMONSTRATION`, `AM_POTIONPITCHER`, `CR_FULLPROTECTION` | Bottle Grenade + Acid Bottle per cast; stun-resist gear | Single-target burst |
| Slim Pitcher support (VIT/DEX) | STR 1, AGI rest, VIT 97–100, INT 1, DEX 99 | `CR_SLIMPITCHER` (Aid Condensed Potion), `AM_POTIONPITCHER`, `CR_FULLPROTECTION` | Condensed potions | Area healer |
| Potion maker | INT 94–99, DEX 36, LUK 94–99 | `AM_PHARMACY`, `CR_SLIMPITCHER` crafting | — | Crafting, not combat |

- **Acid Demonstration.** Damage ≈ level × 0.7 × INT² × VIT / (INT + VIT),
  1–10 hits, bypasses FLEE and DEF, half damage vs players, chance to break
  weapon/armor; Lex Aeterna doubles it (iRO Wiki Classic). rAthena: Misc damage,
  ignores FLEE.
  - *Good against:* high-VIT, high-DEF, high-FLEE single targets — MVPs and
    bosses; "Sword Guardians in Thor's 3 are easy to kill"; high EXP in Thor's
    Volcano and Biolab 3.
  - *Bad against:* low-VIT mobs (damage scales with target VIT; misses 0-VIT
    targets); packs (single target); consumable cost.
- **Slim Pitcher.** At level 10, heals everyone in a 7x7 area; damage based on
  VIT and skill levels. Guilds use two or three in WoE (iRO Wiki Classic).
  - *Good against:* spread damage on a party standing together.
  - *Bad against:* no damage; costs potions; must stand near the fight.
- Creators also put Full Chemical Protection (`CR_FULLPROTECTION`) on party
  members, preventing equipment strip/break.

---

## Star Gladiator

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| STR/VIT Heat / Union (all-purpose tank) | STR 110–130, AGI 1, VIT 90–110, INT 1, DEX 1, LUK 1–9 | `SG_SUN_WARM`/`SG_MOON_WARM`/`SG_STAR_WARM` (Heat), `SG_FUSION` (Union), `SG_SUN_COMFORT` etc. | Book (3-slot) | Tank, AoE |
| STR/DEX Heat | STR 110–130, VIT 20–40, DEX 100–120 | Heat | Book | Area damage (needs a separate tank) |
| AGI Kicker | STR 110–130, AGI 70–90, VIT 1–50, DEX 50–70 | `TK_STORMKICK`, `TK_DOWNKICK`, `TK_TURNKICK`, `TK_COUNTER`, `SG_SUN_ANGER`/`SG_MOON_ANGER`/`SG_STAR_ANGER` (Wrath), Heat | Book | Single-target DPS |

- Heat (Warmth) hits everything around the SG and knocks it back, on maps set by
  Feeling (`SG_FEEL`); Wrath and Comfort/Protection depend on the day (Solar
  even, Lunar odd, Stellar every 5th) and on Hatred targets (`SG_HATE`).
  Union makes every hit land; the Star Gladiator link removes its HP drain
  (link part common knowledge). Miracle (`SG_*`) unlocks everything for an hour
  (iRO Wiki Classic). Places used: "Thors, Somatology Labs, MVPing."
  - *Good against:* packs that surround the SG on its Feeling maps; Heat
    "pushes mobs back so flee is not reduced"; with Union, high-FLEE targets.
  - *Bad against:* anything off its three chosen maps (Heat only works there);
    Wrath only on its Hatred monsters; knockback scatters mobs a party is
    AoE-ing.

---

## Soul Linker

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Esma bolter (INT/DEX) | STR 1, AGI 9, VIT 1, INT 120+, DEX 99+ | `SL_SMA` (Esma), `TK_SEVENWIND` (Mild Wind), `SL_STIN`/`SL_STUN` (Estin/Estun), `SL_SWOO` (Eswoo), `SL_KAINA` | SP gear (Morpheus set, Sohee) | Single-target magic DPS (main damage dealer) |
| Esma VIT / Kaahi tank | STR 1, VIT 50–99, INT 90–99, DEX 1–50 | `SL_SMA`, `SL_KAAHI` | — | Tanky caster |
| Kaite / Kaizel / Spirit support | STR 1, AGI 1, VIT 20–90, INT 90–100, DEX 60–90, LUK 9 | `SL_KAITE`, `SL_KAUPE`, `SL_KAIZEL`, `SL_KAAHI`, `SL_KAINA`, spirits (`SL_STAR`, `SL_SAGE`, `SL_MONK`, `SL_ASSASIN`, `SL_WIZARD`, `SL_PRIEST`, `SL_CRUSADER`, `SL_KNIGHT`, `SL_BLACKSMITH`, `SL_HUNTER`, `SL_BARDDANCER`, `SL_ROGUE`, `SL_ALCHEMIST`) | — | Buffs (class links) |
| Dagger melee | STR 70–99, AGI 70–99, INT/DEX 18–48 | Mild Wind + spirits/Ka skills | Dagger of Counter / Gladius | Melee, low priority |

- Es-skills only work against monsters (iRO Wiki Classic: "Its Es skills only
  work in PvM"). Esma's element follows Mild Wind; Estin/Estun allow follow-up
  Esma. Kaite reflects magic, Kaupe dodges a hit, Kaizel auto-revives,
  Kaahi heals on being hit (common knowledge for exact effects).
  - *Good against (Esma):* single monsters weak to the chosen Mild Wind
    element; ignores FLEE (magic).
  - *Bad against (Esma):* SP drains quickly; packs.
  - *Support:* strong only with the right class in the party; each link is
    specific (Star Gladiator, Sage, Champion, Wizard, ...).

---

## Ninja

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Magic ninja | STR 1, AGI 1, INT ~95, DEX ~99, VIT rest, LUK 9 | `NJ_HYOUSENSOU` (Freezing Spear), `NJ_BAKUENRYU` (Exploding Dragon), `NJ_KAENSIN` (Blaze Shield), `NJ_HUUJIN`, `NJ_RAIGEKISAI`, `NJ_KAMAITACHI` (First Wind), `NJ_NEN`, `NJ_UTSUSEMI` | MATK dagger; Amatsu catalyst stones | Magic damage, some AoE |
| Throwing ninja | STR 9x, DEX 5x–8x, rest AGI/VIT | `NJ_SYURIKEN`, `NJ_KUNAI`, `NJ_HUUMA`, `NJ_UTSUSEMI`, `NJ_NEN` | Huuma shuriken, kunai/shuriken stocks | Ranged physical |
| Final Strike (Killing Stroke) | STR 80–110, VIT 80–100, DEX 2x–5x | `NJ_ISSEN`, `NJ_NEN`, `NJ_UTSUSEMI` | 4-slot dagger/huuma for % cards | Single-target burst |

- **Magic.** "Fastest leveler"; short casts; lower damage, low HP.
  - *Good against:* elemental weaknesses (fire/water/wind spells); FLEE-heavy
    mobs.
  - *Bad against:* catalyst cost; status effects; high MDEF.
- **Throwing.** Huuma hits a 3x3 splash split among targets (rAthena).
  "Throw Huuma Shuriken performs poorly against high DEF and without element
  advantage."
  - *Good against:* small groups (Huuma); element-matched kunai.
  - *Bad against:* high DEF; ammunition cost.
- **Final Strike.** Damage STR × 40 + user HP × up to 80%; never misses (rAthena:
  ignores FLEE); user drops to 1 HP; "only 50% damage to boss type monsters"
  (iRO Wiki Classic).
  - *Good against:* one non-boss target with high FLEE.
  - *Bad against:* bosses/MVPs (halved), high-HP or high-DEF targets; leaves the
    ninja at 1 HP, so it needs a healer.
- Melee (Shadow Slash `NJ_KIRIKAGE`) builds also exist; "hardest Ninja build to
  level".

---

## Gunslinger

| Build | Stats at 99 | Key skills | Gear | Role |
|---|---|---|---|---|
| Desperado | STR 1, AGI 1, VIT 80–100, INT 40–60, DEX 120–140, LUK 9 | `GS_DESPERADO`, `GS_MADNESSCANCEL`, `GS_INCREASING` | Revolver (pistol); 10 bullets per cast | Melee-range AoE (mob killer) |
| Gatling / AGI-DEX auto-attack | STR 1, AGI 99, VIT 1, INT 9, DEX 120–140 | `GS_CHAINACTION` (pistol), `GS_GATLINGFEVER` (gatling), `GS_MADNESSCANCEL`, `GS_ADJUSTMENT` | Revolver or Gatling gun | Ranged single-target DPS |
| Rifle Tracking / crit | STR 1, AGI 70+, VIT 50+, DEX 99+, LUK 25–40 | `GS_TRACKING`, `GS_PIERCINGSHOT`, `GS_INCREASING` | Rifle | Ranged single-target |
| Shotgun / Grenade | DEX-based | `GS_FULLBUSTER`, `GS_SPREADATTACK` (shotgun), `GS_GROUNDDRIFT` (grenade launcher), `GS_TRIPLEACTION` | Shotgun/launcher | Ranged AoE / burst **[community, unconfirmed]** |

- **Desperado.** 7x7 around the gunslinger, up to 550%, 0–10 hits per enemy
  (closer = more), treated as melee and blocked by Safety Wall (iRO Wiki
  Classic). "Compares it to a Grand Cross Crusader." Weaknesses: "low HP
  modifier, no Heal skill."
  - *Good against:* packs that crowd around; no mob-size limit.
  - *Bad against:* single targets (no AoE bonus); spread-out or ranged mobs;
    weak without a healer.
- **Gatling / Chain Action.** "Fast attacks and a high Flee rate"; low damage
  with handguns.
  - *Good against:* low-DEF single mobs; FLEE tanks melee hits.
  - *Bad against:* high DEF (many weak hits).
- **Rifle.** iRO Wiki Classic's Lever Action build is crit-based ("active skills
  are not recommended"). Tracking as the rifle single-target nuke is standard
  (skill exists in pre-re db) but was not described as a build in a fetched
  source **[community, unconfirmed]**.
  - *Good against:* single high-HP targets at long range.
  - *Bad against:* packs; long cast for Tracking.
- **Shotgun/Grenade.** Full Buster (blinds the user), Spread Attack and Ground
  Drift (elemental spheres with knockback/status) exist in the pre-re skill db;
  only the Triple Action launcher build appears in the fetched page.

---

## Notes for monster balancing (derived from the above)

These are summaries of the per-build notes, not further research.

- **High DEF** hurts: Combo Champion, Bowling Bash/ASPD LK, Gatling GS, Throw
  Ninja, Sonic Blow without crit. It does not hurt: Asura, Acid Demonstration,
  Clashing Spiral, Blitz/Falcon Assault, crit builds, all magic, Investigate,
  Ice Pick users.
- **High FLEE** hurts: every physical non-crit build (LK, Combo Champion, Sonic
  Blow, Cart Termination, Arrow Vulcan, Double Strafe, Desperado). It does not
  hurt: Asura, Acid Demonstration, Blitz Beat/Falcon Assault, Final Strike, the
  INT half of Soul Breaker, Union SG, magic.
- **Not Undead/Demon** shuts off ME Priests completely and weakens Grand Cross
  Paladins and Battle Priests.
- **Boss protocol** shuts off Meteor Assault/Storm Gust/trap status control,
  halves Final Strike, and resists knockback (Bowling Bash, Heat).
- **High-HP single bosses** favour Asura (with Lex), Acid Demonstration,
  Soul Breaker, Cart Termination, Esma, Pierce/Spiral.
- **Packs** favour Storm Gust/Meteor/LoV, Grand Cross, Magnus (undead/demon),
  Desperado, Bowling Bash, Brandish, Heat, Meteor Assault, Sharp Shooting
  lines.
- **Low-VIT targets** weaken Acid Demonstration a lot (damage scales with
  target VIT).
- **Ghost element** blunts every Neutral-only attack: Asura, Shield Chain,
  Final Strike, Neutral bullets/arrows.

---

## Sources

- iRO Wiki Classic, class pages (Builds sections):
  - https://irowiki.org/classic/Lord_Knight
  - https://irowiki.org/classic/Paladin
  - https://irowiki.org/classic/High_Wizard
  - https://irowiki.org/classic/Professor (redirects to Scholar)
  - https://irowiki.org/classic/High_Priest
  - https://irowiki.org/classic/Champion
  - https://irowiki.org/classic/Sniper
  - https://irowiki.org/classic/Clown (Minstrel)
  - https://irowiki.org/classic/Gypsy
  - https://irowiki.org/classic/Assassin_Cross
  - https://irowiki.org/classic/Stalker
  - https://irowiki.org/classic/Whitesmith (Mastersmith)
  - https://irowiki.org/classic/Creator (Biochemist)
  - https://irowiki.org/classic/Star_Gladiator
  - https://irowiki.org/classic/Soul_Linker
  - https://irowiki.org/classic/Ninja
  - https://irowiki.org/classic/Gunslinger
- iRO Wiki Classic, skill pages:
  - https://irowiki.org/classic/Asura_Strike
  - https://irowiki.org/classic/Grand_Cross
  - https://irowiki.org/classic/Magnus_Exorcismus
  - https://irowiki.org/classic/Blitz_Beat
  - https://irowiki.org/classic/Sharp_Shooting
  - https://irowiki.org/classic/Acid_Demonstration
  - https://irowiki.org/classic/Soul_Breaker
  - https://irowiki.org/classic/Meteor_Assault
  - https://irowiki.org/classic/Cart_Termination
  - https://irowiki.org/classic/Shield_Chain
  - https://irowiki.org/classic/Desperado
  - https://irowiki.org/classic/Killing_Stroke
- iRO Wiki Classic, Leveling Spots (party notes): https://irowiki.org/classic/Leveling_Spots
- RateMyServer write-ups:
  - Champion Guide (2008): https://write.ratemyserver.net/ragnoark-online-character-guides/champion-guide/
  - Lord Knight Guide 2011: https://write.ratemyserver.net/ragnoark-online-character-guides/lord-knight-guide-2011/
  - Assassin Cross Breaker Guide (WoE emperium breaking, used only to confirm it is not PvE): https://write.ratemyserver.net/ragnoark-online-character-guides/ragnoark-online-character-builds-stats-skills-guides/assassin-cross-breaker-guide/
- rAthena fork, `db/pre-re/skill_db.yml`: AegisNames and `DamageFlags`
  (IgnoreFlee/IgnoreDefense/Splash) for the skills listed.
