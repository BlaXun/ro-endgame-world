# Cards (phase 8 of the level-175 run)

The cards the converted monsters and bosses drop and pre-renewal lacks (95) are made pre-renewal
cards by `build_cards.py` and drop as in renewal. The owner's rules (2026-10-17): weaker rather than
stronger; no single-skill effects; build enablers are fine; every card checked for abuse; before
and after for every card (status page, Cards section). The owner's draft
(`CARD_REBALANCE_DRAFT.yml`, development directory) is the starting idea.

How a card is made, in order (the script's header has the detail):
1. The draft's script.
2. **Weaker of draft and renewal**, number by number: the draft's "Buff" verdicts never raise a card
   above renewal's own numbers (DEF and MDEF excepted: the eras count them differently).
3. **Held to pre-renewal's cards of the same slot**: a bonus a pre-renewal card of the slot also
   gives is at most the most any of them gives (MVP cards against MVP cards).
4. Flat MATK becomes a MATK rate of a tenth, as pre-renewal's cards give MATK.
5. Single-skill bonuses stay on their skill at a third of renewal's value, damage at most +15 % a
   line (owner, 2026-10-18; before that they became the gear's broad stand-ins). A card whose renewal
   effect is a skill bonus keeps the draft's other lines and loses the draft's stand-ins for it.
6. **The abuse check** flags status immunity, element and race resistance, reflects, drains, damage
   against bosses (each cut to a cap when over it), autocasts and autobonuses, scaling with refine,
   stats or level, special flags (no cast cancel, no knock-back...), defence ignored, and drops,
   zeny or experience effects. Every flag shows on the card's entry.
7. `cards.csv` for a card the rules cannot settle (Kraken Card: its build-enabling skills kept, its
   Raid autocast for the Rogue line only (owner, 2026-10-18); Coyote Card: uninterruptible casting with the Phen card's +25 % cast time).

Result: 68 of 95 cards differ from renewal, 27 are as renewal had them. No card is stronger than the
best pre-renewal card of its slot for the same bonus; the well-geared test party already carries two
Turtle General cards (+20 % against everything) in its weapon, more than any of these.

The cards, their sets and their client entries ship in the mod `renewal-world-cards`; its
`npc/renewal_world_card_drops.txt` adds their drops on load (DROPS.md, "Which mod ships what").

## Too like existing cards (phase 9, 2026-10-18)

The owner found some cards very like cards pre-renewal already has. `build_cards.py` now checks every
converted card against pre-renewal's cards of the same slot and against the other converted cards
(`too_similar()`), on what a card does, numbers aside: the bonuses and their targets, their sign, and
any condition on the wearer's class or weapon. A card is too similar when it has

- **the same effects** as another card,
- **a part of one card's effects at no higher number** (a weaker copy), or
- **all of a pre-renewal card's effects at its numbers or more, plus at most as many again** (that card
  would never be slotted again).

Pre-renewal's own cards are never changed. The first run found 21; each was changed through
`cards.csv` (the note on each says why), and the check now finds none. It shows on every card's
entry on the status page. What changed:

| Card | Too like | Now |
|---|---|---|
| Alnoldi | Soldier Andre (Plant -30 %) | Plant -20 %, Poison resistance +20 % |
| Cendrawasih, Siorava, Dolomedes, King Dramoh | Elder Willow / Mole (+2 of the stat) | the stat +1, the class line's refine bonus kept |
| Cenere | two converted garments (ASPD +5 %) | ASPD +1 % per 20 AGI, at most +5 % (renewal's idea) |
| Wakwak | Whisper Boss, Magmaring (ATK) | ATK +1 per 20 STR, at most +5 (renewal's idea) |
| Cowraiders 3 | Andre, Hilsrion (ATK) | its refine bonus on a dagger only, as in renewal |
| DR815 | Galion (HIT +5) | HIT +3, Formless damage taken -5 % |
| Frozen Wolf, Scaraba, Piranha | each other (MATK %) | Water magic +3 % and Water -5 %; Earth magic +3 % and Insect -5 %; Piranha as it was |
| Exploration Rover | Steam Goblin (CRIT vs Formless) | CRIT vs Formless +5, 10 % of Formless DEF ignored |
| Gold Queen Scaraba | Elder Willow (INT) | MATK +1 %, Earth magic +5 %, Insect protection kept |
| Nightmare Verit | Fallen Bishop (MATK) | Max SP +4 % added |
| Sedora | Mobster, The Paper (critical damage) | critical damage +10 %, 3 % chance of Bleeding |
| E Cowraiders 1 and 2 | Archer Skeleton, each other | their renewal skill bonuses back, scaled (Spread Attack, Rapid Shower) |
| the EP17 skill cards (Beta Cleaner, Beta Guards, Omega Cleaner, ...) | each other (stat, HP, +1 % damage) | their renewal skill bonuses back, scaled |

Kept although alike at a glance: Comodo against Alicel and Gaster against Alice are their mirror
images (the trade the other way round), Bellare and High Bellare work on different guns, and a card
whose effect pre-renewal has only in another slot (Jejeling's HP on a garment, Menblatt's ranged
damage on a garment) is a new option for that slot, not a copy.
