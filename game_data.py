"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

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

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename=QUESTS_PATH_DEFAULT):
    """
    Load quests file into dict {quest_id: quest_dict}
    """
    if not os.path.isfile(filename):
        raise MissingDataFileError(f"Quests file missing: {filename}")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Could not read quests file: {e}")

    # Split into blocks separated by blank lines
    blocks = [b.strip().splitlines() for b in raw.split("\n\n") if b.strip()]
    quests = {}
    for block in blocks:
        try:
            q = parse_quest_block(block)
            qid = q.get("quest_id")
            if not qid:
                raise InvalidDataFormatError("Quest missing QUEST_ID.")
            validate_quest_data(q)
            quests[qid] = q
        except InvalidDataFormatError:
            raise
        except Exception as e:
            raise CorruptedDataError(f"Error parsing quest block: {e}")
    return quests

def validate_quest_data(quest_dict):
    required = {"quest_id", "title", "description", "reward_xp", "reward_gold", "required_level", "prerequisite"}
    if not isinstance(quest_dict, dict):
        raise InvalidDataFormatError("Quest must be a dictionary.")
    missing = required - set(quest_dict.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing quest fields: {', '.join(sorted(missing))}")
    # numeric checks
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
    # effect format validated later in inventory_system
    return True
    
def create_default_data_files():
    """
    Create default items.txt and quests.txt in data/ if they don't exist.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    # Default items
    if not os.path.isfile(ITEMS_PATH_DEFAULT):
        default_items = """ITEM_ID: sword_01
NAME: Short Sword
TYPE: weapon
EFFECT: strength:3
COST: 50
DESCRIPTION: A simple iron short sword.

ITEM_ID: robe_01
NAME: Apprentice Robe
TYPE: armor
EFFECT: max_health:10
COST: 30
DESCRIPTION: Basic robe for budding spellcasters.

ITEM_ID: potion_01
NAME: Healing Potion
TYPE: consumable
EFFECT: health:20
COST: 10
DESCRIPTION: Restores a small amount of health.
"""
        with open(ITEMS_PATH_DEFAULT, "w", encoding="utf-8") as f:
            f.write(default_items)

    # Default quests
    if not os.path.isfile(QUESTS_PATH_DEFAULT):
        default_quests = """QUEST_ID: q1
TITLE: Slay the Goblin
DESCRIPTION: A goblin prowls nearby. Deal with it.
REWARD_XP: 20
REWARD_GOLD: 10
REQUIRED_LEVEL: 1
PREREQUISITE: NONE

QUEST_ID: q2
TITLE: Orcish Raid
DESCRIPTION: Orcs have raided a farm.
REWARD_XP: 50
REWARD_GOLD: 25
REQUIRED_LEVEL: 2
PREREQUISITE: q1

QUEST_ID: q3
TITLE: Dragon Menace
DESCRIPTION: A dragon threatens the countryside.
REWARD_XP: 300
REWARD_GOLD: 200
REQUIRED_LEVEL: 5
PREREQUISITE: NONE
"""
        with open(QUESTS_PATH_DEFAULT, "w", encoding="utf-8") as f:
            f.write(default_quests)

    return True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    """
    Parse lines of a quest block into a dict.
    """
    out = {}
    for lineno, line in enumerate(lines, start=1):
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
            # ignore unknown keys but keep them if needed
            out[key.lower()] = val
    # normalize missing optional fields
    out.setdefault("description", "")
    out.setdefault("prerequisite", "NONE")
    out.setdefault("reward_xp", 0)
    out.setdefault("reward_gold", 0)
    out.setdefault("required_level", 1)
    return out


def parse_item_block(lines):
    """
    Parse lines of an item block into a dict.
    """
    out = {}
    for lineno, line in enumerate(lines, start=1):
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
    # defaults
    out.setdefault("description", "")
    out.setdefault("effect", "")
    out.setdefault("cost", 0)
    return out


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
   try:
        create_default_data_files()
        quests = load_quests()
        items = load_items()
        print("Quests loaded:", list(quests.keys()))
        print("Items loaded:", list(items.keys()))
    except Exception as e:
        print("Error:", e)


