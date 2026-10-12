#!/usr/bin/env python3
"""Lightweight source-level regression checks for Pokémon Prestigious Ruby.

These checks do not replace an in-game playthrough, but they catch accidental
reverts of the most important agreed source changes in CI.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
checks = []

def require(label, ok, detail=""):
    checks.append((label, bool(ok), detail))

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

moves = read("src/data/battle_moves.c")
evolutions = read("src/data/pokemon/evolution.h")
trainers = read("src/data/trainer_parties.h")
cave_scripts = read("data/maps/CaveOfOrigin_B4F/scripts.inc")
gym_scripts = read("data/maps/PetalburgCity_Gym/scripts.inc")
flags = read("include/constants/flags.h")
damage = read("src/calculate_base_damage.c")
field_moves = read("data/field_move_scripts.inc")
magma_text = read("data/maps/MeteorFalls_1F_1R/text.inc")

def move_entry(name):
    match = re.search(r"\[" + re.escape(name) + r"\]\s*=\s*\{(.*?)\n\s*\},", moves, re.S)
    return match.group(1) if match else ""

for move, effect in (("MOVE_BULLET_SEED", "EFFECT_MULTI_HIT"),
                     ("MOVE_FURY_CUTTER", "EFFECT_FURY_CUTTER")):
    entry = move_entry(move)
    require(f"{move} has base power 25", bool(re.search(r"\.power\s*=\s*25\b", entry)))
    require(f"{move} keeps its original effect", effect in entry)

for species, level, target in (
    ("SPECIES_ARON", 25, "SPECIES_LAIRON"),
    ("SPECIES_LAIRON", 38, "SPECIES_AGGRON"),
    ("SPECIES_VIBRAVA", 40, "SPECIES_FLYGON"),
    ("SPECIES_SHELGON", 45, "SPECIES_SALAMENCE"),
    ("SPECIES_KADABRA", 36, "SPECIES_ALAKAZAM"),
    ("SPECIES_MACHOKE", 36, "SPECIES_MACHAMP"),
    ("SPECIES_GRAVELER", 36, "SPECIES_GOLEM"),
    ("SPECIES_HAUNTER", 36, "SPECIES_GENGAR"),
    ("SPECIES_ONIX", 36, "SPECIES_STEELIX"),
    ("SPECIES_SCYTHER", 36, "SPECIES_SCIZOR"),
    ("SPECIES_SEADRA", 36, "SPECIES_KINGDRA"),
):
    pattern = rf"\[{species}\]\s*=\s*\{{\{{EVO_LEVEL,\s*{level},\s*{target}\}}"
    require(f"{species} evolves at level {level}", bool(re.search(pattern, evolutions)))

require("Physical/special split classifies moves individually",
        "static bool8 IsMovePhysical" in damage and "static bool8 IsMoveSpecial" in damage)
physical_cases = damage[damage.find("static bool8 IsMovePhysical"):damage.find("static bool8 IsMoveSpecial")]
special_cases = damage[damage.find("static bool8 IsMovePhysical"):damage.find("s32 CalculateBaseDamage")]
for move in ("MOVE_FIRE_PUNCH", "MOVE_WATERFALL", "MOVE_BULLET_SEED",
             "MOVE_THUNDER_PUNCH", "MOVE_ICE_PUNCH", "MOVE_DRAGON_CLAW",
             "MOVE_BITE", "MOVE_SHADOW_PUNCH", "MOVE_METAL_CLAW"):
    require(f"{move} is classified physical", f"case {move}:" in physical_cases)
for move in ("MOVE_SHADOW_BALL", "MOVE_SLUDGE_BOMB", "MOVE_HYPER_BEAM",
             "MOVE_ICY_WIND", "MOVE_DRAGON_BREATH", "MOVE_TWISTER",
             "MOVE_HIDDEN_POWER", "MOVE_WEATHER_BALL"):
    require(f"{move} is classified special", f"case {move}:" in special_cases)
require("Brandon encounter is gated behind game clear",
        "CaveOfOrigin_B4F_EventScript_UpdateBrandonVisibility" in cave_scripts
        and "FLAG_SYS_GAME_CLEAR" in cave_scripts
        and "FLAG_DEFEATED_BRANDON_CAVE_OF_ORIGIN" in cave_scripts)
require("Brandon battle uses Steven's original encounter slot",
        "CaveOfOrigin_B4F_EventScript_Brandon::" in cave_scripts
        and "trainerbattle_no_intro TRAINER_STEVEN" in cave_scripts)
require("Brandon encounter has intro and post-battle dialogue",
        "CaveOfOrigin_B4F_Text_BrandonIntro" in cave_scripts
        and "CaveOfOrigin_B4F_Text_BrandonAfterBattle" in cave_scripts)
require("Team Magma dialogue retains land goal",
        "homes of future generations" in magma_text)
require("Team Magma dialogue references Maxie and the meteorite",
        "MAXIE" in magma_text and "METEORITE" in magma_text)
brandon_party_start = trainers.find("gTrainerParty_Steven[]")
brandon_party = trainers[brandon_party_start:brandon_party_start + 4000]
require("Brandon party definition exists", brandon_party_start >= 0)
for species in ("SPECIES_REGIROCK", "SPECIES_REGICE", "SPECIES_REGISTEEL",
                "SPECIES_NINJASK", "SPECIES_DUSCLOPS", "SPECIES_SOLROCK"):
    require(f"Brandon party includes {species}", species in brandon_party)

require("HM field scripts retain badge progression checks",
        "CannotUseCut" in field_moves and "CannotUseRockSmash" in field_moves
        and "FLAG_BADGE01_GET" in field_moves and "FLAG_BADGE03_GET" in field_moves)
require("Absol event and one-time state flag are present",
        "SPECIES_ABSOL, 5, ITEM_NONE" in gym_scripts
        and "VAR_PETALBURG_GYM_STATE, 2" in gym_scripts
        and "PetalburgCity_Gym_EventScript_ReturnFromWallyTutorial" in gym_scripts)

failed = 0
for label, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    failed += not ok
print(f"\n{len(checks) - failed}/{len(checks)} source checks passed.")
sys.exit(1 if failed else 0)
