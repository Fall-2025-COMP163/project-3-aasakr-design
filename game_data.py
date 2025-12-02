"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Implementation compatible with provided tests.

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ---------------------------------------------------------------------------
# PATH CONSTANTS
# ---------------------------------------------------------------------------

DATA_DIR = "data"
DEFAULT_QUESTS_FILE = os.path.join(DATA_DIR, "quests.txt")
DEFAULT_ITEMS_FILE = os.path.join(DATA_DIR, "items.txt")

# ---------------------------------------------------------------------------
# DATA LOADING FUNCTIONS
# ---------------------------------------------------------------------------

def load_quests(filename: str = DEFAULT_QUESTS_FILE):
    """
    Load quest data from file.

    Expected format per quest (separated by blank lines):
    QUEST_ID: unique_quest_name
    TITLE: Quest Display Title
    DESCRIPTION: Quest description text
    REWARD_XP: 100
    REWARD_GOLD: 50
    REQUIRED_LEVEL: 1
    PREREQUISITE: previous_quest_id (or NONE)

    Returns: dict {quest_id: quest_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Quest data file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            contents = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Error reading quest data file: {e}")

    contents = contents.strip()
    if not contents:
        raise InvalidDataFormatError("Quest file is empty.")

    quests = {}
    # Split blocks by blank lines
    for raw_block in contents.split("\n\n"):
        block_lines = [line.strip() for line in raw_block.splitlines() if line.strip()]
        if not block_lines:
            continue
        quest = parse_quest_block(block_lines)      # may raise InvalidDataFormatError
        validate_quest_data(quest)                  # may raise InvalidDataFormatError
        qid = quest.get("quest_id")
        if not qid:
            raise InvalidDataFormatError("Quest missing quest_id.")
        quests[qid] = quest

    return quests


def load_items(filename: str = DEFAULT_ITEMS_FILE):
    """
    Load item data from file.

    Expected format per item (separated by blank lines):
    ITEM_ID: unique_item_name
    NAME: Item Display Name
    TYPE: weapon|armor|consumable
    EFFECT: stat_name:value (e.g., strength:5 or health:20)
    COST: 100
    DESCRIPTION: Item description

    Returns: dict {item_id: item_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Item data file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            contents = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Error reading item data file: {e}")

    contents = contents.strip()
    if not contents:
        raise InvalidDataFormatError("Item file is empty.")

    items = {}
    for raw_block in contents.split("\n\n"):
        block_lines = [line.strip() for line in raw_block.splitlines() if line.strip()]
        if not block_lines:
            continue
        item = parse_item_block(block_lines)        # may raise InvalidDataFormatError
        validate_item_data(item)                    # may raise InvalidDataFormatError
        iid = item.get("item_id")
        if not iid:
            raise InvalidDataFormatError("Item missing item_id.")
        items[iid] = item

    return items


def validate_quest_data(quest_dict):
    """
    Validate that quest dictionary has all required fields.

    Required fields: quest_id, title, description, reward_xp,
                     reward_gold, required_level, prerequisite

    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields or bad types
    """
    if not isinstance(quest_dict, dict):
        raise InvalidDataFormatError("Quest must be a dictionary.")

    required = {
        "quest_id",
        "title",
        "description",
        "reward_xp",
        "reward_gold",
        "required_level",
        "prerequisite",
    }

    missing = required - set(quest_dict.keys())
    if missing:
        raise InvalidDataFormatError(
            f"Missing quest fields: {', '.join(sorted(missing))}"
        )

    # Type checks
    for key in ("reward_xp", "reward_gold", "required_level"):
        if not isinstance(quest_dict.get(key), int):
            raise InvalidDataFormatError(f"Quest field '{key}' must be an integer.")

    return True


def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields.

    Required fields: item_id, name, type, effect, cost, description
    Valid types: weapon, armor, consumable

    Returns: True if valid
    Raises: InvalidDataFormatError if missing fields or invalid type
    """
    if not isinstance(item_dict, dict):
        raise InvalidDataFormatError("Item must be a dictionary.")

    required = {"item_id", "name", "type", "effect", "cost", "description"}
    missing = required - set(item_dict.keys())
    if missing:
        raise InvalidDataFormatError(
            f"Missing item fields: {', '.join(sorted(missing))}"
        )

    if item_dict.get("type") not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError("Invalid item type.")

    if not isinstance(item_dict.get("cost"), int):
        raise InvalidDataFormatError("Item 'cost' must be integer.")

    return True


def create_default_data_files():
    """
    Create default data files if they don't exist.
    ONLY used when running the game manually, not by the tests.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    # Default items
    if not os.path.isfile(DEFAULT_ITEMS_FILE):
        default_items = """ITEM_ID: health_potion
NAME: Health Potion
TYPE: consumable
EFFECT: health:20
COST: 25
DESCRIPTION: A small potion that restores health.

ITEM_ID: iron_sword
NAME: Iron Sword
TYPE: weapon
EFFECT: strength:5
COST: 50
DESCRIPTION: A basic iron sword.

ITEM_ID: apprentice_robe
NAME: Apprentice Robe
TYPE: armor
EFFECT: max_health:10
COST: 40
DESCRIPTION: Simple protective robe.
"""
        with open(DEFAULT_ITEMS_FILE, "w", encoding="utf-8") as f:
            f.write(default_items)

    # Default quests
    if not os.path.isfile(DEFAULT_QUESTS_FILE):
        default_quests = """QUEST_ID: first_steps
TITLE: First Steps
DESCRIPTION: Your first quest as an adventurer.
REWARD_XP: 50
REWARD_GOLD: 25
REQUIRED_LEVEL: 1
PREREQUISITE: NONE
"""
        with open(DEFAULT_QUESTS_FILE, "w", encoding="utf-8") as f:
            f.write(default_quests)

    return True

# ---------------------------------------------------------------------------
# HELPER PARSERS
# ---------------------------------------------------------------------------

def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary.

    Raises InvalidDataFormatError if parsing fails.
    """
    quest = {}
    for line in lines:
        if ":" not in line:
            # This is exactly what the invalid-data test is looking for
            raise InvalidDataFormatError(f"Invalid quest line: '{line}'")
        key, value = line.split(":", 1)
        key = key.strip().upper()
        value = value.strip()

        if key == "QUEST_ID":
            quest["quest_id"] = value
        elif key == "TITLE":
            quest["title"] = value
        elif key == "DESCRIPTION":
            quest["description"] = value
        elif key == "REWARD_XP":
            try:
                quest["reward_xp"] = int(value)
            except ValueError:
                raise InvalidDataFormatError("REWARD_XP must be an integer")
        elif key == "REWARD_GOLD":
            try:
                quest["reward_gold"] = int(value)
            except ValueError:
                raise InvalidDataFormatError("REWARD_GOLD must be an integer")
        elif key == "REQUIRED_LEVEL":
            try:
                quest["required_level"] = int(value)
            except ValueError:
                raise InvalidDataFormatError("REQUIRED_LEVEL must be an integer")
        elif key == "PREREQUISITE":
            quest["prerequisite"] = value if value else "NONE"
        else:
            # Unknown fields are just stored lowercase
            quest[key.lower()] = value

    # Reasonable defaults
    quest.setdefault("description", "")
    quest.setdefault("reward_xp", 0)
    quest.setdefault("reward_gold", 0)
    quest.setdefault("required_level", 1)
    quest.setdefault("prerequisite", "NONE")

    return quest


def parse_item_block(lines):
    """
    Parse a block of lines into an item dictionary.

    Raises InvalidDataFormatError if parsing fails.
    """
    item = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid item line: '{line}'")
        key, value = line.split(":", 1)
        key = key.strip().upper()
        value = value.strip()

        if key == "ITEM_ID":
            item["item_id"] = value
        elif key == "NAME":
            item["name"] = value
        elif key == "TYPE":
            item["type"] = value.lower()
        elif key == "EFFECT":
            item["effect"] = value
        elif key == "COST":
            try:
                item["cost"] = int(value)
            except ValueError:
                raise InvalidDataFormatError("COST must be an integer")
        elif key == "DESCRIPTION":
            item["description"] = value
        else:
            item[key.lower()] = value

    item.setdefault("description", "")
    item.setdefault("effect", "")
    item.setdefault("cost", 0)

    return item


# ---------------------------------------------------------------------------
# TESTING (manual)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    try:
        create_default_data_files()
        qs = load_quests()
        it = load_items()
        print("Loaded quests:", list(qs.keys()))
        print("Loaded items:", list(it.keys()))
    except Exception as e:
        print("Error:", e)
