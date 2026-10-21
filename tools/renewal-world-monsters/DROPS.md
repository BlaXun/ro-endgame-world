# Drops of the converted monsters (phase 5 of the level-175 run)

Each converted monster drops what it drops in renewal, with these rules (PORTING_EQUIP.md, in the
development directory, is the spec; the conversion rules themselves are in `build_equipment.py`'s
header, taken from the 1,920 equipment pieces both eras' tables share).

| Kind | What happens | Count |
|---|---|---|
| Loot (etc, usable) | as in renewal; what pre-renewal lacks is copied from renewal's tables | as before |
| Equipment pre-renewal has | drops as pre-renewal's own item, unchanged | 43 items |
| Equipment new to pre-renewal | converted by `build_equipment.py` and drops | 54 items: 25 by rule, 29 best attempts |
| A card pre-renewal has | drops with pre-renewal's effect, unchanged | 1 |
| A card new to pre-renewal | converted by `build_cards.py` and drops (phase 8, `CARDS.md`); what it cannot convert is listed in `cards_left_out.csv` | 95 cards, 102 drop rows |
| Random option groups on drops | left out (pre-renewal has none) | |

A boss's items are converted now and drop once the boss is in (phase 6).

## Which mod ships what (2026-10-18)

`build_monsters.py --write` writes four mods; each works without the ones after it:

| Mod | Drops |
|---|---|
| `renewal-world-monsters` | its mob_db's `Drops`: the loot, pre-renewal's own equipment and cards, and the etc/usable items copied from renewal (its `db/item_db.yml`) |
| `renewal-world-minibosses` | the minibosses' `Drops`, by the same rules |
| `renewal-world-mvps` | the MVPs' `Drops` and `MvpDrops`, by the same rules |
| `renewal-world-gear` | the converted equipment: `npc/renewal_world_gear_drops.txt` adds each drop on load (`addmonsterdrop`), at the rate and steal protection the mob_db had, to each monster that is loaded (a boss's only with its mod on) |
| `renewal-world-cards` | the converted cards, the same way (`npc/renewal_world_card_drops.txt`) |

The scripts log `<mod>: N ... drops added to M monsters` on start, and an error naming any drop
that found no free slot. The build fails when a converted item or card is an MVP reward (`MvpDrops`
cannot be added on load), when a set mixes converted equipment and cards, and when a monster's
drops with the added ones would pass rAthena's 10.

**Best attempts** (an item the rules alone could not settle) are all in `EQUIPMENT_REVIEW.md` with
their renewal values, what the rules gave and what was done instead and why; the overrides are in
`equipment.csv`. Kinds of best attempt:
- 21 weapons over the power budget (best pre-renewal weapon of the type, +5 % at level 100 and +3 %
  every 10 levels above): ATK cut to it. Renewal's level-150 weapons carry 250-320 ATK where
  pre-renewal's best of the type is 140-230.
- 2 items carried by skill-specific bonuses (Imperial Spear, Red Ether Bag): a replacement effect
  of the preferred kinds (the tank's HP; MATK and INT).
- 2 level-70 weapons whose ATK grows with the square of the refine (Crimson Dagger and Two-Handed
  Axe, +100 at +10): made linear (+40 at +10).
- 5 Doram-only items (3 of them otherwise by rule) (Summoner, a class this game does not have): the armour given to every job,
  the staves to the Mage line.

**Per region** (an item that drops in two regions counts in both):

| Region | By rule | Best attempt |
|---|---|---|
| Bifrost | 5 | 0 |
| El Dicastes | 5 | 6 |
| Episode 17.2 (Illusion maps) | 9 | 10 |
| Malangdo | 0 | 1 |
| Nightmare pyramid | 0 | 1 |
| Rockridge | 6 | 6 |
| Bosses only | 5 | 7 |

**Gear sets per level step** for phase 6: `GEAR_SETS.md` and `gear_sets.csv`.
