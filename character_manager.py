"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Fully Test-Compatible Implementation
"""

import os

from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================
# SAVE DIRECTORY
# ============================================================

SAVE_DIR = os.path.join("data", "save_games")
os.makedirs(SAVE_DIR, exist_ok=True)

# ============================================================
# CHARACTER CLASS DEFINITIONS
# ============================================================

_VALID_CLASSES = {
    "Warrior": {"max_health": 120, "strength": 15, "magic": 5},
    "Mage":    {"max_health": 80,  "strength": 8,  "magic": 20},
    "Rogue":   {"max_health": 90,  "strength": 12, "magic": 10},
    "Cleric":  {"max_health": 100, "strength": 10, "magic": 15},
}

# ============================================================
# CHARACTER CREATION
# ============================================================

def create_character(name, character_class):
    """Create a new character."""
    if character_class not in _VALID_CLASSES:
        raise InvalidCharacterClassError("Invalid class")

    base = _VALID_CLASSES[character_class]

    return {
        "name": name,
        "class": character_class,
        "level": 1,
        "experience": 0,
        "health": base["max_health"],
        "max_health": base["max_health"],
        "strength": base["strength"],
        "magic": base["magic"],
        "gold": 0,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }

# ============================================================
# FILE HELPERS
# ============================================================

def _save_path(name):
    return os.path.join(SAVE_DIR, f"{name}_save.txt")

# ============================================================
# SAVE CHARACTER
# ============================================================

def save_character(character):
    """Save character to text file."""
    if not isinstance(character, dict):
        raise InvalidSaveDataError("Invalid character format")

    path = _save_path(character["name"])

    try:
        with open(path, "w") as f:
            for key, value in character.items():
                if isinstance(value, list):
                    f.write(f"{key}:{','.join(value)}\n")
                else:
                    f.write(f"{key}:{value}\n")
        return True
    except:
        raise SaveFileCorruptedError("Could not save")

# ============================================================
# LOAD CHARACTER
# ============================================================

def load_character(name):
    """Load a saved character."""
    path = _save_path(name)

    if not os.path.exists(path):
        raise CharacterNotFoundError("Save file missing")

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except:
        raise SaveFileCorruptedError("Cannot read file")

    data = {}

    for line in lines:
        if ":" not in line:
            raise InvalidSaveDataError("Corrupt line")

        key, val = line.strip().split(":", 1)

        if key in ("inventory", "active_quests", "completed_quests"):
            data[key] = [v for v in val.split(",") if v]
        else:
            try:
                data[key] = int(val) if val.isdigit() else val
            except:
                raise InvalidSaveDataError("Invalid value")

    # Validation
    required = [
        "name", "class", "level", "experience", "health", "max_health",
        "strength", "magic", "gold", "inventory", "active_quests",
        "completed_quests"
    ]

    for field in required:
        if field not in data:
            raise InvalidSaveDataError("Missing field")

    return data

# ============================================================
# DELETE CHARACTER
# ============================================================

def delete_character(name):
    """Delete saved character."""
    path = _save_path(name)
    if not os.path.exists(path):
        raise CharacterNotFoundError("Save file missing")
    os.remove(path)

# ============================================================
# CHARACTER STAT FUNCTIONS
# ============================================================

def gain_experience(character, xp):
    """Gain XP and handle level up."""
    if character["health"] <= 0:
        raise CharacterDeadError("Character is dead")

    character["experience"] += xp

    leveled = False

    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]
        leveled = True

    return leveled

def add_gold(character, amount):
    """Add or subtract gold."""
    new = character["gold"] + amount
    if new < 0:
        raise ValueError("Gold cannot be negative")
    character["gold"] = new
    return new

def heal_character(character, amount):
    """Heal character without exceeding max health."""
    healed = min(amount, character["max_health"] - character["health"])
    character["health"] += healed
    return healed
