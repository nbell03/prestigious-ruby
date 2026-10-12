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
- The current evolution table already contains the requested Aron/Lairon/Aggron, Vibrava/Flygon, and Shelgon/Salamence levels, and several standard trade evolutions already use level 36. Audit every trade-based evolution, especially held-item trade evolutions, for complete coverage. These values have not yet been validated in a successful ROM build.
- The Absol gift event is present in `data/maps/PetalburgCity_Gym/scripts.inc`: Norman gives a level-5 Absol after Wally's tutorial, and the gym-state variable prevents repeat gifts. The script uses `givemon`, which routes a gift to storage when the party is full; this still needs gameplay verification.
- HM access is being changed so Cut, Rock Smash, and Strength obstacle interactions no longer require a matching move in the party, while badge checks remain. Surf, Fly, Flash, Dive, and Waterfall are being exposed contextually from the party menu and use the selected Pokémon only for animation.
- A clean source build succeeded on commit `be1384e9be7897363ca7903604949f70e77355da` (Actions run [38194767589](https://github.com/nbell03/prestigious-ruby/actions/runs/38194767589)); it produced a ROM artifact. The workflow is being changed to verify builds without uploading the full copyrighted ROM. No patch has been created or verified yet.

## Next steps
1. Run CI on the HM-access changes, confirm the source still builds, and inspect the output-check step.
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
