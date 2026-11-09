# Date-first GvG data

Scope: `qxwd565/Goblins-Vs-Gnomes`, all 143 existing API IDs (123 collectible cards and 20 generated tokens, choices and Spare Parts). The migration source is `0149620ba64f983ef09e715452d7581e3870b5fb`. No other expansion, plugin, site, database, source URL or import configuration is changed.

## Canonical representation

Every `data/<CARD_ID>.json` keeps its filename and uses ascending KST date keys. The first key is the available release gameplay baseline. Later keys contain only changed fields. All 55 prior events are preserved. Four proven secondary-race events move from 2022-11-30 to 2023-02-15; the other 51 dates remain unchanged. Eight existing events also receive a sourced keyword-ability delta. Actual field names such as `cost` are unchanged.

- An omitted later field inherits its previous value.
- `__remove: ["field"]` removes an attribute, and cannot overlap a value written in the same record.
- Zero, false, null, empty strings and empty lists remain values rather than removals. Objects and lists replace the prior entire field.
- Source exporter placeholders for absent race/races/school are excluded from exact states but retained in original evidence and the compatibility projection.
- The 100 minions retain attack/health, 38 spells have no invented attack/health/durability/armor, and five weapons retain their genuine attack/durability. Weapon health mirrors exist only in the old-client projection.
- A real zero, such as Vitality Totem's attack or Gallywix's Coin's cost, stays zero. There is no truthiness-based zero substitution.
- Display text uses exactly `<br></br>`. Raw native/archive text stays verbatim.
- Later tribes and schools are not backdated. Neptulon gains Elemental on 2017-04-05, schools begin 2021-03-26, and the four affected Mechs gain Beast on 2023-02-15.

`fold` is exact chronological replay and returns no card before its first date. `resolve` also preserves the general estimated/pending confidence behavior. These 143 release dates are verified, but no entire baseline is promoted to fully verified. Strict historical resolution rejects partially verified baselines.

## What the dates mean

The selected rule is actual normal constructed-match availability in Korea. All 143 records retain **2014-12-10**, when cards could be acquired/crafted for normal decks; generated tokens, choices and Spare Parts follow their producing cards. The earlier Arena preview, demos and client preload do not establish this date.

`tools/gvg-date-recheck.json` records the official Korean live announcement, the December 9 to 10 delay, the separately described Arena preview and targeted patch rechecks. It preserves the 2023-09-07 live health change for Soot Spewer: original GVG_123 still had 3 health in 27.2, while WON_033 had 4. The 27.2.2 client/collection fix was not yet the in-game server fix. The comparison test explicitly records that discrepancy rather than converting a client observation into a live date.

The four cards Anodized Robo Cub (GVG_030), Mech-Bear-Cat (GVG_034), Metaltooth Leaper (GVG_048) and Explosive Sheep (GVG_076) gained Beast in 25.4, not the initial 25.0 dual-type framework. Their event dates are corrected from 2022-11-30 to **2023-02-15 KST** in canonical and both transports. Official Korean 25.4 notes, a live announcement at 2023-02-14T18:04:43.156Z (February 15 KST), a contemporary four-card list and exact 25.4 tags establish the date. Actual 25.0 lacks their secondary race while other entities already carry secondary tags; this is not a universal export omission. The original 55-event documents remain untouched in sidecars. Only these 4 IDs' race history intentionally differs from the prior root behavior during the corrected interval.

Mechwarper's Wild ban on 2023-09-29 and unban on 2024-03-12 are separately sourced format-availability observations. They do not become numeric spec changes or a universal card-hiding filter. Exact Ship's Cannon 4.1 Korean cosmetic-text timing remains unresolved between December 5 and 6; no date is invented.

## Lossless source and uncertainty

Each `metadata/<ID>.json` preserves the complete `originalSource`, pinned `sourceCommit`, unchanged `currentCatalog`, relationships, English name, raw/native tags and text, assets, prior patch sources, baseline confidence and observations. Every pre-existing non-output JSON evidence file stays byte-identical. Current-only fields are not dated as if they existed at release. Precise render labels use each card’s full current-only field set. The original `chooseOne` flag is true on three parent cards and false on 140 other source records; it is absent from all 143 old current-catalog records. Canonical and precise gameplay preserve all three true and 140 false values unchanged. The root retains its endpoint-specific absence.

All 143 baseline statuses remain `partially-verified`. The 99 existing exact initial Korean text discrepancies remain explicit; 44 matching initial descriptions do not establish complete intermediate cosmetic history. Raw observations and their ranges stay available without fabricated patch dates.

V-07-TR-0N's inherited `rarity: null` is explicitly **provisional/unknown historical reconstruction**, not verified historical absence. Release through sampled 9.0 has raw rarity tag 203=5 (Legendary), while sampled 10.0 onward lacks that tag. Its exact Korean transition and token-display semantics remain unresolved. Field-specific uncertainty is recorded in its sidecar; no null-to-absence conversion or invented rarity patch is made.

## Bounded keyword-ability lists

The original GvG source and current catalog omitted `mechanics` on every record. Canonical and precise outputs now contain a bounded, documented list of verifiable intrinsic keyword abilities and targeting restrictions. This is not a complete executable description of every free-text effect or an exhaustive list of engine flags. An empty list means no recognized keyword in this vocabulary, not that the card has no effect.

`tools/gvg-keyword-abilities.json` defines this vocabulary and the eight existing dated events that change it. `tools/gvg-mechanics-evidence.json` separately retains actual XML `Tag` and `ReferencedTag` observations across 32 selected builds, 4,576 card/build observations. Sidecars retain compressed observation ranges for implementation flags too. A referenced keyword is not automatically an intrinsic ability: Coghammer grants Divine Shield/Taunt, and Wee Spellstopper grants Elusive to adjacent minions.

Conversely, XML child type is not a universal semantic oracle. V-07-TR-0N's own release text explicitly says Mega-Windfury and four attacks, and every selected text observation retains that ability. Neither release nor current has actual WINDFURY 189 or MEGA_WINDFURY 1207; current uses a ReferencedTag. The complete narrow extract is in `tools/gvg-voltron-extract.json`. This text-backed exception is distinguished from keywords merely granted to another card. Anodized Robo Cub, Grove Tender and Dark Wispers likewise explicitly have their own Choose One keyword in release text, before their dedicated 443 tag appears in sampled XML. The original source `chooseOne` boolean is true on these three parents and false on the other 140 records, including all six generated choice entities. All 143 values agree with the latest actual 443 tag presence. The old current catalog omits this field on every record. Canonical and precise records retain this existing field and all 3 true / 140 false values, while root compatibility continues to omit it. The three true release baselines are supported by their own release text and option relationships; latest engine tags alone are not treated as release-date proof. Genuine false values are not discarded or converted to absence.

Important dated distinctions:

- Mistress of Pain's pre-existing healing is not backdated as the named Lifesteal keyword. Lifesteal appears on 2017-08-09. The official note also changes certain Auchenai interactions; keyword replacement does not establish identical behavior in every interaction.
- Warbot's Enrage keyword disappears on 2018-04-11, while its conditional attack effect remains. Raw ENRAGED tag persistence is separately observed.
- Burrowing Mine's Casts When Drawn wording is dated 2018-10-03 even though its dedicated tag appears later in the selected samples. Flame Leviathan's later engine tag of the same name does not make it a spell carrying that displayed keyword.
- 27.2 adds Flame Leviathan's Rush, Iron Juggernaut's Deathrattle and Soot Spewer's Battlecry, and removes King of Beasts' Battlecry. Soot Spewer retains Spell Damage while its health fix is dated separately.
- Arcane Nullifier's two targeting restrictions become the Elusive keyword on 2024-03-12. The restriction already existed before the keyword. Wee Spellstopper does not gain intrinsic Elusive.

Fluctuating AURA/TRIGGER_VISUAL indicators are retained as implementation observations rather than invented gameplay changes. This GvG vocabulary is narrower than earlier sets' sourced engine-marker lists: callers must not interpret mechanics as a cross-set exhaustive rule engine. No unknown engine-flag transition date is asserted.

The five GvG source weapons already contain genuine durability. Some later archives encode it in HEALTH/tag 45 rather than DURABILITY/tag 187; the test recognizes that proven per-weapon/build representation only. No Legacy-specific weapon decoder is applied to canonical input.

## Dual root transports

All six bundles are siblings, preserving existing `art/<ID>` URL bases.

Old clients continue using schema 1:

- `cards.json`: generated current catalog, byte-identical to the pinned source.
- `render.json`: current rendering data and ordinary sparse reverse intervals.
- `history.json`: DBF-keyed `id`/`history` contract.

Precise clients explicitly opt into:

- `cards-date.json`: current type-specific state, reconstructed keyword lists and separately retained current-only metadata.
- `render-date.json`: `historySchema: 2`, explicit removal operations, confidence and current-only labels.
- `history-date.json`: complete authoritative current gameplay for all 143 IDs and disjoint reverse intervals.

The four reviewed historical race-date corrections apply to root and precise intervals, without changing the current root catalog. The postponed old plugin must not be pointed at the precise endpoints. Its whitelist cannot represent arbitrary removals, field presence or a complete authoritative snapshot. The compatibility projection restores zero/empty sentinels and weapon health mirrors, and omits mechanics only because all pinned GvG records originally omitted it. Precise output continues to reflect future approved canonical changes; there is no frozen whole-state fallback.

Old-client before-release fallback remains unchanged, with no new mass hiding or strict gate. Installed current nativeTags can still affect an old renderer. These deliberate losses are documented in `tools/legacy-compatibility-losses.json`.

## Rebuild and verification

From the repository root:

1. `python3 tools/migrate-date-schema.py`
2. `python3 tools/build-api.py`
3. `python3 tools/test-gvg-history.py`
4. `python3 tools/test-date-schema.py`
5. `python3 tools/test-gvg-mechanics.py`
6. `python3 tools/test-legacy-compatibility.py`
7. `python3 tools/test-build-idempotence.py`
8. `python3 tools/test-clean-migration.py`
9. `git diff --check`

Primary-tag evidence can be re-extracted with `python3 tools/extract-gvg-mechanics.py --archive-dir /path/to/local/CardDefs/archives` (repeat `--archive-dir` for additional directories). The saved source URLs and full XML SHA256 hashes identify the exact 32 snapshots; this optional extractor does not download them.

The historical wrapper builder remains read-only as `tools/wrapper_api_reference.py`; its writer is disabled. CI uses the local builder, preserves the existing read-only validation workflow, and checks out full history with `fetch-depth: 0`. Source-preservation checks fail explicitly when the pinned source is missing, rather than skipping verification.

Checks cover 143 original documents, all 55 events, 8,580 all-card/global-date precise cases, 8,580 old-consumer cases (including 12 explicitly corrected race-history cases), 4,147 retained numeric observations and 4,576 freshly extracted numeric/type/class/race/school/ability observations. The latter cover the same original 29 builds plus selected 25.0, 25.4 and 29.0 snapshots, not 8,723 independent snapshots. All 762 artwork/golden files and 858 bundle-relative art URL checks are preserved. Clean pinned-source regeneration reproduces 292 canonical/sidecar/bundle files byte-for-byte. Fixtures cover null, zero, emptiness, absence, removal, identity protection and all supported card-type transitions.

For the unchanged PHP parser, generate a fixture with `python3 tools/test-legacy-compatibility.py --fixture /tmp/gvg-compatibility.json`, then run `php tools/test-legacy-plugin.php /path/to/unmodified/plugin /tmp/gvg-compatibility.json`. The offline harness compares all 143 imported records to the original import, checks assets, and tests all 8,580 date cases. Local validation uses PHP WASM 8.5.12 and passes 8,581 checks (8,580 historical cases plus original import equality). The pinned unmodified plugin source is `78ce6fdc4e70f689880a70d6f22aa77a6c75e337`. This is not a live browser, WordPress, database or deployment test.

These checks are bounded evidence, not exhaustive every-build, exact-wording, artwork, temporary-format-legality or rule-engine bug chronology. Migration success does not promote incomplete historical baselines. Future approved gameplay changes require reviewing the expected-difference tests rather than freezing current output.
