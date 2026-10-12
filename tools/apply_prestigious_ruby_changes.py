#!/usr/bin/env python3
"""Apply small, deterministic Prestigious Ruby source edits before building.

This staged patcher intentionally fails closed: every expected vanilla source
pattern must be present exactly once, so an upstream source change cannot
silently produce a partially modified ROM.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MOVES = ROOT / "src/data/battle_moves.c"
text = MOVES.read_text(encoding="utf-8")

def set_move_power(name: str, expected: int, desired: int) -> None:
    global text
    pattern = rf"(\[MOVE_{name}\]\s*=\s*\{{.*?\.power\s*=\s*){expected}(\s*,)"
    text_new, count = re.subn(pattern, rf"\g<1>{desired}\g<2>", text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"Refusing to patch MOVE_{name}: expected exactly one power-{expected} entry, found {count}")
    text = text_new
    block = re.search(rf"\[MOVE_{name}\]\s*=\s*\{{(.*?)\n\s*\}},", text, re.S)
    if not block or not re.search(rf"\.power\s*=\s*{desired}\s*,", block.group(1)):
        raise SystemExit(f"Validation failed for MOVE_{name}")

set_move_power("BULLET_SEED", 10, 25)
set_move_power("FURY_CUTTER", 10, 25)
MOVES.write_text(text, encoding="utf-8")
print("PASS: Bullet Seed power 25; multi-hit effect retained")
print("PASS: Fury Cutter power 25; Fury Cutter effect retained")
