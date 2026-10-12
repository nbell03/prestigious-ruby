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
- Implement a move-based physical/special split.
- Revise Team Magma to feel more compelling without changing the original Ruby progression: at Slateport, Maxie explains the desire for more land for homes, farms, and future generations while acknowledging the risks and believing inaction is worse; at Meteor Falls, he is more calculating, recognizes the meteorite plan's danger, and accepts history may judge him harshly. Strengthen selected major Team Magma battles.
- Keep the intended game design and requested changes documented here as work progresses.

## Current implementation / verification snapshot
- Brandon-related Cave of Origin scripts and dialogue labels are present on `prestigious-ruby-dev`. His current trainer party data has the requested six species (Regirock, Regice, Registeel, Ninjask, Dusclops, Solrock), with levels in the high 60s and custom moves/items. The trainer record is named BRANDON and uses the Champion class.
- The latest known GitHub Actions build checked (run 38193309459, commit `3f5d570f7d584103a00091b933513007b7fd046e`) failed during linking with unresolved symbols for:
  - `CaveOfOrigin_B4F_Text_BrandonIntro`
  - `CaveOfOrigin_B4F_Text_BrandonDefeat`
  - `CaveOfOrigin_B4F_Text_BrandonAfterBattle`
- Root cause identified: `data/event_scripts.s` includes the Cave of Origin B4F scripts but did not include `data/maps/CaveOfOrigin_B4F/text.inc`. Added the missing text include in commit `e77c77b2e8b698982c3b2b039e529d21b4d1469b`; GitHub Actions run 38194037375 is building that fix.
- Bullet Seed and Fury Cutter are already set to 25 base power in `src/data/battle_moves.c` and keep their existing effects (`EFFECT_MULTI_HIT` and `EFFECT_FURY_CUTTER`).
- The move-based physical/special split has not yet been implemented or verified.
- No successful ROM build or patch has been verified yet. Do not describe the game as finished or playable until CI produces a ROM artifact and it is checked.

## Next steps
1. Confirm GitHub Actions run 38194037375 passes after adding the missing dialogue include; fix any next build errors.
2. Fix the Brandon dialogue/linking issue if it persists, then rerun until the build succeeds.
3. Implement and test the move-based physical/special split; audit and refine the Magma storyline dialogue and strengthened major battles.
4. Add/adjust tests and perform a clean build; test key event flow where feasible.
5. Keep this file updated in the same commit as meaningful feature milestones and build/test results.
6. When the user later provides their clean Ruby ROM, create and verify the patch against the matching base revision; never commit or distribute the copyrighted ROM itself.

## Working agreement
- Save meaningful progress frequently with Git commits, and update this file when a milestone changes.
- Be candid about what is implemented, what is only planned, and what has actually passed tests.
- Work happens during active tool-assisted sessions; no build or coding continues in the background between messages.
