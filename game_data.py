"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
QUESTS_PATH_DEFAULT = os.path.join(DATA_DIR, "quests.txt")
ITEMS_PATH_DEFAULT = os.path.join(DATA_DIR, "items.txt")

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename=QUESTS_PATH_DEFAULT):
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Quests file missing: {filename}")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Could not read quests file: {e}")

    if not content.strip():
        raise InvalidDataFormatError("Quest file is empty.")

    quests = {}
    blocks = content.split("\n\n")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        quest = parse_quest_block(lines)  # may raise InvalidDataFormatError
        validate_quest_data(quest)
        qid = quest.get("quest_id")
        if not qid:
            raise InvalidDataFormatError("Quest missing quest_id.")
        quests[qid] = quest
    return quests


def load_items(filename=ITEMS_PATH_DEFAULT):
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Items file missing: {filename}")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Could not read items file: {e}")

    if not content.strip():
        raise InvalidDataFormatError("Item file is empty.")

    items = {}
    blocks = content.split("\n\n")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        item = parse_item_block(lines)
        validate_item_data(item)
        iid = item.get("item_id")
        if not iid:
            raise InvalidDataFormatError("Item missing item_id.")
        items[iid] = item
    return items

def validate_quest_data(quest_dict):
    required = {
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    }
    if not isinstance(quest_dict, dict):
        raise InvalidDataFormatError("Quest must be a dictionary.")
    missing = required - set(quest_dict.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing quest fields: {', '.join(sorted(missing))}")
    for num in ("reward_xp", "reward_gold", "required_level"):
        if not isinstance(quest_dict.get(num), int):
            raise InvalidDataFormatError(f"Quest field '{num}' must be an integer.")
    return True

def validate_item_data(item_dict):
    required = {"item_id", "name", "type", "effect", "cost", "description"}
    if not isinstance(item_dict, dict):
        raise InvalidDataFormatError("Item must be a dictionary.")
    missing = required - set(item_dict.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing item fields: {', '.join(sorted(missing))}")
    if item_dict.get("type") not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError("Invalid item type.")
    if not isinstance(item_dict.get("cost"), int):
        raise InvalidDataFormatError("Item 'cost' must be integer.")
    return True

def create_default_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.isfile(ITEMS_PATH_DEFAULT):
        default_items = """ITEM_ID: health_potion
NAME: Health Potion
TYPE: consumable
EFFECT: health:20
COST: 25
DESCRIPTION: Restores a small amount of health.
"""
        with open(ITEMS_PATH_DEFAULT, "w", encoding="utf-8") as f:
            f.write(default_items)

    if not os.path.isfile(QUESTS_PATH_DEFAULT):
        default_quests = """QUEST_ID: first_steps
TITLE: First Steps
DESCRIPTION: Complete your first adventure.
REWARD_XP: 50
REWARD_GOLD: 25
REQUIRED_LEVEL: 1
PREREQUISITE: NONE
"""
        with open(QUESTS_PATH_DEFAULT, "w", encoding="utf-8") as f:
            f.write(default_quests)

    return True

# ============================================================================
# PARSERS
# ============================================================================

def parse_quest_block(lines):
    out = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid quest line: '{line}'")
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
            try:
                out["reward_xp"] = int(val)
            except ValueError:
                raise InvalidDataFormatError("REWARD_XP must be an integer")
        elif key == "REWARD_GOLD":
            try:
                out["reward_gold"] = int(val)
            except ValueError:
                raise InvalidDataFormatError("REWARD_GOLD must be an integer")
        elif key == "REQUIRED_LEVEL":
            try:
                out["required_level"] = int(val)
            except ValueError:
                raise InvalidDataFormatError("REQUIRED_LEVEL must be an integer")
        elif key == "PREREQUISITE":
            out["prerequisite"] = val if val else "NONE"
        else:
            out[key.lower()] = val

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
            raise InvalidDataFormatError(f"Invalid item line: '{line}'")
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
            try:
                out["cost"] = int(val)
            except ValueError:
                raise InvalidDataFormatError("COST must be an integer")
        elif key == "DESCRIPTION":
            out["description"] = val
        else:
            out[key.lower()] = val

    out.setdefault("description", "")
    out.setdefault("effect", "")
    out.setdefault("cost", 0)
    return out

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    try:
        create_default_data_files()
        qs = load_quests()
        it = load_items()
        print("Quests loaded:", list(qs.keys()))
        print("Items loaded:", list(it.keys()))
    except Exception as e:
        print("Error:", e)

