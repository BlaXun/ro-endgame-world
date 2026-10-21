# Porting Renewal Equipment to Pre-Renewal

Spec for converting rAthena Renewal equipment (`db/re/`) into the pre-renewal database used by ragnarokoffline.app, as part of raising the max base level to 175.

**Core principle:** derive conversion rules from data, apply them mechanically through a script, and flag everything that doesn't fit a rule for human review. Never hand-edit converted items.

**Hard constraints**
- **Max level is 175 base / 70 job.**
- **Third classes exist.** A transcendent character at 99/70 can convert to its third class. Levels 100–175 are third-class territory; there is no route from non-transcendent 2nd classes to third classes.
- Gameplay for levels 1–99 must stay unchanged.
- No fixed cast time, no instant cast via items.
- No renewal-style power creep (see `RENEWAL_PERCEPTION.md`).

---

## 1. Calibrate on items that exist in both databases

rAthena keeps separate item databases under `db/pre-re/` and `db/re/`, and many item IDs appear in both.

For every shared ID, extract side by side:
- ATK, MATK, DEF, MDEF
- Weapon level / armor level
- Required level (`EquipLevelMin`)
- Slots, refineable flag, allowed jobs
- Script bonuses (parsed per bonus type)

Output: `calibration.csv` (one row per shared ID) plus a summary of observed ratios per field and per bonus type.

These pairs are real Gravity decisions ("this item was X in pre-re and Y in re") and are the basis for every rescale rule below. Where the data disagrees with a formula, the data wins and the discrepancy is logged.

## 2. DEF: convert by damage reduction, not by number

The two systems reduce damage differently:
- **Pre-re hard DEF:** reduces damage by DEF % (roughly 1 DEF = 1%).
- **Renewal hard DEF (approximate):** damage multiplier ≈ `(4000 + DEF) / (4000 + DEF × 10)`.

Rule: convert each item to the pre-re DEF value that gives the same % reduction.

```
re_reduction = 1 - (4000 + D) / (4000 + 10 * D)
pre_def      = round(100 * re_reduction)     # e.g. D = 100 → ~18
```

> ⚠️ Verify both formulas against rAthena's `battle.cpp` before use, and validate against the calibration pairs from step 1. Per-item DEF is a share of the total, so check the rule against full gear sets, not just single items.

Apply the same approach to MDEF once its formulas are confirmed.

## 3. Sort every script bonus into four groups

| Group | Meaning | Examples |
|---|---|---|
| **Keep** | Works the same in both systems | Element, race and size modifiers; flat stat bonuses (STR, AGI…) |
| **Rescale** | Same concept, different scale | ATK, MATK, DEF values; percentage rates calibrated in step 1 |
| **Translate** | Renewal-only concept with a pre-re equivalent | Weapon MATK → MATK % (pre-re staves work this way) |
| **Drop** | No acceptable pre-re equivalent | Fixed cast bonuses, refine effects above +10, random options, enchant and shadow gear hooks |

References:
- `doc/item_bonus.txt` in rAthena for bonus definitions.
- `#ifdef RENEWAL` / `RENEWAL_*` blocks in the source to find bonuses that behave differently per mode.

Every bonus type found in the renewal items must be assigned to exactly one group. Unknown bonus types → review list, never silently kept.

## 4. Level and class requirements

- **Equip level:** keep renewal required levels up to 175 (see 4b). Items whose renewal level is ≤ 99 keep their pre-re level if they already exist in pre-re.
- **Class restrictions:** third-class gear keeps its restrictions. Only third classes reached from transcendence exist, so restrictions should point at the transcended-third variants (rAthena `Classes: Third_Upper`); references to non-trans third classes, baby third classes and fourth jobs are dropped or remapped. Never leave references to classes that don't exist in this game.
- **Gear above level 99 is effectively third-class gear**, since only third classes can level past 99. Items usable by 2nd/transcendent classes should stay at ≤ 99 or be checked individually.
- **Item sets / combos:** remove any combo whose partner items aren't being ported.
- **Refine:** cap at +10; strip any script branches for `getrefine() > 10`.

## 4b. Level cap 175/70

The base cap of 175 matches the classic third-class era of Renewal, so most renewal equip levels and level thresholds (e.g. `BaseLevel >= 175`, "+1 ATK per 10 base levels") can be **kept as they are**.

- **Gear from later episodes (level cap 200+, fourth-job era):** exclude by default. If a piece is wanted, map its level into ≤ 175 with one fixed rule and remap its script thresholds with the same rule; otherwise thresholds above 175 never trigger.
- **Job level checks.** Scripts checking third-class job levels stay valid as long as they fit within job 70; anything above is remapped or dropped.
- **Stats above 99.** 175 levels give far more stat points than pre-re was built for. Gear with large stat bonuses pushes stats further, so check cast-time and damage results at high stats against the anti-instant-cast rule.
- **Monsters use the same level bands**, so drop sources and item levels stay aligned.

## 5. Power budget (decide before converting)

Write the budget down first, then enforce it automatically:
- No item usable below level 100 may beat the best existing pre-re option at that level.
- Items above level 100 improve on their predecessors in steps, not jumps.
- Top-end gear is balanced against **third classes running on pre-renewal formulas**, not against renewal's endgame. The power of renewal gear depends on renewal damage formulas and third-class skills; in a pre-re damage model the same bonuses can hit very differently.
- **Equipment balance depends on the third-class skill port.** Third-class skills were the biggest source of renewal power creep (see `RENEWAL_PERCEPTION.md`, section 5). Settle the skill formulas first, or at least alongside, and calibrate gear against them.
- No item reduces cast time to zero.

Any converted item that breaks the budget goes to the review list.

## 5b. Skill-specific bonuses: drop by default

Gear that boosts a single skill (skill-damage % bonuses, skill-specific cooldown or cast reductions, "enhances Skill X" effects) is **dropped, not converted**.

Reasoning:
- If a skill is too weak to be used without a gear bonus, the skill itself is flawed. The fix belongs in the skill's formula, cost or delay (skill port), not in an item that makes it mandatory.
- Skill-specific gear turns builds into "best in slot for my skill" and pushes cards out of their role as the main customization layer.
- It makes each player optimize their own rotation instead of their role in the party, which works against party play.

Rules for the conversion script:
- Remove skill-specific bonuses from the item script and log each removal.
- If removing them leaves an item with nothing meaningful, mark the item for exclusion on the review list.
- If a removed bonus suggests that a third-class skill depends on it to be viable, add that skill to a **skill-port follow-up list** (skill name, item(s), removed bonus).
- Prefer slotted variants of items, so cards remain the primary way to customize.

Preferred kinds of power for gear (when an item needs a replacement effect after review):
- Role support: tanking, healing efficiency, support skill durations, party-relevant utility.
- Generic modifiers that work alongside cards: race, element, size, flat stats.

Note: party play itself mostly comes from systems outside gear (monster density and damage high enough that tanks and healers matter, EXP sharing that rewards grouping, support skills worth bringing). Gear should simply not work against it.

## 6. Reproducible pipeline

- The agent writes a **conversion script**, not hand-edited item entries.
- Output goes into a **separate import file for the mod**; the base pre-re database stays untouched.
- **Per-item log:** source values, rules applied, resulting values.
- **Review list:** every item that didn't fit a rule, broke the power budget, or used an unknown bonus.
- **Regression check:** run against the level 1–99 baseline (damage, cast times, EXP, drops for a fixed set of test characters) to prove nothing below 99 changed.

## 7. Client data

- Item descriptions in the client data still show renewal numbers. Regenerate them from the converted values so players see what the server actually does.
- Check that roBrowserLegacy (ragnarokoffline branch) has the sprites, icons and item IDs for every ported item.

## 8. Port together with monsters

Most of this gear comes from renewal monster drops. Equipment and monster conversion should share level bands and be done together, so drop sources make sense and the population engine's looting and vending (prontera-vendors price list, shell-looting rare-item priority) stay consistent.

---

## Deliverables checklist

- [ ] `calibration.csv` + ratio summary (step 1)
- [ ] Verified DEF/MDEF conversion rule (step 2)
- [ ] Bonus classification table covering every bonus type in scope (step 3)
- [ ] Level/class/refine mapping rules (step 4)
- [ ] 175/70 handling: exclusion or remapping of 200+ era gear, job-level checks, high-stat checks (step 4b)
- [ ] Written power budget, calibrated against the ported third-class skills (step 5)
- [ ] Skill-specific bonuses removed + removal log + skill-port follow-up list (step 5b)
- [ ] Conversion script + mod import file + per-item log + review list (step 6)
- [ ] Regenerated client item descriptions (step 7)
- [ ] Level band alignment with monster conversion (step 8)
- [ ] Level 1–99 regression baseline passes
