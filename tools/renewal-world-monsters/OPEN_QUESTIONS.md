# Open questions

Decisions taken while working without you (2026-10-09, overnight), each with
the default chosen so the work could go on. Overrule any of them and the
regions concerned are rebuilt and retested.

## 1. Stock unfair monsters in new regions

Bifrost spawns stock Luciola Vespa and Cornus (you said: leave them for now).
El Dicastes spawns stock Centipede (98) and Tatacho (52), both on the unfair
list too. **Default: left as they are, like Bifrost's.** Say if both regions
should drop them or get converted copies instead.

## 2. A new region is a step above its references

You agreed Dewata should be a step above ordinary monsters of its level. **Default:
every band follows that rule** (toughness above 1 in the mid band, experience at
1.25× the band's reference rate), not only Dewata.

## 3. Regions spanning two bands

Only Verus (renewal 100-171) spans the mid/high edge (renewal 140 by default,
see 4). **Default: its monsters follow their own band**, so the inner city
(the higher levels) is a step above the tunnels.

## 4. Where the renewal regions sit in pre-renewal's levels (the big one)

Converting by the shared monsters nearest in renewal level (the mid band's way)
places renewal level 100 at pre-renewal 56, 110 at 67, 125 at 76, 145 at 92;
above renewal 145 no shared monster exists. The high band instead uses the
shared monsters pre-renewal itself put beyond 99 (Splendide, Manuk), and puts
everything from renewal 105 up at pre-renewal 101-114. So two layouts are
possible:

1. **Renewal regions from renewal level 105 up are endgame** (pre-renewal
   101+), as Bifrost and Eclage are now.
2. **The renewal regions spread over pre-renewal's levels**: Dewata 43-53,
   Malaya about 56-76, El Dicastes about 73-76, Bifrost and Eclage about
   73-92, only what lies beyond renewal 145 at 99+. New content for every
   level from 45 up; Bifrost and Eclage would be converted and tested again.

**Default for tonight: between the two.** The mid band's way covers renewal
60-139 and the high band starts at renewal 140, where Bifrost and Eclage begin,
so those two stay exactly as tested. That gives Dewata 43-53, Malaya about
56-76, El Dicastes about 73-80, then Bifrost and Eclage at 110+: a progression
in renewal's own order. Kept in the high band instead, Malaya would have come
out at pre-renewal 101-108 with 8-16k HP, endgame levels a level-99 party
hardly notices. Verus (renewal 100-171) is split by map. A region can be put
in one band as a whole with `band` in monster_maps.csv. Choosing layout 1
or 2 instead changes bands.csv; the plans and the harness carry over.

## 5. Borderline after the night's tests

- **Antique Book ×3** (Eclage): beaten by an Assassin Cross party 4 of 6, a
  Professor party 2 of 3, a Clown party 2 of 3; the standard party loses.
  Kept as converted (your rule: one common party is enough).
- **Elite Buffalo Bandit, the shooter (E_COWRAIDERS2)** (Rockridge mine): with
  Pneuma and its HP halved, three still beat a level-99 party in one run of
  three. Twenty spawn in the mine. Default: kept; say if it should lose more.
- **Cendrawasih ×2** (Dewata): half the runs wipe; it is judged alone (sixteen
  on its field).
- **The Scaraba eggs** pay half the reference rate. Default; they could also
  pay nothing, as objects.

## 6. The quest areas

Bios Island, Rudus, Wolfchev's laboratory, the Verus bunker, the nightmare
pyramids, clock tower and Glast Heim, Prontera's prison and Payon's illusion
cave get their monsters (spawned only while the quest areas setting is on);
their bosses do not, and Lasagna, Amicitia and the staged maps have none.

- Their loot includes some of renewal's quest items (Key of Twisted Time,
  event items EP17_1_EVT02/39). **Default: kept as drops**; they do nothing in
  pre-renewal. Say if they should be left out.
- Their HP and attack are capped (see BALANCING.md) and halved on top
  (`offence`/`toughness` 0.5 in monster_maps.csv): with the cap alone a level-99
  party lost nearly every pack. **Default: halved; their experience is the
  conversion's, halved with HP, not calibrated yet.**
- Left without monsters, since even halved theirs beat every party tried:
  Wolfchev's laboratory (lhz_dun04: the Bio Lab 4 versions of Bio Lab 3's
  unfair monsters), Bios Island's library and research rooms (ba_lib,
  ba_pw01-03: Bookworm, Cramp, Bellare, Plaga, Plasma), the nightmare clock
  tower (c_tower2_, c_tower3_) and Glast Heim castle (gl_cas02_: Wanderer and
  Rideword). Options: scale them further, or leave them as the hardest content.
- The quest-area tests ran once with three or four servers; the first server
  in each run went bad after an early wipe (even its references "wiped"), so
  the verdicts rest on the other servers' runs.
