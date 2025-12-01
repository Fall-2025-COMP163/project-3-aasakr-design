"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Implementation (test-compatible)

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Provides character creation, saving/loading, leveling, and simple stat helpers.
"""

import os

from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# Default save directory
SAVE_DIR_DEFAULT = os.path.join(os.path.dirname(__file__), "data", "save_games")

# Valid classes required by the project/tests
VALID_CLASSES = {
    "Warrior": {"max_health": 120, "strength": 15, "magic": 5},
    "Mage":    {"max_health": 80,  "strength": 8,  "magic": 20},
    "Rogue":   {"max_health": 90,  "strength": 12, "magic": 10},
    "Cleric":  {"max_health": 100, "strength": 10, "magic": 15},
}

# ========================================================================
# Creation / Persistence
# ========================================================================

def create_character(name, character_class):
    """
    Create a character dictionary for the given class.
    Raises InvalidCharacterClassError for invalid classes.
    """
    if not isinstance(name, str) or not name.strip():
        raise InvalidCharacterClassError("Name must be a non-empty string.")
    if character_class not in VALID_CLASSES:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    tpl = VALID_CLASSES[character_class]
    character = {
        "name": name.strip(),
        "class": character_class,
        "level": 1,
        "experience": 0,
        "health": tpl["max_health"],
        "max_health": tpl["max_health"],
        "strength": tpl["strength"],
        "magic": tpl["magic"],
        "gold": 0,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }
    return character


def save_character(character, save_directory=SAVE_DIR_DEFAULT):
    """
    Save character to a text file in save_directory.
    Returns True on success. Raises I/O exceptions as normal.
    """
    if not isinstance(character, dict) or "name" not in character:
        raise ValueError("Invalid character object to save.")

    os.makedirs(save_directory, exist_ok=True)
    filename = f"{character['name']}_save.txt"
    path = os.path.join(save_directory, filename)

    # Serialize lists as comma-separated strings
    inv = ",".join(map(str, character.get("inventory", [])))
    active = ",".join(map(str, character.get("active_quests", [])))
    done = ",".join(map(str, character.get("completed_quests", [])))

    lines = [
        f"NAME: {character.get('name')}",
        f"CLASS: {character.get('class')}",
        f"LEVEL: {character.get('level')}",
        f"EXPERIENCE: {character.get('experience')}",
        f"HEALTH: {character.get('health')}",
        f"MAX_HEALTH: {character.get('max_health')}",
        f"STRENGTH: {character.get('strength')}",
        f"MAGIC: {character.get('magic')}",
        f"GOLD: {character.get('gold')}",
        f"INVENTORY: {inv}",
        f"ACTIVE_QUESTS: {active}",
        f"COMPLETED_QUESTS: {done}"
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return True


def load_character(character_name, save_directory=SAVE_DIR_DEFAULT):
    """
    Load character file and return character dict.
    Raises CharacterNotFoundError, SaveFileCorruptedError, InvalidSaveDataError.
    """
    if not isinstance(character_name, str) or not character_name.strip():
        raise CharacterNotFoundError("Invalid character name.")

    filename = f"{character_name}_save.txt"
    path = os.path.join(save_directory, filename)

    if not os.path.isfile(path):
        raise CharacterNotFoundError(f"Save file for '{character_name}' not found.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_lines = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        raise SaveFileCorruptedError(f"Could not read save file: {e}")

    data = {}
    for lineno, line in enumerate(raw_lines, start=1):
        if ":" not in line:
            raise InvalidSaveDataError(f"Malformed line in save file (line {lineno}): {line}")
        key, val = line.split(":", 1)
        data[key.strip().upper()] = val.strip()

    # Required keys
    required = {"NAME", "CLASS", "LEVEL", "EXPERIENCE", "HEALTH", "MAX_HEALTH", "STRENGTH", "MAGIC", "GOLD", "INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"}
    if not required.issubset(set(data.keys())):
        missing = required - set(data.keys())
        raise InvalidSaveDataError(f"Missing keys in save: {', '.join(sorted(missing))}")

    # Parse numeric fields
    try:
        level = int(data["LEVEL"])
        experience = int(data["EXPERIENCE"])
        health = int(data["HEALTH"])
        max_health = int(data["MAX_HEALTH"])
        strength = int(data["STRENGTH"])
        magic = int(data["MAGIC"])
        gold = int(data["GOLD"])
    except ValueError as e:
        raise InvalidSaveDataError(f"Invalid numeric value in save: {e}")

    def _parse_list_field(s):
        s = s.strip()
        if not s:
            return []
        return [it for it in (x.strip() for x in s.split(",")) if it]

    inventory = _parse_list_field(data["INVENTORY"])
    active_quests = _parse_list_field(data["ACTIVE_QUESTS"])
    completed_quests = _parse_list_field(data["COMPLETED_QUESTS"])

    character = {
        "name": data["NAME"],
        "class": data["CLASS"],
        "level": level,
        "experience": experience,
        "health": health,
        "max_health": max_health,
        "strength": strength,
        "magic": magic,
        "gold": gold,
        "inventory": inventory,
        "active_quests": active_quests,
        "completed_quests": completed_quests
    }

    # Basic validation
    try:
        validate_character_data(character)
    except InvalidSaveDataError as e:
        raise InvalidSaveDataError(f"Save validation failed: {e}")

    return character


def delete_character(character_name, save_directory=SAVE_DIR_DEFAULT):
    """
    Delete a saved character file.
    Raises CharacterNotFoundError if not found.
    """
    filename = f"{character_name}_save.txt"
    path = os.path.join(save_directory, filename)
    if not os.path.isfile(path):
        raise CharacterNotFoundError(f"Save for '{character_name}' not found.")
    os.remove(path)
    return True


def list_saved_characters(save_directory=SAVE_DIR_DEFAULT):
    """
    Return a list of saved character names (without suffix). Empty list if none.
    """
    if not os.path.isdir(save_directory):
        return []
    names = []
    for fname in sorted(os.listdir(save_directory)):
        if fname.endswith("_save.txt"):
            names.append(fname[:-len("_save.txt")])
    return names

# ========================================================================
# Progression / Stats
# ========================================================================

def gain_experience(character, xp_amount):
    """
    Add experience and perform level-ups.
    Raises CharacterDeadError if character's health <= 0.
    Level up rule: required_xp = current_level * 100
    On level up:
      - level += 1
      - max_health += 10
      - strength += 2
      - magic += 2
      - health restored to max_health
    Returns True if leveled up at least once, False otherwise.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    if int(character.get("health", 0)) <= 0:
        raise CharacterDeadError("Cannot gain experience: character is dead.")
    if not isinstance(xp_amount, int):
        raise ValueError("xp_amount must be int.")

    character["experience"] = character.get("experience", 0) + xp_amount
    leveled = False
    while True:
        current_level = int(character.get("level", 1))
        required = current_level * 100
        if character["experience"] >= required:
            character["experience"] -= required
            character["level"] = current_level + 1
            character["max_health"] = int(character.get("max_health", 0)) + 10
            character["strength"] = int(character.get("strength", 0)) + 2
            character["magic"] = int(character.get("magic", 0)) + 2
            character["health"] = int(character.get("max_health", 0))
            leveled = True
        else:
            break
    return leveled


def add_gold(character, amount):
    """
    Add or subtract gold. Raises ValueError if resulting gold < 0.
    Returns new gold total.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    if not isinstance(amount, int):
        raise ValueError("Amount must be integer.")
    new = int(character.get("gold", 0)) + amount
    if new < 0:
        raise ValueError("Resulting gold cannot be negative.")
    character["gold"] = new
    return new


def heal_character(character, amount):
    """
    Heal character by amount (not to exceed max_health). Returns actual healed amount.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    if amount <= 0:
        return 0
    max_hp = int(character.get("max_health", 0))
    cur = int(character.get("health", 0))
    healed = min(amount, max_hp - cur)
    character["health"] = cur + healed
    return healed


def is_character_dead(character):
    return int(character.get("health", 0)) <= 0


def revive_character(character):
    """
    Revive with 50% of max_health. Returns True if revived, False if already alive.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    if not is_character_dead(character):
        return False
    max_hp = int(character.get("max_health", 1))
    character["health"] = max(1, max_hp // 2)
    return True


# ========================================================================
# Validation
# ========================================================================

def validate_character_data(character):
    """
    Ensure required fields exist and types are correct. Raises InvalidSaveDataError on problems.
    """
    if not isinstance(character, dict):
        raise InvalidSaveDataError("Character must be a dict.")
    req = ["name", "class", "level", "experience", "health", "max_health",
           "strength", "magic", "gold", "inventory", "active_quests", "completed_quests"]
    missing = [k for k in req if k not in character]
    if missing:
        raise InvalidSaveDataError(f"Missing fields: {', '.join(missing)}")
    # Basic type checks
    if not isinstance(character["name"], str):
        raise InvalidSaveDataError("Field 'name' must be string.")
    if not isinstance(character["class"], str):
        raise InvalidSaveDataError("Field 'class' must be string.")
    for n in ["level", "experience", "health", "max_health", "strength", "magic", "gold"]:
        if not isinstance(character.get(n), int):
            raise InvalidSaveDataError(f"Field '{n}' must be int.")
    for l in ["inventory", "active_quests", "completed_quests"]:
        if not isinstance(character.get(l), list):
            raise InvalidSaveDataError(f"Field '{l}' must be list.")
    return True


# ========================================================================
# Module self-test
# ========================================================================
if __name__ == "__main__":
    print("Character manager quick self-test")
    c = create_character("TestHero", "Warrior")
    print("Created:", c)
    save_character(c)
    loaded = load_character("TestHero")
    print("Loaded:", loaded)
    delete_character("TestHero")
    print("Deleted save.")
