# Pokémon Prestigious Ruby — Project Status

Last updated: 2026-10-12

## Source of truth
- Repository: https://github.com/nbell03/prestigious-ruby
- Active development branch: `prestigious-ruby-dev`
- Keep all game source changes and this status file committed to this repository. Do not rely on chat history as the only record.
- Secondary presentation/README repository: https://github.com/nbell03/Pokemon-Prestigious-Ruby

## Confirmed design requirements
- Project title: **Pokémon Prestigious Ruby**.
- Build from the Ruby decompilation source; produce a buildable ROM and, once verified, a patch that requires the user's own clean Ruby ROM.
- Brandon is the final postgame boss, located in Cave of Origin in the Steven-like encounter spot after the main story.
- Brandon's team: Regirock, Regice, Registeel, Ninjask, Dusclops, and Solrock.
- Remove Battle Frontier progression; Brandon's Cave of Origin battle is the final postgame boss.
- Bullet Seed and Fury Cutter have 25 base power while retaining their original multi-hit / consecutive-use behavior.
- Use a move-based physical/special split rather than the Generation III type-based categories.
- Revise Team Magma to feel more compelling without changing the original Ruby progression: at Slateport, Maxie explains the desire for more land for homes, farms, and future generations while acknowledging the risks and believing inaction is worse; at Meteor Falls, he is more calculating, recognizes the meteorite plan's danger, and accepts history may judge him harshly. Strengthen selected major Team Magma battles.

## Additional confirmed design requirements (2026-10-12)
- After Wally's Pokémon-catching tutorial, Norman gives the player an Absol at level 5. The gift must be one-time only and handle a full party safely.
- Field HMs can be used outside battle without requiring a party Pokémon to know the specific HM. Preserve obstacle and badge progression; this is not permission to bypass world gates.
- Evolution levels: Aron -> Lairon at 25; Lairon -> Aggron at 38; Vibrava -> Flygon at 40; Shelgon -> Salamence at 45.
- All trade evolutions become level-36 evolutions, including trade evolutions that normally require a held item and a trade.

## Current implementation / verification snapshot
- Brandon-related Cave of Origin scripts and dialogue labels are present on `prestigious-ruby-dev`. His current trainer party data has the requested six species (Regirock, Regice, Registeel, Ninjask, Dusclops, Solrock), with levels in the high 60s and custom moves/items. The trainer record is named BRANDON and uses the Champion class. This has not yet been verified in-game.
- Fixed a missing assembly include for `data/maps/CaveOfOrigin_B4F/text.inc` in commit `e77c77b2e8b698982c3b2b039e529d21b4d1469b`, which was responsible for unresolved Brandon dialogue labels in an earlier link attempt.
- Bullet Seed and Fury Cutter are set to 25 base power in `src/data/battle_moves.c` and retain `EFFECT_MULTI_HIT` and `EFFECT_FURY_CUTTER`.
- A first implementation of move-based physical/special damage categories is in `src/calculate_base_damage.c`; it switches key Gen III moves to their Generation IV-style categories and updates related attack/defense, held-item, weather, and screen handling. A successful clean build was verified on commit `96009ac0b41ccb561645e791de25257d3d012915` (Actions run [38194470484](https://github.com/nbell03/prestigious-ruby/actions/runs/38194470484)). The category table still needs coverage review and gameplay testing.
- GitHub Actions runs for the latest feature commit were still in progress at the last check. The custom build workflow had not reached its compile step yet, so no successful ROM build or ROM artifact has been confirmed.
- Updated Maxie's Slateport warning to explain the need for land for homes, farms, and future generations, while acknowledging the risk to nature and the cost of inaction. Updated his Meteor Falls speech to address the meteorite's uncertain power and his willingness to accept historical blame. These text changes still need in-game verification.
- Evolution audit: the requested levels are present (Aron 25, Lairon 38, Vibrava 40, Shelgon 45). The Ruby evolution table also has the Gen III trade-based evolutions converted to Level 36, including item-assisted trade lines represented in Ruby (Slowpoke, Onix, Scyther, Seadra, and Clamperl branches). This is a source review only; full in-game evolution testing remains outstanding.
- The Absol gift event is present in `data/maps/PetalburgCity_Gym/scripts.inc`: Norman gives a level-5 Absol after Wally's tutorial, and the gym-state variable prevents repeat gifts. The script uses `givemon`, which routes a gift to storage when the party is full; this still needs gameplay verification.
- HM access is being changed so Cut, Rock Smash, and Strength obstacle interactions no longer require a matching move in the party, while badge checks remain. Surf, Fly, Flash, Dive, and Waterfall are being exposed contextually from the party menu and use the selected Pokémon only for animation.
- A clean source build succeeded on commit `be1384e9be7897363ca7903604949f70e77355da` (Actions run [38194767589](https://github.com/nbell03/prestigious-ruby/actions/runs/38194767589)). That historical run uploaded a temporary test-ROM artifact; the current `.github/workflows/prestigious-build.yml` no longer includes a ROM-upload step, so future verification runs should not publish the full ROM. No patch has been created or verified yet.

- Added `tools/check_prestigious_features.py` and wired it into `.github/workflows/prestigious-build.yml`. The checks cover move power/effects, selected evolution levels and trade evolutions, the physical/special helper functions, Brandon's story gate/dialogue/party species, HM badge gates, Absol's level-5 gift, and key Team Magma dialogue. The checks have been committed, but no CI result is available yet; source-text checks do not substitute for playing the ROM.
- Recent development commits on `prestigious-ruby-dev`: `a40b0686` (source regression checks), `57eb996a` (CI integration), `0e241c31` (correct Absol test), and `fd8eb846` (expanded Brandon/Magma coverage). Save after each coherent change and update this status file frequently.
- Current CI status for the newest commit is not confirmed; the commit-status endpoint returned no status records, so do not claim these checks passed.

- Physical/special split audit advanced: expanded the regression script to check representative moves that changed category in Generation IV (physical Fire/Water/Grass/Electric/Ice/Dragon/Dark/Ghost/Steel/Poison and special Normal/Flying/Poison/Ground/Ghost/Bug moves). Corrected the special-category tests to check only moves that actually require explicit reclassification; unchanged Ice/Dragon special moves correctly fall through to the type default. These checks are committed but still need a successful CI run and gameplay validation.
- Latest source-test commits: `32e84501` (expand split coverage) and `b93741f8` (correct the tested move list). Continue frequent saves after each focused change.
- Fastest-path-to-testing update: GitHub Actions runs are now active for the latest branch. The Prestigious Ruby build has checked out source and installed the GBA dependencies; the actual ROM compilation is in progress. The repository's upstream CI is also running. Neither run has reported a result yet, and no patch artifact is available.
- Added source regression coverage for additional level-36 trade evolutions: Slowpoke -> Slowking, Poliwhirl -> Politoed, and Clamperl -> Huntail, alongside the existing list. Commit: `33df9f5a`.
- Next release milestone: get the custom branch's build and source checks green, then make a BPS patch from the built ROM against a clean matching Ruby 1.0 base. Do not upload the complete copyrighted ROM as a workflow artifact; keep only the patch and verification metadata.

- User preference clarified: do not invite or ask the user to test interim builds; they want to wait until Prestigious Ruby is finished. Continue building and validate internally before announcing a finished test-ready patch.
- Added a first balance pass to the late rival battles in `src/data/trainer_parties.h`: all three starter matchups for the late Brendan/May party variants now use the fully evolved starter (Sceptile, Blaziken, or Swampert) at level 38, with supporting party members raised from levels 31/32 to 35/36. Commit: `7425f689`.
- Added regression checks for the fully evolved starter in all six late rival party variants. Commit: `c897c721`. These tests and the latest build still require CI confirmation; do not treat the party changes as playtested.
- Latest build run `38195719134` failed at C compilation because `ITEM_HM07_WATERFALL` was not visible in `src/field_control_avatar.c`; the same item constant is used in `src/pokemon_menu.c`. The next commit adds explicit `constants/items.h` includes to both files. No successful build of the HM-access changes is confirmed yet.

- Regression script correction: fixed the new late-rival party check so it correctly extracts each party block before checking its evolved starter and level. Commit: `c653599d`.
- User explicitly does not want to test interim builds. Do not suggest testing until the feature list is finished, the latest source checks pass, and a verified patch is available.

## Next steps
1. Trigger CI on the current branch tip and confirm the current workflow builds successfully without publishing the full ROM.
2. Review the move-category implementation for move coverage and edge cases, including Thick Fat, screens, weather, critical hits, fixed-damage moves, and move/type overrides.
3. Verify Maxie's revised Slateport and Meteor Falls dialogue in-game and audit the existing strengthened Maxie battle levels; preserve original story progression.
4. Confirm the Brandon event is accessible at the intended Cave of Origin location after the main story and that the encounter is the final postgame boss.
5. Review all eight HMs, badge gates, contextual menu behavior, and evolution branches; test in-game where feasible.
6. When the user later provides their clean Ruby ROM, create and verify a patch against the matching base revision; do not upload or distribute the full ROM.
7. Keep this file updated in the same commit as meaningful feature milestones and build/test results.

## Working agreement
- Save meaningful progress frequently with Git commits, and update this file when a milestone changes.
- Be candid about what is implemented, what is only planned, and what has actually passed tests.
- Work happens during active tool-assisted sessions; no build or coding continues in the background between messages.
