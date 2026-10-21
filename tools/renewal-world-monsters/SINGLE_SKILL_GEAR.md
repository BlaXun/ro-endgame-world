# Gear that lost its single-skill effects (phase 7 of the level-175 run)

**Changed 2026-10-18 (owner):** the single-skill effects are back, scaled down: a third of renewal's
value, skill damage at most +15 % a line (`scaled_skill()` in `build_equipment.py`; OPEN_QUESTIONS 32).
The effects below, written in phase 7, stay beside them.

Renewal gives many items a bonus to one skill (Hundred Spear +45 %, Comet's cooldown -10 s).
PORTING_EQUIP.md §5b drops those: an item one build cannot do without makes that build's skill
the problem, pushes cards out of their role, and rewards a player's own rotation over the party.
Phase 5 turned each such bonus into a broad stand-in (`stand_in()` in `build_equipment.py`),
which keeps the items usable but leaves many of them alike: "+5 % ranged damage, -5 % delay".
The owner (2026-10-17): no single-skill boosts, no must-have items, but good and interesting gear.

The list is whatever the status page's Gear section marks ("single-skill effects replaced");
it was 38 items when this was written. Each gets an effect of its own through `equipment.csv`
(`Script`, with a note), never a hand edit of the generated table.

## What an effect may be

Allowed, in this order of preference (§5b's "preferred kinds"):

1. **A party role**: something the wearer does for the party or in its role. Tanking (damage
   taken, HP, a reflect, an aggro-holding effect), healing (heal power, SP for heals), support
   (buff duration, cast time of support skills by type, not by name).
2. **The class's theme without naming a skill**: an element the class works with (a Warlock
   staff that strengthens Water and Neutral magic), a race or size its region's monsters have
   (a Dicastes weapon against Insects), a weapon type's own strength (a bow's ranged damage, a
   knuckle's critical rate).
3. **A small proc**: an autobonus or autospell that fits the item's story (a Pitaya bow that
   sometimes casts a low-level Fire Bolt), at a rate and level that never carries a rotation.
4. **Stats and plain modifiers** only to round an item off.

Not allowed: a bonus to one skill or a short list of skills by name; cooldown, cast or SP cost
of a named skill; anything that only pays off with one rotation; any fixed-cast change;
anything that stacks without a cap (per stat point, per hit) beyond what pre-renewal's own
items do.

## How strong

- **The budget is the slot's best pre-renewal item at the item's level**, as for the stand-ins:
  at level 100 about what that item gives, plus a step of about 3 % per 10 levels above.
  A weapon's ATK is already set by phase 5; the effect is on top and is what makes it worth a
  slot over a carded pre-renewal weapon, not more than that.
- **Refine unlocks the second half**, as renewal does it (+7, +9): the base effect at +0, a
  second effect at +7 or +9. Nothing above +10.
- **Weaker rather than stronger**: an item that is a little weak is picked less; one that is
  too strong undoes the classes and monsters balanced before it.

## How it is checked

- The class numbers frozen in phase 3 hold with the item worn: the class's single-target
  damage within its target band, area skills under the 0.5 rule and the pack limits
  (`run_specs.py` with the item; the specs in `ro-endgame-classes/tools/transcendent-third-classes/level175/`).
- A tested monster step does not get too easy: a sample of map pulls in the item (phase 5's
  recheck method).
- Each item's renewal effect, its stand-in and its new effect, with the reason, show on the
  status page (Gear section).
