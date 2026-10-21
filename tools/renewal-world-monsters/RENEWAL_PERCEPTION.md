# Ragnarok Online Renewal: How Players Perceived It

A compilation of player criticism of the Renewal update (2010 onward), why many veterans left, and what it means for pre-renewal modding (ragnarokoffline.app, level cap 175).

---

## 1. Rollout and immediate reception

- Renewal was a system-wide revamp: stats, skills, EXP, level limits and monster placement all changed, and third classes were added, breaking the long-standing base level cap of 99.
- **jRO rolled it back.** Renewal went live in Japan on July 6, 2010, was withdrawn after a poor player reception, and was later reintroduced *without* the new EXP system, the new monster spawns, the third-class job change quest and the Adventurer's Academy.
- Other regions followed in 2010–2012 (pRO, iRO, idRO, bRO, aRO, ruRO, fRO). Episodes after 13.3 require Renewal, so classic servers are stuck at that point unless content is adapted by hand.

## 2. Formulas and stats felt "off"

- **Exponential → linear.** Pre-renewal stats scaled exponentially, with breakpoints that added depth to stat and gear builds and rewarded game knowledge. Renewal made them linear.
- **Casting.** Pre-renewal: casting time is entirely variable, and 150 DEX means instant cast. Renewal added a fixed cast time on top of the variable one, so instant cast became impossible.
- **Pacing mismatch.** Attack speed became trivial (190 ASPD was easy to reach) while casts felt slow.
- **Danger disappeared.** One veteran estimated pre-renewal monsters dealt roughly 3–10× more base damage. In renewal, even New World mobs hit so softly that an ungeared character could survive several hits.
- **Gear mattered less.** Popular summary: in pre-trans gear was nice to have, in pre-renewal it was a requirement, in renewal it was an afterthought.
- **DEF rework.** In pre-renewal ~100 DEF was close to invincible; in renewal you'd need around 4000 for a similar effect, so all gear values changed meaning.

## 3. Mob placement and leveling

- Monster placement was changed game-wide, wiping out years of shared knowledge about classic leveling spots.
- **Level-gap penalties.** Renewal added EXP (and on kRO-style servers, drop) penalties for killing monsters above or below your level.
- **Strong monsters stopped being rewarding.** In pre-renewal monsters gave fixed EXP, so e.g. a solo Archer with an off-party tank could kill Kasas and gain huge chunks of levels. In renewal, the main reason to fight stronger monsters was to avoid the penalty.
- **Party play weakened.** EXP share range went from 10 to 15 levels, but in practice the mechanics (EXP quests, easy one-shot mobs) pushed people toward solo play despite a party bonus.

## 4. Streamlining and loss of identity

- First-job quests were replaced by the Adventurer's Academy: mini quests to 10/10, then simply talk to the right teacher to change class.
- Maps now tell you where monsters spawn.
- Leveling moved toward EXP quests ("quests telling you what to do").
- One veteran's quick guide summed up the perception: quests telling you what to do, solo play, easy difficulty and "WoW-clone" point to Renewal; the opposite points to pre-renewal.
- Lore changes: Morroc became a ruin reachable only by teleport.

## 5. Third classes

### 5.1 Diluted class identity
- When Gravity launched Revo-Classic, press coverage noted that some fans felt the third tier diluted what made each class appealing, which is why that version returned to the original skill trees.
- Neither Ragnarok Online: Zero nor Russian Revo-Classic launched with third classes.

### 5.2 Power creep: every class got a "broken button"
- Common complaint: every class now had its own absurd gimmick (one veteran compared it to Marvel vs. Capcom).
- **Rune Knight** was the extreme case: for a while it was the best class in PvM, PvP and WoE at once, mainly through a handful of skills (Spiral Pierce, Dragon Breath), until nerfs.
- **PvP became "rocket launcher tag"**: fights decided by who lands their burst first.
- WoE balance was widely seen as broken.
- Even players who preferred renewal servers admitted third-class skills were imbalanced.

### 5.3 Old content became trivial
- MVPs went from needing a guild (or bug abuse) to being soloable by almost anyone.
- Players who liked pre-renewal's difficulty felt renewal removed the fear of dying from a single mistake.

### 5.4 Rebirth lost its meaning
- In kRO you could skip rebirth and go straight to third job, permanently giving up rebirth skills and stat bonuses in exchange for reaching endgame faster. Transcendence went from prestige milestone to optional.

### 5.5 The creep never stopped
- Fourth jobs repeated the pattern; players cite their heavy impact on refining (extremely expensive, RNG-dependent).
- The developers of Ragnarok Online 3 now openly name **stat inflation** (old dungeons becoming too easy as player power keeps growing) as a problem they want to solve with seasonal resets.

## 6. Gravity's own response

- jRO withdrew Renewal and reintroduced it without the new EXP, spawns and academy.
- iRO opened an official Classic server; the producer acknowledged the community had asked for years to play the game "the way we all remember it".
- Revo-Classic servers combine renewal formulas with **pre-renewal monster spawns** and an EXP curve between the two, a strong signal the spawn changes were seen as a mistake.
- Revo-Classic and Zero launched without third classes; Zero rebalanced 1st/2nd/trans skills and raised the trans level cap to 130 instead.

## 7. The other side (what renewal defenders liked)

- More build variety: pre-renewal WoE was cookie-cutter (every Professor a support, offensive bolters a novelty).
- Stronger weapons finally mattered more than 4-slotted weak weapons; level 4 weapons became worth using.
- Renewal acted as a reset for pre-renewal's own power creep after transcendent classes, when certain builds (katar Assassin Cross, Creator, Champion) one-shot everything.
- Late pre-renewal content had its own problem: monsters and MVPs often became binary — either you get one-shot or you're unkillable — and some MVPs effectively required boss cards, bug abuse or a whole guild.

## 8. Design takeaways for the level-175 mod

Goal: raise max base level to 175 while keeping the 1–99 feel unchanged and preventing instant cast.

**Avoid (most disliked renewal mechanics):**
- Fixed cast time.
- Level-gap EXP/drop penalties.
- Moving monster spawns away from classic leveling spots.
- Third-class-style power spikes above 99 that trivialize MVPs and turn PvP into burst races.

**Consider:**
- **Redux cast formula** (fan project reworking renewal on pre-renewal foundations): `cast_time * 0.989^dex`
  - Matches pre-renewal at 100 DEX (~33% remaining).
  - Never reaches zero: ~19% remaining at 150 DEX, ~11% at 200, ~6% at 250.
  - Lets you raise `max_parameter` beyond 99 without bringing instant cast back.
- **Redux attack formula** (linear, easier to balance with stats above 99):
  ```
  bonus = floor(str / 10) * 10
  base  = str + dex/5 + luk/5 + bonus
  final = (base + (bonus + weaponAttack + attackBonuses) * %cards) * element
  ```
  Note: this changes damage below 99 too, so it conflicts with "1–99 unchanged" unless only applied above a threshold.
- **Redux status resistance**: attacker's base level reduces the target's resistance, so 100 VIT no longer grants universal immunity once levels go above 99.
- Keep power growth between 99 and 175 incremental (stats, gear, maybe skill levels) instead of new burst skills, to avoid the "every class has a broken button" problem.

---

## Sources

- [iRO Wiki – Renewal](https://irowiki.org/wiki/Renewal)
- [RateMyServer forum – Difference between pre renewal and renewal RO (pages 1–2, 2013)](https://forum.ratemyserver.net/general-discussion/difference-between-pre-renewal-and-renewal-ro/)
- [Ragnarok Wiki – Episode Updates (Renewal, Revo-Classic, Zero)](https://ragnarok.fandom.com/wiki/Episode_Updates_(RO))
- [Steam Community – Renewal or Classic?](https://steamcommunity.com/app/215100/discussions/0/1474222595297237703)
- [Steam Community – euRO player comments on renewal](https://steamcommunity.com/app/250740/discussions/0/684839199319695569/)
- [Siliconera – Ragnarok Online "Classic" server](https://www.siliconera.com/?p=222297)
- [Prima Games – Revo-Classic relaunch](https://primagames.com/featured/legendary-mmo-ragnarok-online-relaunches)
- [mein-mmo.de – Ragnarok Online Revo-Classic](https://mein-mmo.de/nach-wow-classic-ragnarok-online-retro-version/)
- [r/RagnarokOnline wiki FAQ (server types)](https://r.datuan.dev/r/RagnarokOnline/wiki/general_faq)
- [r/RagnarokOnline – fourth jobs and refining (LATAM thread)](https://reddit.sudovanilla.org/r/RagnarokOnline/top)
- [NoypiGeeks – Ragnarok Online 3 seasonal system and stat inflation](https://www.noypigeeks.com/?p=271035)
- [Redux initiative (HackMD)](https://hackmd.io/@ro-for-casuals/redux)
