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

# Default save folder
SAVE_DIR = os.path.join(os.path.dirname(__file__), "data", "save_games")
os.makedirs(SAVE_DIR, exist_ok=True)

# Allowed classes and their base stats
_VALID_CLASSES = {
    "Warrior": {"max_health": 120, "strength": 15, "magic": 5},
    "Mage":    {"max_health": 80,  "strength": 8,  "magic": 20},
    "Rogue":   {"max_health": 90,  "strength": 12, "magic": 10},
    "Cleric":  {"max_health": 100, "strength": 10, "magic": 15},
}


def create_character(name, character_class):
    """
    Create a new character dict. Raises InvalidCharacterClassError when class invalid.
    """
    if not isinstance(name, str) or not name.strip():
        raise InvalidCharacterClassError("Name must be a non-empty string.")
    if character_class not in _VALID_CLASSES:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    tpl = _VALID_CLASSES[character_class]
    character = {
        "name": name.strip(),
        "class": character_class,
        "level": 1,
        "experience": 0,
        "health": int(tpl["max_health"]),
        "max_health": int(tpl["max_health"]),
        "strength": int(tpl["strength"]),
        "magic": int(tpl["magic"]),
        "gold": 0,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }
    return character


def _save_path_for(name, save_directory=SAVE_DIR):
    return os.path.join(save_directory, f"{name}_save.txt")


def save_character(character, save_directory=SAVE_DIR):
    """
    Save character to text file. Returns True on success.
    Format: KEY: value (one per line)
    """
    if not isinstance(character, dict) or "name" not in character:
        raise ValueError("Invalid character object.")

    os.makedirs(save_directory, exist_ok=True)
    path = _save_path_for(character["name"], save_directory)

    # Serialize lists to comma separated strings
    inv = ",".join(map(str, character.get("inventory", [])))
    active = ",".join(map(str, character.get("active_quests", [])))
    done = ",".join(map(str, character.get("completed_quests", [])))

    lines = [
        f"NAME: {character.get('name')}",
        f"CLASS: {character.get('class')}",
        f"LEVEL: {int(character.get('level', 1))}",
        f"EXPERIENCE: {int(character.get('experience', 0))}",
        f"HEALTH: {int(character.get('health', 0))}",
        f"MAX_HEALTH: {int(character.get('max_health', 0))}",
        f"STRENGTH: {int(character.get('strength', 0))}",
        f"MAGIC: {int(character.get('magic', 0))}",
        f"GOLD: {int(character.get('gold', 0))}",
        f"INVENTORY: {inv}",
        f"ACTIVE_QUESTS: {active}",
        f"COMPLETED_QUESTS: {done}"
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True


def load_character(character_name, save_directory=SAVE_DIR):
    """
    Load character from save file.
    Raises CharacterNotFoundError if file missing.
    Raises InvalidSaveDataError or SaveFileCorruptedError on bad data.
    """
    if not isinstance(character_name, str) or not character_name.strip():
        raise CharacterNotFoundError("Invalid character name.")

    path = _save_path_for(character_name, save_directory)
    if not os.path.isfile(path):
        raise CharacterNotFoundError(f"Save file for '{character_name}' not found.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        raise SaveFileCorruptedError(f"Could not read save file: {e}")

    data = {}
    for idx, line in enumerate(raw, 1):
        if ":" not in line:
            raise InvalidSaveDataError(f"Malformed line {idx}: {line}")
        k, v = line.split(":", 1)
        data[k.strip().upper()] = v.strip()

    required = {"NAME", "CLASS", "LEVEL", "EXPERIENCE", "HEALTH", "MAX_HEALTH", "STRENGTH", "MAGIC", "GOLD", "INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"}
    if not required.issubset(set(data.keys())):
        missing = required - set(data.keys())
        raise InvalidSaveDataError(f"Missing keys in save: {', '.join(sorted(missing))}")

    try:
        level = int(data["LEVEL"])
        experience = int(data["EXPERIENCE"])
        health = int(data["HEALTH"])
        max_health = int(data["MAX_HEALTH"])
        strength = int(data["STRENGTH"])
        magic = int(data["MAGIC"])
        gold = int(data["GOLD"])
    except ValueError as e:
        raise InvalidSaveDataError(f"Invalid numeric in save: {e}")

    def _parse_list(s):
        s = s.strip()
        if not s:
            return []
        return [it for it in (x.strip() for x in s.split(",")) if it]

    inventory = _parse_list(data.get("INVENTORY", ""))
    active_quests = _parse_list(data.get("ACTIVE_QUESTS", ""))
    completed_quests = _parse_list(data.get("COMPLETED_QUESTS", ""))

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

    # basic validation
    try:
        validate_character_data(character)
    except InvalidSaveDataError as e:
        raise InvalidSaveDataError(f"Save validation failed: {e}")

    return character


def delete_character(character_name, save_directory=SAVE_DIR):
    """Delete a saved character file. Raises CharacterNotFoundError if missing."""
    path = _save_path_for(character_name, save_directory)
    if not os.path.isfile(path):
        raise CharacterNotFoundError(f"Save for '{character_name}' not found.")
    os.remove(path)
    return True


def list_saved_characters(save_directory=SAVE_DIR):
    """Return list of saved character names (without suffix)."""
    if not os.path.isdir(save_directory):
        return []
    out = []
    for fname in sorted(os.listdir(save_directory)):
        if fname.endswith("_save.txt"):
            out.append(fname[:-len("_save.txt")])
    return out


# =========================
# STAT & PROGRESSION HELPERS
# =========================

def gain_experience(character, xp_amount):
    """
    Add experience and handle levelling.
    Raises CharacterDeadError if character['health'] <= 0.
    Level-up rule: required_xp = current_level * 100.
    On level-up:
      - level +=1
      - max_health +=10
      - strength +=2
      - magic +=2
      - health restored to max
    Returns True if leveled at least once, else False.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    if int(character.get("health", 0)) <= 0:
        raise CharacterDeadError("Character is dead; cannot gain experience.")
    if not isinstance(xp_amount, int):
        raise ValueError("xp_amount must be int.")

    character["experience"] = character.get("experience", 0) + xp_amount
    leveled = False
    while True:
        cur_level = int(character.get("level", 1))
        req = cur_level * 100
        if character["experience"] >= req:
            character["experience"] -= req
            character["level"] = cur_level + 1
            character["max_health"] = int(character.get("max_health", 0)) + 10
            character["strength"] = int(character.get("strength", 0)) + 2
            character["magic"] = int(character.get("magic", 0)) + 2
            # restore health
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
        raise ValueError("Amount must be int.")
    new = int(character.get("gold", 0)) + amount
    if new < 0:
        raise ValueError("Resulting gold cannot be negative.")
    character["gold"] = new
    return new


def heal_character(character, amount):
    """
    Heal a character by amount (do not exceed max_health).
    Returns actual healed amount.
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


def validate_character_data(character):
    """
    Validate required fields/types. Raises InvalidSaveDataError on problems.
    """
    if not isinstance(character, dict):
        raise InvalidSaveDataError("Character must be a dict.")
    required = ["name", "class", "level", "experience", "health", "max_health",
                "strength", "magic", "gold", "inventory", "active_quests", "completed_quests"]
    missing = [k for k in required if k not in character]
    if missing:
        raise InvalidSaveDataError(f"Missing fields: {', '.join(missing)}")
    # basic type checks
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


# Self test
if __name__ == "__main__":
    print("Character manager quick test")
    c = create_character("Test", "Warrior")
    print("Created:", c)
    save_character(c)
    loaded = load_character("Test")
    print("Loaded:", loaded.get("name"))
    delete_character("Test")
    print("Deleted save")

