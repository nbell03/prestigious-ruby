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

# Requested move buffs; preserve original effects and flags.
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

# Earlier evolution thresholds requested for the Aron and Bagon lines.
path = "src/data/pokemon/evolution.h"
text = read(path)
for species, old, new, target in [
    ("ARON", 32, 25, "LAIRON"),
    ("LAIRON", 42, 38, "AGGRON"),
    ("VIBRAVA", 45, 40, "FLYGON"),
    ("SHELGON", 50, 45, "SALAMENCE"),
]:
    pattern = rf"(\[SPECIES_{species}\]\s*=\s*\{{\{{EVO_LEVEL,\s*){old}(,\s*SPECIES_{target}\}}\}})"
    text = replace_once(text, pattern, rf"\g<1>{new}\g<2>", f"{species} evolution level")
write(path, text)
print("PASS: Aron 25, Lairon 38, Vibrava 40, Shelgon 45 evolution thresholds")

# Requested Treecko line rebalance: trade some special attack for physical attack.
path = "src/data/pokemon/base_stats.h"
text = read(path)
for species, old_atk, new_atk, old_spa, new_spa in [
    ("TREECKO", 45, 65, 65, 45),
    ("GROVYLE", 65, 85, 85, 65),
    ("SCEPTILE", 85, 105, 105, 85),
]:
    pattern = rf"(\[SPECIES_{species}\]\s*=\s*\{{.*?\.baseAttack\s*=\s*){old_atk}(,.*?\.baseSpAttack\s*=\s*){old_spa}(,)"
    text = replace_once(text, pattern, rf"\g<1>{new_atk}\g<2>{new_spa}\g<3>", f"{species} Attack/Sp. Attack")
# Absol's requested Speed buff.
text = replace_once(text, r"(\[SPECIES_ABSOL\]\s*=\s*\{.*?\.baseSpeed\s*=\s*)75(,)",
                    r"\g<1>100\g<2>", "Absol Speed")
write(path, text)
print("PASS: Treecko line Attack/Sp. Attack rebalance; Absol Speed 100")
