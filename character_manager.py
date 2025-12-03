"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Test-focused implementation

Name: [Your Name Here]
AI Usage: [Document any AI assistance used]
"""

import os

from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError,
)

# ---------------------------------------------------------------------------
# SAVE PATHS
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVE_DIR = os.path.join(DATA_DIR, "save_games")

os.makedirs(SAVE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# CHARACTER CREATION
# ---------------------------------------------------------------------------

CLASS_STATS = {
    "Warrior": {"max_health": 120, "strength": 15, "magic": 5},
    "Mage": {"max_health": 80, "strength": 8, "magic": 20},
    "Rogue": {"max_health": 90, "strength": 12, "magic": 10},
    "Cleric": {"max_health": 100, "strength": 10, "magic": 15},
}


def create_character(name, character_class):
    """Create a new character dictionary.

    Raises InvalidCharacterClassError if the class is not one of the allowed ones.
    """
    if character_class not in CLASS_STATS:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    base = CLASS_STATS[character_class]
    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "experience": 0,
        "health": base["max_health"],
        "max_health": base["max_health"],
        "strength": base["strength"],
        "magic": base["magic"],
        "gold": 100,  # give some starting gold so shop tests work comfortably
        "inventory": [],
        "active_quests": [],
        "completed_quests": [],
    }
    return character


# ---------------------------------------------------------------------------
# SAVE / LOAD HELPERS
# ---------------------------------------------------------------------------

def _save_path_for(name):
    return os.path.join(SAVE_DIR, f"{name}_save.txt")


def save_character(character):
    """Save character to a simple text file. Returns True on success."""
    if not isinstance(character, dict) or "name" not in character:
        raise InvalidSaveDataError("Character must be a dict with a name.")

    path = _save_path_for(character["name"])

    lines = [
        f"name:{character['name']}",
        f"class:{character['class']}",
        f"level:{int(character.get('level', 1))}",
        f"experience:{int(character.get('experience', 0))}",
        f"health:{int(character.get('health', 0))}",
        f"max_health:{int(character.get('max_health', 0))}",
        f"strength:{int(character.get('strength', 0))}",
        f"magic:{int(character.get('magic', 0))}",
        f"gold:{int(character.get('gold', 0))}",
        "inventory:" + ",".join(character.get("inventory", [])),
        "active_quests:" + ",".join(character.get("active_quests", [])),
        "completed_quests:" + ",".join(character.get("completed_quests", [])),
    ]

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except OSError as e:
        raise SaveFileCorruptedError(f"Unable to save character: {e}")

    return True


def load_character(name):
    """Load character from save file.

    Raises CharacterNotFoundError if missing.
    Raises InvalidSaveDataError or SaveFileCorruptedError on problems.
    """
    path = _save_path_for(name)
    if not os.path.isfile(path):
        raise CharacterNotFoundError(f"Character '{name}' not found")

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except OSError as e:
        raise SaveFileCorruptedError(f"Unable to read save file: {e}")

    data = {}
    for line in lines:
        if ":" not in line:
            raise InvalidSaveDataError(f"Malformed line in save: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()

    required_keys = [
        "name",
        "class",
        "level",
        "experience",
        "health",
        "max_health",
        "strength",
        "magic",
        "gold",
        "inventory",
        "active_quests",
        "completed_quests",
    ]
    if any(k not in data for k in required_keys):
        raise InvalidSaveDataError("Missing required character fields in save.")

    try:
        character = {
            "name": data["name"],
            "class": data["class"],
            "level": int(data["level"]),
            "experience": int(data["experience"]),
            "health": int(data["health"]),
            "max_health": int(data["max_health"]),
            "strength": int(data["strength"]),
            "magic": int(data["magic"]),
            "gold": int(data["gold"]),
            "inventory": [i for i in data["inventory"].split(",") if i],
            "active_quests": [q for q in data["active_quests"].split(",") if q],
            "completed_quests": [q for q in data["completed_quests"].split(",") if q],
        }
    except ValueError as e:
        raise InvalidSaveDataError(f"Invalid numeric field in save: {e}")

    return character


def delete_character(name):
    """Delete a saved character file. Used by integration tests."""
    path = _save_path_for(name)
    if not os.path.isfile(path):
        raise CharacterNotFoundError(f"Character '{name}' not found")
    os.remove(path)
    return True


# ---------------------------------------------------------------------------
# STATS & LEVELING
# ---------------------------------------------------------------------------

def gain_experience(character, xp_amount):
    """Add XP and handle level-ups.

    - Raises CharacterDeadError if health <= 0.
    - Uses simple rule: required XP to level = level * 100
    """
    if character.get("health", 0) <= 0:
        raise CharacterDeadError("Dead characters cannot gain experience")

    if not isinstance(xp_amount, int):
        raise ValueError("xp_amount must be an int")

    character["experience"] = character.get("experience", 0) + xp_amount
    leveled_up = False

    # Allow multiple level-ups if enough XP
    while True:
        current_level = character.get("level", 1)
        required = current_level * 100
        if character["experience"] >= required:
            character["experience"] -= required
            character["level"] = current_level + 1
            character["max_health"] += 10
            character["strength"] += 2
            character["magic"] += 2
            character["health"] = character["max_health"]  # restore HP on level-up
            leveled_up = True
        else:
            break

    return leveled_up


def add_gold(character, amount):
    """Add (or subtract) gold. Raise ValueError if result would be negative."""
    if not isinstance(amount, int):
        raise ValueError("Gold amount must be an int")

    new_total = character.get("gold", 0) + amount
    if new_total < 0:
        # tests expect ValueError for overspending
        raise ValueError("Gold cannot be negative")

    character["gold"] = new_total
    return new_total


def heal_character(character, amount):
    """Heal up to 'amount' HP without exceeding max_health."""
    if amount <= 0:
        return 0

    max_hp = character.get("max_health", 0)
    current = character.get("health", 0)
    missing = max_hp - current
    healed = min(amount, missing)
    character["health"] = current + healed
    return healed

