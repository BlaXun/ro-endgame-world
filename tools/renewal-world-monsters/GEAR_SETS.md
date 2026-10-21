# Gear sets per level step

The test gear for phase 6 (bosses) and for the gear recheck of phase 5: what a party of a step
would wear after farming the regions of its step and those below, per class. The rows are in
`gear_sets.csv`; a set is every row of its step and the steps below it, the later row winning for
the same member. `level175/stepfight.py --gearset` puts them on.

- Base: `GEAR=mid` (FIGHT_TESTS.md): a +7 shop weapon, casters a +4 Arc Wand, a +4 Muffler with a
  Raydric card; with the well-geared yardstick's two Turtle General cards in the physical
  weapons (the stand-in for a player's race, size and element cards).
- On top: the converted renewal weapons and shields of the steps at or below, refined to +7, the
  same cards in their slots. Only items that drop from ordinary monsters: a boss's items join
  when the boss goes in (phase 6), and are not in these sets.
- Members at 99/70 keep the pre-renewal set (`GEAR=mid`).
- No converted armour, garment, shoes or accessory beats the pre-renewal set's for these classes
  (the converted ones are for Minstrels, Wanderers and the classes Doram gear was given to), so
  only weapons and the Royal Guard's shield change.

| Step | Rune Knight | Royal Guard | Arch Bishop | Warlock | Ranger | Genetic |
|---|---|---|---|---|---|---|
| 100, 110 | +7 Claymore | +7 Pike, +4 Shield | +4 Arc Wand | +4 Arc Wand | +7 Arbalest | +7 shop weapon |
| 120 | Crimson Two-Handed Axe | | | | | |
| 130 | | Imperial Spear, Imperial Guard | | | | |
| 140, 150 | | | Illusion hammer (Ep172_1h_Hammer) | | Illusion bow (Ep172_Bh_Bow) | Illusion sword (Ep172_1h_Sword2) |
| 160 | Illusion spear (Ep172_Bh_Spear) | | | | | |
| 170 | Illusion sword (Ep172_Bh_Sword) | Illusion spear (Ep172_1h_Spear) | | Illusion staff (Ep172_Bh_Staff) | | |
