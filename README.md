# Renewal endgame: world

Mods for [Ragnarok Offline](https://github.com/Flux159/ragnarokoffline.app) that fill renewal's lands with their monsters, bosses and loot for pre-renewal characters from level 80 to 175. Everything is balanced against pre-renewal, with companion parties as the test, rather than copied from renewal.

| Mod | What it is | Needs |
|---|---|---|
| [`renewal-world-monsters`](mods/renewal-world-monsters) | 115 renewal monsters on 45 renewal-world maps, levels 80–175, on a ladder of level steps. | renewal-world |
| [`renewal-world-minibosses`](mods/renewal-world-minibosses) | King Dramoh, Wild Rider and the gold Scarabas, with their eggs. | renewal-world, renewal-world-monsters |
| [`renewal-world-mvps`](mods/renewal-world-mvps) | 14 bosses, including Leak, Kraken, the Scaraba Queens, Spider Chariot and Nightmare Amon Ra, with their MVP rewards. | the three above |
| [`renewal-world-gear`](mods/renewal-world-gear) | 54 renewal items from these monsters, each held to pre-renewal's best of its kind, and 3 sets. | renewal-world-monsters |
| [`renewal-world-cards`](mods/renewal-world-cards) | 95 cards, none stronger than pre-renewal's best for its slot and bonus, and 11 sets. | renewal-world-monsters |

Pre-renewal only. The maps come from the app's own [renewal-world](https://github.com/Flux159/ragnarokoffline.app/tree/main/registry/mods/renewal-world) mod. The classes that level to 175 are in [ro-endgame-classes](https://github.com/BlaXun/ro-endgame-classes).

## Installing

In the app: **Settings → Mods → Find Mods**, then install `renewal-world` and the mods above that you want.

`renewal-world-monsters`, `-gear` and `-cards` need app 1.5.4 or later. The minibosses and MVPs need the release after 1.6.7: it joins several mods' monster skill rows (`mob_skill_db.txt`), so the three monster mods no longer take each other's skills away.

## How it's built

No table in these mods is written by hand. [`tools/renewal-world-monsters/build_monsters.py`](tools/renewal-world-monsters/build_monsters.py) writes all five mods from rAthena's renewal tables and the CSVs beside it:

```sh
python3 tools/renewal-world-monsters/build_monsters.py --rathena ../rathena            # show the conversion
python3 tools/renewal-world-monsters/build_monsters.py --rathena ../rathena --write    # write the tables
python3 tools/renewal-world-monsters/build_monsters.py --rathena ../rathena --check    # fail if stale
```

It reads the translation and the maps list from a [ragnarokoffline.app](https://github.com/Flux159/ragnarokoffline.app) checkout with its `vendor/` fetched: the one beside this repository, or wherever `RO_APP` points.

[`tools/companion-strategies`](tools/companion-strategies) holds the fight harness, one `mvp-<boss>.party.yml` per boss, the calibration results, and the references written along the way. [`tools/renewal-world-monsters/BALANCING.md`](tools/renewal-world-monsters/BALANCING.md) has the rules for converting a monster. The record of the whole endgame, both repositories, is [docs/RENEWAL_ENDGAME.md](https://github.com/BlaXun/ro-endgame-classes/blob/main/docs/RENEWAL_ENDGAME.md) in ro-endgame-classes.

## Releasing

The five mods are released together and always carry the same version.

1. `python3 tools/package.py --set-version X.Y.Z`
2. Add a `## X.Y.Z` section to [CHANGELOG.md](CHANGELOG.md). It becomes the release notes players read.
3. Commit, then tag `vX.Y.Z` and push the tag.

The [release workflow](.github/workflows/release.yml) builds `<mod>-X.Y.Z.zip` for each mod from the tagged commit and publishes the release. It refuses a tag that doesn't match the mods' version. `python3 tools/package.py` builds the same zips into `dist/` locally.

## Licence

[GPL-3.0](LICENSE), like the app and rAthena, whose tables these are generated from.
