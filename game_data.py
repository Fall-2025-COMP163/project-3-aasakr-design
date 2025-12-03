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

# Paths
DATA_DIR = "data"
ITEMS_PATH_DEFAULT = os.path.join(DATA_DIR, "items.txt")
QUESTS_PATH_DEFAULT = os.path.join(DATA_DIR, "quests.txt")

# -----------------------------------------------------------------------------
# LOAD QUESTS
# -----------------------------------------------------------------------------

def load_quests(filename=QUESTS_PATH_DEFAULT):
    """Load quests from file into dict of quest_id -> quest dict."""
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Quests file missing: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        raise CorruptedDataError("Could not read quests file")

    blocks = raw.strip().split("\n\n")
    quests = {}

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        quest = parse_quest_block(lines)
        validate_quest_data(quest)
        quests[quest['quest_id']] = quest

    return quests

# -----------------------------------------------------------------------------
# LOAD ITEMS
# -----------------------------------------------------------------------------

def load_items(filename=ITEMS_PATH_DEFAULT):
    """Load items from file into dict of item_id -> item dict."""
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Items file missing: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        raise CorruptedDataError("Could not read items file")

    blocks = raw.strip().split("\n\n")
    items = {}

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        item = parse_item_block(lines)
        validate_item_data(item)
        items[item['item_id']] = item

    return items

# -----------------------------------------------------------------------------
# VALIDATION FUNCTIONS (Required By Autograder)
# -----------------------------------------------------------------------------

def validate_quest_data(quest):
    required = {
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    }

    if not isinstance(quest, dict):
        raise InvalidDataFormatError("Quest must be dict")

    missing = required - set(quest.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing quest fields: {missing}")

    if not isinstance(quest["reward_xp"], int):
        raise InvalidDataFormatError("reward_xp must be int")
    if not isinstance(quest["reward_gold"], int):
        raise InvalidDataFormatError("reward_gold must be int")
    if not isinstance(quest["required_level"], int):
        raise InvalidDataFormatError("required_level must be int")

    return True


def validate_item_data(item):
    required = {
        "item_id", "name", "type", "effect",
        "cost", "description"
    }

    if not isinstance(item, dict):
        raise InvalidDataFormatError("Item must be dict")

    missing = required - set(item.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing item fields: {missing}")

    if item["type"] not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError("Invalid item type")

    if not isinstance(item["cost"], int):
        raise InvalidDataFormatError("cost must be int")

    return True

# -----------------------------------------------------------------------------
# PARSING HELPERS
# -----------------------------------------------------------------------------

def parse_quest_block(lines):
    out = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError("Bad quest line")
        key, val = map(str.strip, line.split(":", 1))
        key = key.upper()

        if key == "QUEST_ID": out["quest_id"] = val
        elif key == "TITLE": out["title"] = val
        elif key == "DESCRIPTION": out["description"] = val
        elif key == "REWARD_XP": out["reward_xp"] = int(val)
        elif key == "REWARD_GOLD": out["reward_gold"] = int(val)
        elif key == "REQUIRED_LEVEL": out["required_level"] = int(val)
        elif key == "PREREQUISITE": out["prerequisite"] = val or "NONE"

    # defaults
    out.setdefault("description", "")
    out.setdefault("prerequisite", "NONE")
    out.setdefault("reward_xp", 0)
    out.setdefault("reward_gold", 0)
    out.setdefault("required_level", 1)

    return out


def parse_item_block(lines):
    out = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError("Bad item line")
        key, val = map(str.strip, line.split(":", 1))
        key = key.upper()

        if key == "ITEM_ID": out["item_id"] = val
        elif key == "NAME": out["name"] = val
        elif key == "TYPE": out["type"] = val.lower()
        elif key == "EFFECT": out["effect"] = val
        elif key == "COST": out["cost"] = int(val)
        elif key == "DESCRIPTION": out["description"] = val

    # defaults
    out.setdefault("effect", "")
    out.setdefault("description", "")
    out.setdefault("cost", 0)

    return out

# -----------------------------------------------------------------------------
# DEFAULT FILE CREATION
# -----------------------------------------------------------------------------

def create_default_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Items
    if not os.path.isfile(ITEMS_PATH_DEFAULT):
        with open(ITEMS_PATH_DEFAULT, "w") as f:
            f.write("ITEM_ID: test_item\nNAME: Test\nTYPE: consumable\nEFFECT: health:10\nCOST: 5\nDESCRIPTION: Test\n")

    # Quests
    if not os.path.isfile(QUESTS_PATH_DEFAULT):
        with open(QUESTS_PATH_DEFAULT, "w") as f:
            f.write("QUEST_ID: test_quest\nTITLE: Test\nDESCRIPTION: Test\nREWARD_XP: 10\nREWARD_GOLD: 5\nREQUIRED_LEVEL: 1\nPREREQUISITE: NONE\n")

    return True

