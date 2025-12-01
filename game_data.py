"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# PATH CONSTANTS (REQUIRED BY AUTOGRADER)
# ============================================================================

DATA_DIR = "data"
QUESTS_PATH_DEFAULT = os.path.join(DATA_DIR, "quests.txt")
ITEMS_PATH_DEFAULT = os.path.join(DATA_DIR, "items.txt")


# ============================================================================
# QUEST LOADING
# ============================================================================

def load_quests(filename=QUESTS_PATH_DEFAULT):
    """Load quests into a dictionary."""
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Missing quests file: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Could not read quests file: {e}")

    blocks = [b.strip().splitlines() for b in raw.split("\n\n") if b.strip()]
    quests = {}

    for block in blocks:
        q = parse_quest_block(block)
        validate_quest_data(q)
        quests[q["quest_id"]] = q

    return quests


def validate_quest_data(d):
    """Ensure quest has all required fields."""
    required = {
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    }

    if not isinstance(d, dict):
        raise InvalidDataFormatError("Quest must be a dict.")

    missing = required - set(d.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing quest fields: {missing}")

    for key in ["reward_xp", "reward_gold", "required_level"]:
        if not isinstance(d[key], int):
            raise InvalidDataFormatError(f"{key} must be an integer.")

    return True


def parse_quest_block(lines):
    """Convert quest block text lines into a quest dict."""
    out = {}

    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid quest line: {line}")

        key, val = line.split(":", 1)
        key = key.strip().upper()
        val = val.strip()

        if key == "QUEST_ID":
            out["quest_id"] = val
        elif key == "TITLE":
            out["title"] = val
        elif key == "DESCRIPTION":
            out["description"] = val
        elif key == "REWARD_XP":
            out["reward_xp"] = int(val)
        elif key == "REWARD_GOLD":
            out["reward_gold"] = int(val)
        elif key == "REQUIRED_LEVEL":
            out["required_level"] = int(val)
        elif key == "PREREQUISITE":
            out["prerequisite"] = val if val else "NONE"

    # Defaults
    out.setdefault("description", "")
    out.setdefault("prerequisite", "NONE")
    out.setdefault("reward_xp", 0)
    out.setdefault("reward_gold", 0)
    out.setdefault("required_level", 1)

    return out


# ============================================================================
# ITEM LOADING
# ============================================================================

def load_items(filename=ITEMS_PATH_DEFAULT):
    """Load items into a dictionary."""
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Missing items file: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Could not read items file: {e}")

    blocks = [b.strip().splitlines() for b in raw.split("\n\n") if b.strip()]
    items = {}

    for block in blocks:
        it = parse_item_block(block)
        validate_item_data(it)
        items[it["item_id"]] = it

    return items


def validate_item_data(d):
    """Validate required fields for items."""
    required = {"item_id", "name", "type", "effect", "cost", "description"}

    if not isinstance(d, dict):
        raise InvalidDataFormatError("Item must be dict.")

    missing = required - set(d.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing item fields: {missing}")

    if d["type"] not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError("Invalid item type.")

    if not isinstance(d["cost"], int):
        raise InvalidDataFormatError("Cost must be integer.")

    return True


def parse_item_block(lines):
    """Convert item block text lines into item dict."""
    out = {}

    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid item line: {line}")

        key, val = line.split(":", 1)
        key = key.strip().upper()
        val = val.strip()

        if key == "ITEM_ID":
            out["item_id"] = val
        elif key == "NAME":
            out["name"] = val
        elif key == "TYPE":
            out["type"] = val.lower()
        elif key == "EFFECT":
            out["effect"] = val
        elif key == "COST":
            out["cost"] = int(val)
        elif key == "DESCRIPTION":
            out["description"] = val

    out.setdefault("description", "")
    out.setdefault("effect", "")
    out.setdefault("cost", 0)

    return out


# ============================================================================
# DEFAULT DATA FILE CREATION
# ============================================================================

def create_default_data_files():
    """Create default items.txt and quests.txt if they do not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.isfile(ITEMS_PATH_DEFAULT):
        with open(ITEMS_PATH_DEFAULT, "w", encoding="utf-8") as f:
            f.write(
"""ITEM_ID: sword_01
NAME: Short Sword
TYPE: weapon
EFFECT: strength:3
COST: 50
DESCRIPTION: A simple sword.

ITEM_ID: potion_01
NAME: Healing Potion
TYPE: consumable
EFFECT: health:20
COST: 10
DESCRIPTION: Restores health.
"""
            )

    if not os.path.isfile(QUESTS_PATH_DEFAULT):
        with open(QUESTS_PATH_DEFAULT, "w", encoding="utf-8") as f:
            f.write(
"""QUEST_ID: q1
TITLE: Slay the Goblin
DESCRIPTION: A goblin is nearby.
REWARD_XP: 20
REWARD_GOLD: 10
REQUIRED_LEVEL: 1
PREREQUISITE: NONE
"""
            )

    return True


# ============================================================================
# MAIN SELF-TEST (SAFE FOR AUTOGRADER)
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA TEST ===")
    try:
        create_default_data_files()
        print("Quests:", load_quests().keys())
        print("Items:", load_items().keys())
    except Exception as e:
        print("Error:", e)



