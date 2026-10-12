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
cave_map = read("data/maps/CaveOfOrigin_B4F/map.json")
gym_scripts = read("data/maps/PetalburgCity_Gym/scripts.inc")
flags = read("include/constants/flags.h")
damage = read("src/calculate_base_damage.c")
field_moves = read("data/field_move_scripts.inc")
field_avatar = read("src/field_control_avatar.c")
pokemon_menu = read("src/pokemon_menu.c")
surf_script = read("data/scripts/surf.inc")
magma_text = read("data/maps/MeteorFalls_1F_1R/text.inc")
slateport_magma_text = read("data/maps/SlateportCity_OceanicMuseum_2F/text.inc")
slateport_magma_scripts = read("data/maps/SlateportCity_OceanicMuseum_2F/scripts.inc")

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
    ("SPECIES_SLOWPOKE", 36, "SPECIES_SLOWKING"),
    ("SPECIES_POLIWHIRL", 36, "SPECIES_POLITOED"),
    ("SPECIES_CLAMPERL", 36, "SPECIES_HUNTAIL"),
    ("SPECIES_CLAMPERL", 36, "SPECIES_GOREBYSS"),
    ("SPECIES_PORYGON", 36, "SPECIES_PORYGON2"),
):
    start = evolutions.find(f"[{species}]")
    end = evolutions.find("\n    [SPECIES_", start + 1)
    block = evolutions[start:end] if start >= 0 and end >= 0 else ""
    pattern = rf"EVO_LEVEL,\s*{level},\s*{target}"
    require(f"{species} evolves at level {level}", bool(re.search(pattern, block)))

require("No trade-triggered evolution methods remain", "EVO_TRADE" not in evolutions)

physical_start = damage.find("static bool8 IsMovePhysical")
special_start = damage.find("static bool8 IsMoveSpecial", physical_start)
calc_start = damage.find("s32 CalculateBaseDamage", special_start)
physical_cases = damage[physical_start:special_start]
physical_override_end = damage.find("// Special moves whose types were physical before Generation IV.", physical_start)
physical_overrides = damage[physical_start:physical_override_end]
special_override_start = physical_override_end
special_override_end = damage.find("return FALSE;", special_override_start)
special_overrides = damage[special_override_start:special_override_end]

require("Light Ball boosts both Pikachu attacking stats under the split",
        "HOLD_EFFECT_LIGHT_BALL" in damage
        and "attack *= 2;" in damage[damage.find("HOLD_EFFECT_LIGHT_BALL"):damage.find("HOLD_EFFECT_THICK_CLUB")]
        and "spAttack *= 2;" in damage[damage.find("HOLD_EFFECT_LIGHT_BALL"):damage.find("HOLD_EFFECT_THICK_CLUB")])

require("Hidden Power remains special regardless of type",
        "case MOVE_HIDDEN_POWER:" in special_overrides
        and "default:" in physical_cases and "return type < TYPE_MYSTERY;" in physical_cases)

require("Physical/special split classifies moves individually",
        "static bool8 IsMovePhysical" in damage and "static bool8 IsMoveSpecial" in damage)
require("Special category is the inverse of physical category",
        "return type != TYPE_MYSTERY && !IsMovePhysical(move, type);" in damage)
physical_move_overrides = set(re.findall(r"case (MOVE_[A-Z0-9_]+):", physical_overrides))
special_move_overrides = set(re.findall(r"case (MOVE_[A-Z0-9_]+):", special_overrides))
require("No move is explicitly listed in both category override groups",
        physical_move_overrides.isdisjoint(special_move_overrides))
for move in ("MOVE_FIRE_PUNCH", "MOVE_WATERFALL", "MOVE_BULLET_SEED",
             "MOVE_VINE_WHIP", "MOVE_NEEDLE_ARM", "MOVE_LEAF_BLADE",
             "MOVE_THUNDER_PUNCH", "MOVE_SPARK", "MOVE_VOLT_TACKLE",
             "MOVE_ICE_PUNCH", "MOVE_ICE_BALL", "MOVE_DRAGON_CLAW",
             "MOVE_OUTRAGE", "MOVE_BITE", "MOVE_CRUNCH", "MOVE_PURSUIT",
             "MOVE_THIEF", "MOVE_KNOCK_OFF", "MOVE_SHADOW_PUNCH",
             "MOVE_LICK", "MOVE_ASTONISH", "MOVE_METAL_CLAW",
             "MOVE_STEEL_WING", "MOVE_POISON_FANG", "MOVE_POISON_TAIL"):
    require(f"{move} is classified physical", f"case {move}:" in physical_overrides)
for move in ("MOVE_SHADOW_BALL", "MOVE_SLUDGE_BOMB", "MOVE_HYPER_BEAM",
             "MOVE_RAZOR_WIND", "MOVE_SONIC_BOOM", "MOVE_SWIFT",
             "MOVE_GUST", "MOVE_TRI_ATTACK", "MOVE_HYPER_VOICE",
             "MOVE_UPROAR", "MOVE_WEATHER_BALL", "MOVE_AIR_CUTTER",
             "MOVE_ACID", "MOVE_SLUDGE", "MOVE_SMOG", "MOVE_MUD_SLAP",
             "MOVE_MUD_SHOT", "MOVE_SNORE", "MOVE_SILVER_WIND",
             "MOVE_SIGNAL_BEAM", "MOVE_ANCIENT_POWER", "MOVE_DOOM_DESIRE"):
    require(f"{move} is classified special", f"case {move}:" in special_overrides)
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
require("Brandon map object uses the intended Cave of Origin slot",
        '"script": "CaveOfOrigin_B4F_EventScript_Brandon"' in cave_map
        and '"flag": "FLAG_HIDE_BRANDON_CAVE_OF_ORIGIN"' in cave_map)
require("Slateport Maxie speech explains the land goal",
        "People need land for homes, farms" in slateport_magma_text
        and "generations who will follow us" in slateport_magma_text)
require("Slateport Maxie speech acknowledges risk and inaction",
        "earth has a delicate balance" in slateport_magma_text
        and "cost is greater than the danger" in slateport_magma_text)
require("Slateport Maxie speech is connected to its event",
        "SlateportCity_OceanicMuseum_2F_Text_MaxieWarning" in slateport_magma_scripts)
require("Meteor Falls Maxie dialogue references the meteorite",
        "MAXIE" in magma_text and "METEORITE" in magma_text
        and "history remembers me as a villain" in magma_text)

# Late Maxie is a key Ruby antagonist battle and should remain a meaningful challenge.
for party, levels in (("Tabitha1", (34, 34, 36)), ("Courtney2", (42, 42))):
    start = trainers.find(f"gTrainerParty_{party}[] = {{")
    end = trainers.find("\n};", start)
    block = trainers[start:end] if start >= 0 and end >= 0 else ""
    found_levels = tuple(int(level) for level in re.findall(r"\.level = (\d+),", block))
    require(f"Team Magma admin party {party} has revised levels", found_levels == levels)

maxie2_start = trainers.find("gTrainerParty_Maxie2[] = {")
maxie2_end = trainers.find("\n};", maxie2_start)
maxie2_party = trainers[maxie2_start:maxie2_end] if maxie2_start >= 0 and maxie2_end >= 0 else ""
for species, level in (("SPECIES_MIGHTYENA", 45),
                       ("SPECIES_CROBAT", 45),
                       ("SPECIES_CAMERUPT", 48)):
    require(f"Late Maxie battle has {species} at level {level}",
            f".level = {level},\n\t.species = {species}" in maxie2_party)
brandon_party_start = trainers.find("gTrainerParty_Steven[]")
brandon_party = trainers[brandon_party_start:brandon_party_start + 4000]
require("Brandon party definition exists", brandon_party_start >= 0)
for species in ("SPECIES_REGIROCK", "SPECIES_REGICE", "SPECIES_REGISTEEL",
                "SPECIES_NINJASK", "SPECIES_DUSCLOPS", "SPECIES_SOLROCK"):
    require(f"Brandon party includes {species}", species in brandon_party)

require("HM obstacle scripts preserve badge and HM acquisition gates",
        "FLAG_BADGE01_GET" in field_moves and "FLAG_RECEIVED_HM01" in field_moves
        and "FLAG_BADGE03_GET" in field_moves and "FLAG_RECEIVED_HM06" in field_moves
        and "FLAG_BADGE04_GET" in field_moves and "FLAG_RECEIVED_HM04" in field_moves)
require("Field HM scripts do not require a Pokemon to know the HM",
        "checkpartymove" not in field_moves and "checkpartymove MOVE_SURF" not in surf_script)
require("Surf, Dive, and Waterfall preserve acquisition gates",
        "FLAG_RECEIVED_HM_SURF" in field_avatar
        and "FLAG_RECEIVED_HM08" in field_avatar
        and "ITEM_HM07_WATERFALL" in field_avatar)
require("Contextual party-menu HMs preserve badge gates",
        "FLAG_BADGE05_GET" in pokemon_menu
        and "FLAG_BADGE06_GET" in pokemon_menu
        and "FLAG_BADGE07_GET" in pokemon_menu
        and "FLAG_BADGE08_GET" in pokemon_menu
        and "FLAG_BADGE02_GET" in pokemon_menu)
require("Absol event and one-time state flag are present",
        "SPECIES_ABSOL, 5, ITEM_NONE" in gym_scripts
        and "VAR_PETALBURG_GYM_STATE, 2" in gym_scripts
        and "PetalburgCity_Gym_EventScript_ReturnFromWallyTutorial" in gym_scripts)

# The later rival encounter has a fully evolved starter in each starter matchup.
for party, species in (("Brendan10", "SPECIES_SCEPTILE"),
                       ("Brendan11", "SPECIES_BLAZIKEN"),
                       ("Brendan12", "SPECIES_SWAMPERT"),
                       ("May10", "SPECIES_SCEPTILE"),
                       ("May11", "SPECIES_BLAZIKEN"),
                       ("May12", "SPECIES_SWAMPERT")):
    start = trainers.find(f"gTrainerParty_{party}[] = {{")
    end = trainers.find("\n};", start)
    block = trainers[start:end] if start >= 0 and end >= 0 else ""
    require(f"Later rival party {party} has fully evolved starter",
            species in block and ".level = 38" in block)

failed = 0
for label, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    failed += not ok
print(f"\n{len(checks) - failed}/{len(checks)} source checks passed.")
sys.exit(1 if failed else 0)
