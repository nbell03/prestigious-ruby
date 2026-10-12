# Pokémon Prestigious Ruby — Project Status

Last updated: 2026-10-11

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
- Revise the Team Magma storyline as agreed in the project conversation; verify the detailed agreed beats against prior project notes before marking complete.
- Keep the intended game design and requested changes documented here as work progresses.

## Current implementation / verification snapshot
- Brandon-related Cave of Origin scripts and dialogue labels are present on `prestigious-ruby-dev`.
- The latest known GitHub Actions build checked (run 38193309459, commit `3f5d570f7d584103a00091b933513007b7fd046e`) failed during linking with unresolved symbols for:
  - `CaveOfOrigin_B4F_Text_BrandonIntro`
  - `CaveOfOrigin_B4F_Text_BrandonDefeat`
  - `CaveOfOrigin_B4F_Text_BrandonAfterBattle`
- Those three labels are present in the current branch's `data/maps/CaveOfOrigin_B4F/text.inc`, so the next step is to trigger/re-run the build on the current branch head and determine whether the old failure is stale or whether the map text is not being linked correctly.
- No successful ROM build or patch has been verified yet. Do not describe the game as finished or playable until CI produces a ROM artifact and it is checked.

## Next steps
1. Re-run CI against the current branch head and inspect the complete build log.
2. Fix the Brandon dialogue/linking issue if it persists, then rerun until the build succeeds.
3. Audit actual source changes for each requested feature (Magma story, physical/special split, move power/behavior, postgame progression, Brandon battle/team, visibility/defeat flags).
4. Add/adjust tests and perform a clean build; test key event flow where feasible.
5. Keep this file updated in the same commit as meaningful feature milestones and build/test results.
6. When the user later provides their clean Ruby ROM, create and verify the patch against the matching base revision; never commit or distribute the copyrighted ROM itself.

## Working agreement
- Save meaningful progress frequently with Git commits, and update this file when a milestone changes.
- Be candid about what is implemented, what is only planned, and what has actually passed tests.
- Work happens during active tool-assisted sessions; no build or coding continues in the background between messages.
