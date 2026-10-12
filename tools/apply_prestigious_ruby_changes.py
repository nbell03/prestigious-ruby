#!/usr/bin/env python3
"""Apply deterministic, fail-closed Prestigious Ruby source edits."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def write(path, data):
    (ROOT / path).write_text(data, encoding="utf-8")

def replace_once(text, pattern, replacement, label):
    out, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"Refusing {label}: expected one source match, found {count}")
    return out

# Move power buffs, preserving each move's original effect and flags.
path = "src/data/battle_moves.c"
text = read(path)
for name in ("BULLET_SEED", "FURY_CUTTER"):
    text = replace_once(text, rf"(\[MOVE_{name}\]\s*=\s*\{{.*?\.power\s*=\s*)10(\s*,)",
                        rf"\g<1>25\g<2>", f"MOVE_{name} power")
    block = re.search(rf"\[MOVE_{name}\]\s*=\s*\{{(.*?)\n\s*\}},", text, re.S)
    if not block or not re.search(r"\.power\s*=\s*25\s*,", block.group(1)):
        raise SystemExit(f"Validation failed for MOVE_{name}")
write(path, text)
print("PASS: Bullet Seed/Fury Cutter power 25; effects unchanged")

# The uploaded repository branch was missing these two level reductions.
path = "src/data/pokemon/evolution.h"
text = read(path)
for species, old, new, target in [
    ("VIBRAVA", 45, 40, "FLYGON"),
    ("SHELGON", 50, 45, "SALAMENCE"),
]:
    pattern = rf"(\[SPECIES_{species}\]\s*=\s*\{{\{{EVO_LEVEL,\s*){old}(,\s*SPECIES_{target}\}}\}})"
    text = replace_once(text, pattern, rf"\g<1>{new}\g<2>", f"{species} evolution level")
write(path, text)
print("PASS: Vibrava evolves at 40; Shelgon evolves at 45")

# Assert that the previously saved stat edits are present; fail closed if not.
path = "src/data/pokemon/base_stats.h"
text = read(path)
for species, attack, special_attack in [
    ("TREECKO", 65, 45),
    ("GROVYLE", 85, 65),
    ("SCEPTILE", 105, 85),
]:
    block = re.search(rf"\[SPECIES_{species}\]\s*=\s*\{{(.*?)\n\s*\}},", text, re.S)
    if not block or not re.search(rf"\.baseAttack\s*=\s*{attack}\s*,", block.group(1)) or not re.search(rf"\.baseSpAttack\s*=\s*{special_attack}\s*,", block.group(1)):
        raise SystemExit(f"Missing expected saved stats for {species}")
absol = re.search(r"\[SPECIES_ABSOL\]\s*=\s*\{(.*?)\n\s*\},", text, re.S)
if not absol or not re.search(r"\.baseSpeed\s*=\s*100\s*,", absol.group(1)):
    raise SystemExit("Missing expected Absol Speed 100 buff")
print("PASS: Treecko line Attack/Sp. Attack changes and Absol Speed 100 verified")
