"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Test-focused implementation

Name: [Your Name Here]
AI Usage: [Document any AI assistance used]

Handles loading and validating quest and item data.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError,
)

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_QUESTS_PATH = os.path.join(DATA_DIR, "quests.txt")
DEFAULT_ITEMS_PATH = os.path.join(DATA_DIR, "items.txt")

# ---------------------------------------------------------------------------
# PARSING HELPERS
# ---------------------------------------------------------------------------

def parse_quest_block(lines):
    """Parse a list of quest lines into a dict with lowercase keys."""
    quest = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid quest line: {line}")
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
            # ignore extra keys for this project
            pass

    # Give defaults if missing
    quest.setdefault("description", "")
    quest.setdefault("reward_xp", 0)
    quest.setdefault("reward_gold", 0)
    quest.setdefault("required_level", 1)
    quest.setdefault("prerequisite", "NONE")

    return quest


def parse_item_block(lines):
    """Parse a list of item lines into a dict with lowercase keys."""
    item = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid item line: {line}")
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
            pass

    item.setdefault("description", "")
    item.setdefault("effect", "")
    item.setdefault("cost", 0)

    return item


# ---------------------------------------------------------------------------
# LOAD FUNCTIONS (USED BY TESTS)
# ---------------------------------------------------------------------------

def load_quests(filename="data/quests.txt"):
    """Load quests from file into dict {quest_id: quest_dict}."""
    # Resolve relative path from project root
    if not os.path.isabs(filename):
        path = os.path.join(os.getcwd(), filename)
    else:
        path = filename

    if not os.path.isfile(path):
        raise MissingDataFileError(f"Quest file not found: {filename}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise CorruptedDataError(f"Error reading quest file: {e}")

    blocks_raw = [b for b in content.split("\n\n") if b.strip()]
    quests = {}

    try:
        for block in blocks_raw:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            q = parse_quest_block(lines)
            validate_quest_data(q)
            quests[q["quest_id"]] = q
    except InvalidDataFormatError:
        # Let InvalidDataFormatError bubble up for the invalid-format test
        raise
    except Exception as e:
        # Any other unexpected issues count as corrupted
        raise CorruptedDataError(f"Error parsing quest data: {e}")

    return quests


def load_items(filename="data/items.txt"):
    """Load items from file into dict {item_id: item_dict}."""
    if not os.path.isabs(filename):
        path = os.path.join(os.getcwd(), filename)
    else:
        path = filename

    if not os.path.isfile(path):
        raise MissingDataFileError(f"Item file not found: {filename}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise CorruptedDataError(f"Error reading item file: {e}")

    blocks_raw = [b for b in content.split("\n\n") if b.strip()]
    items = {}

    try:
        for block in blocks_raw:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            it = parse_item_block(lines)
            validate_item_data(it)
            items[it["item_id"]] = it
    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise CorruptedDataError(f"Error parsing item data: {e}")

    return items


# ---------------------------------------------------------------------------
# VALIDATION (USED DIRECTLY BY TESTS)
# ---------------------------------------------------------------------------

def validate_quest_data(quest_dict):
    """Check a quest dict has required keys & numeric fields."""
    required = {
        "quest_id",
        "title",
        "description",
        "reward_xp",
        "reward_gold",
        "required_level",
        "prerequisite",
    }
    if not isinstance(quest_dict, dict):
        raise InvalidDataFormatError("Quest must be a dict")
    missing = required - set(quest_dict.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing quest fields: {', '.join(sorted(missing))}")

    for k in ("reward_xp", "reward_gold", "required_level"):
        if not isinstance(quest_dict.get(k), int):
            raise InvalidDataFormatError(f"Quest field '{k}' must be an integer")

    return True


def validate_item_data(item_dict):
    """Check an item dict has required keys & valid types."""
    required = {"item_id", "name", "type", "effect", "cost", "description"}
    if not isinstance(item_dict, dict):
        raise InvalidDataFormatError("Item must be a dict")
    missing = required - set(item_dict.keys())
    if missing:
        raise InvalidDataFormatError(f"Missing item fields: {', '.join(sorted(missing))}")

    if item_dict.get("type") not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError("Invalid item type")

    if not isinstance(item_dict.get("cost"), int):
        raise InvalidDataFormatError("Item 'cost' must be an integer")

    return True


# ---------------------------------------------------------------------------
# OPTIONAL: CREATE DEFAULT FILES (not used by tests but harmless)
# ---------------------------------------------------------------------------

def create_default_data_files():
    """Create default quests.txt and items.txt if they do not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.isfile(DEFAULT_QUESTS_PATH):
        with open(DEFAULT_QUESTS_PATH, "w", encoding="utf-8") as f:
            f.write("")

    if not os.path.isfile(DEFAULT_ITEMS_PATH):
        with open(DEFAULT_ITEMS_PATH, "w", encoding="utf-8") as f:
            f.write("")

