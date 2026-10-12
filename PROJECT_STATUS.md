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

## Current implementation / verification snapshot
- Brandon-related Cave of Origin scripts and dialogue labels are present on `prestigious-ruby-dev`. His current trainer party data has the requested six species (Regirock, Regice, Registeel, Ninjask, Dusclops, Solrock), with levels in the high 60s and custom moves/items. The trainer record is named BRANDON and uses the Champion class. This has not yet been verified in-game.
- Fixed a missing assembly include for `data/maps/CaveOfOrigin_B4F/text.inc` in commit `e77c77b2e8b698982c3b2b039e529d21b4d1469b`, which was responsible for unresolved Brandon dialogue labels in an earlier link attempt.
- Bullet Seed and Fury Cutter are set to 25 base power in `src/data/battle_moves.c` and retain `EFFECT_MULTI_HIT` and `EFFECT_FURY_CUTTER`.
- A first implementation of move-based physical/special damage categories was committed in `37e3eed9ee6d8a52a12e90edcc01b97709420981` (`src/calculate_base_damage.c`). It categorizes moves by their Generation IV-style category rather than type, and updates related attack/defense, held-item, weather, and screen handling. This implementation still needs careful review and successful compilation/testing; it is not yet verified as correct.
- GitHub Actions runs for the latest feature commit were still in progress at the last check. The custom build workflow had not reached its compile step yet, so no successful ROM build or ROM artifact has been confirmed.
- Team Magma dialogue needs a focused audit. The Meteor Falls Maxie speech currently contains the land-expansion motivation and willingness to be judged harshly, but the requested later, more calculating response about the meteorite plan's danger still needs to be checked at the correct story event.
- No successful ROM build or patch has been verified. Do not describe the game as finished or playable until CI produces a ROM artifact and it is checked.

## Next steps
1. Check the latest GitHub Actions runs for the physical/special split and missing-dialogue-include fix; address compile/link errors before adding more features.
2. Review the move-category implementation for move coverage and edge cases, including Thick Fat, screens, weather, critical hits, fixed-damage moves, and move/type overrides.
3. Audit the correct Slateport and Meteor Falls story events for Maxie's revised dialogue, then strengthen selected major Team Magma battles without disrupting original progression.
4. Confirm the Brandon event is accessible at the intended Cave of Origin location after the main story and that the encounter is the final postgame boss.
5. Add/adjust tests where feasible, run a clean build, and inspect the produced ROM artifact.
6. When the user later provides their clean Ruby ROM, create and verify the patch against the matching base revision; never commit or distribute the copyrighted ROM itself.
7. Keep this file updated in the same commit as meaningful feature milestones and build/test results.

## Working agreement
- Save meaningful progress frequently with Git commits, and update this file when a milestone changes.
- Be candid about what is implemented, what is only planned, and what has actually passed tests.
- Work happens during active tool-assisted sessions; no build or coding continues in the background between messages.
