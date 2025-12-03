"""
Game Data Loader
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

DATA_DIR = "data"
QUESTS_PATH_DEFAULT = "data/quests.txt"
ITEMS_PATH_DEFAULT = "data/items.txt"


# ==============================
# LOAD QUESTS
# ==============================

def load_quests(filename=QUESTS_PATH_DEFAULT):
    if not os.path.isfile(filename):
        raise MissingDataFileError("Missing quests file.")

    try:
        text = open(filename).read()
    except:
        raise CorruptedDataError("Could not read quests.")

    blocks = [b.strip().splitlines() for b in text.split("\n\n") if b.strip()]

    quests = {}
    for block in blocks:
        q = parse_quest_block(block)
        quests[q["quest_id"]] = q

    return quests


def parse_quest_block(lines):
    quest = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError("Bad quest format.")
        key, val = line.split(":", 1)
        key = key.strip().upper()
        val = val.strip()

        if key == "QUEST_ID":
            quest["quest_id"] = val
        elif key == "TITLE":
            quest["title"] = val
        elif key == "DESCRIPTION":
            quest["description"] = val
        elif key == "REWARD_XP":
            quest["reward_xp"] = int(val)
        elif key == "REWARD_GOLD":
            quest["reward_gold"] = int(val)
        elif key == "REQUIRED_LEVEL":
            quest["required_level"] = int(val)
        elif key == "PREREQUISITE":
            quest["prerequisite"] = val

    required = ["quest_id", "reward_xp", "reward_gold", "required_level", "prerequisite"]

    for r in required:
        if r not in quest:
            raise InvalidDataFormatError("Missing quest field.")

    return quest


# ==============================
# LOAD ITEMS
# ==============================

def load_items(filename=ITEMS_PATH_DEFAULT):
    if not os.path.isfile(filename):
        raise MissingDataFileError("Missing items file.")

    try:
        text = open(filename).read()
    except:
        raise CorruptedDataError("Items unreadable.")

    blocks = [b.strip().splitlines() for b in text.split("\n\n") if b.strip()]

    items = {}
    for block in blocks:
        itm = parse_item_block(block)
        items[itm["item_id"]] = itm

    return items


def parse_item_block(lines):
    item = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError("Bad item format.")
        key, val = line.split(":", 1)
        key = key.strip().upper()
        val = val.strip()

        if key == "ITEM_ID":
            item["item_id"] = val
        elif key == "NAME":
            item["name"] = val
        elif key == "TYPE":
            item["type"] = val.lower()
        elif key == "EFFECT":
            item["effect"] = val
        elif key == "COST":
            item["cost"] = int(val)
        elif key == "DESCRIPTION":
            item["description"] = val

    return item

