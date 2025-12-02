"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Minimal, test-compatible implementation

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]
"""

import os

from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ---------------------------------------------------------------------------
# SAVE DIRECTORY
# ---------------------------------------------------------------------------

SAVE_DIR = os.path.join(os.path.dirname(__file__), "data", "save_games")
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# DEFAULT CLASSES
# ---------------------------------------------------------------------------

_VALID_CLASSES = {
    "Warrior": {"max_health": 120, "strength": 15, "magic": 5},
    "Mage":    {"max_health": 80,  "strength": 8,  "magic": 20},
    "Rogue":   {"max_health": 90,  "strength": 12, "magic": 10},
    "Cleric":  {"max_health": 100, "strength": 10, "magic": 15},
}


# ---------------------------------------------------------------------------
# CHARACTER CREATION
# ---------------------------------------------------------------------------

def create_character(name, character_class):
    """
    Create and return a new character dictionary.
    Raises InvalidCharacterClassError if class is not recognized.
    """
    if not isinstance(name, str) or not name.strip():
        raise InvalidCharacterClassError("Name must be a non-empty string.")

    if character_class not in _VALID_CLASSES:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    base = _VALID_CLASSES[character_class]

    return {
        "name": name.strip(),
        "class": character_class,
        "level": 1,
        "experience": 0,

        "max_health": base["max_health"],
        "health": base["max_health"],

        "strength": base["strength"],
        "magic": base["magic"],

        "gold": 0,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }


# ---------------------------------------------------------------------------
# SAVE / LOAD SYSTEM
# ---------------------------------------------------------------------------

def _save_path_for(name, save_directory=SAVE_DIR):
    return os.path.join(save_directory, f"{name}_save.txt")


def save_character(character, save_directory=SAVE_DIR):
    """
    Save character to disk.
    Returns True on success.
    """
    if not isinstance(character, dict) or "name" not in character:
        raise ValueError("Invalid character object.")

    os.makedirs(save_directory, exist_ok=True)
    path = _save_path_for(character["name"], save_directory)

    def encode_list(lst):
        return ",".join(str(x) for x in lst)

    lines = [
        f"NAME: {character['name']}",
        f"CLASS: {character['class']}",
        f"LEVEL: {character['level']}",
        f"EXPERIENCE: {character['experience']}",
        f"HEALTH: {character['health']}",
        f"MAX_HEALTH: {character['max_health']}",
        f"STRENGTH: {character['strength']}",
        f"MAGIC: {character['magic']}",
        f"GOLD: {character['gold']}",
        f"INVENTORY: {encode_list(character['inventory'])}",
        f"ACTIVE_QUESTS: {encode_list(character['active_quests'])}",
        f"COMPLETED_QUESTS: {encode_list(character['completed_quests'])}"
    ]

    with open(path, "w") as f:
        f.write("\n".join(lines))

    return True


def load_character(name, save_directory=SAVE_DIR):
    """
    Load a character from disk.
    Raises:
      CharacterNotFoundError — save file missing  
      SaveFileCorruptedError — unreadable file  
      InvalidSaveDataError — malformed data
    """
    path = _save_path_for(name, save_directory)

    if not os.path.isfile(path):
        raise CharacterNotFoundError(f"Save file for '{name}' not found.")

    try:
        with open(path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        raise SaveFileCorruptedError(f"Could not read save file: {e}")

    data = {}
    for line in lines:
        if ":" not in line:
            raise InvalidSaveDataError(f"Malformed line: {line}")
        k, v = line.split(":", 1)
        data[k.strip().upper()] = v.strip()

    required = {
        "NAME", "CLASS", "LEVEL", "EXPERIENCE", "HEALTH", "MAX_HEALTH",
        "STRENGTH", "MAGIC", "GOLD", "INVENTORY",
        "ACTIVE_QUESTS", "COMPLETED_QUESTS"
    }
    if not required.issubset(data.keys()):
        raise InvalidSaveDataError("Missing fields in save file.")

    def decode_list(s):
        if not s:
            return []
        return [x for x in s.split(",") if x]

    try:
        character = {
            "name": data["NAME"],
            "class": data["CLASS"],
            "level": int(data["LEVEL"]),
            "experience": int(data["EXPERIENCE"]),
            "health": int(data["HEALTH"]),
            "max_health": int(data["MAX_HEALTH"]),
            "strength": int(data["STRENGTH"]),
            "magic": int(data["MAGIC"]),
            "gold": int(data["GOLD"]),
            "inventory": decode_list(data["INVENTORY"]),
            "active_quests": decode_list(data["ACTIVE_QUESTS"]),
            "completed_quests": decode_list(data["COMPLETED_QUESTS"])
        }
    except Exception:
        raise InvalidSaveDataError("Invalid numeric data in save file.")

    validate_character_data(character)
    return character


def delete_character(name, save_directory=SAVE_DIR):
    path = _save_path_for(name, save_directory)
    if not os.path.isfile(path):
        raise CharacterNotFoundError(f"Save file for '{name}' not found.")
    os.remove(path)
    return True


def list_saved_characters(save_directory=SAVE_DIR):
    if not os.path.isdir(save_directory):
        return []
    result = []
    for fname in os.listdir(save_directory):
        if fname.endswith("_save.txt"):
            result.append(fname[:-9])
    return result


# ---------------------------------------------------------------------------
# CHARACTER PROGRESSION
# ---------------------------------------------------------------------------

def gain_experience(character, xp):
    """
    Add XP. Level up when xp >= level * 100.
    Raises CharacterDeadError if HP <= 0.
    """
    if character["health"] <= 0:
        raise CharacterDeadError("Character is dead; cannot gain XP.")

    character["experience"] += xp
    leveled = False

    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1

        # Stat increases
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2

        # Restore full health on level up
        character["health"] = character["max_health"]

        leveled = True

    return leveled


def add_gold(character, amount):
    """
    Add/remove gold. Cannot go below zero.
    Raises ValueError if resulting gold < 0.
    """
    new_gold = character["gold"] + amount
    if new_gold < 0:
        raise ValueError("Resulting gold cannot be negative.")
    character["gold"] = new_gold
    return new_gold


def heal_character(character, amount):
    """
    Heal by up to 'amount', not exceeding max_health.
    """
    amount = max(0, amount)
    missing = character["max_health"] - character["health"]
    healed = min(missing, amount)
    character["health"] += healed
    return healed


# ---------------------------------------------------------------------------
# VALIDATION HELPERS
# ---------------------------------------------------------------------------

def validate_character_data(character):
    """
    Confirm saved character data is valid.
    Raises InvalidSaveDataError on problems.
    """
    if not isinstance(character, dict):
        raise InvalidSaveDataError("Character must be a dict.")

    required = [
        "name", "class", "level", "experience", "health", "max_health",
        "strength", "magic", "gold", "inventory",
        "active_quests", "completed_quests"
    ]
    for field in required:
        if field not in character:
            raise InvalidSaveDataError(f"Missing field: {field}")

    # Type checks
    if not isinstance(character["name"], str):
        raise InvalidSaveDataError("Name must be a string.")
    if not isinstance(character["class"], str):
        raise InvalidSaveDataError("Class must be a string.")

    numeric_fields = ["level", "experience", "health", "max_health", "strength", "magic", "gold"]
    for f in numeric_fields:
        if not isinstance(character[f], int):
            raise InvalidSaveDataError(f"{f} must be an integer.")

    if not isinstance(character["inventory"], list):
        raise InvalidSaveDataError("inventory must be a list.")
    if not isinstance(character["active_quests"], list):
        raise InvalidSaveDataError("active_quests must be a list.")
    if not isinstance(character["completed_quests"], list):
        raise InvalidSaveDataError("completed_quests must be a list.")

    return True


# ---------------------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    c = create_character("Tester", "Warrior")
    print("Created:", c)
    save_character(c)
    loaded = load_character("Tester")
    print("Loaded:", loaded)
    delete_character("Tester")
    print("Deleted save successfully")


