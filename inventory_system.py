"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError,
)

MAX_INVENTORY_SIZE = 20


# ---------------------------------------------------------------------------
# BASIC INVENTORY
# ---------------------------------------------------------------------------

def _ensure_inventory(character):
    if "inventory" not in character or character["inventory"] is None:
        character["inventory"] = []
    return character["inventory"]


def add_item_to_inventory(character, item_id):
    inv = _ensure_inventory(character)
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    inv.append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not found.")
    inv.remove(item_id)
    return True


# ---------------------------------------------------------------------------
# ITEM EFFECT HELPERS
# ---------------------------------------------------------------------------

def parse_item_effect(effect_string):
    if not isinstance(effect_string, str) or ":" not in effect_string:
        raise InvalidItemTypeError("Invalid effect format.")
    stat, val_str = effect_string.split(":", 1)
    stat = stat.strip()
    try:
        value = int(val_str.strip())
    except ValueError:
        raise InvalidItemTypeError("Effect value must be int.")
    return stat, value


def apply_stat_effect(character, stat, value):
    if stat == "health":
        max_hp = character.get("max_health", 0)
        old = character.get("health", 0)
        new = min(max_hp, old + value)
        character["health"] = new
        return new - old

    if stat == "max_health":
        character["max_health"] = character.get("max_health", 0) + value
        return value

    if stat == "strength":
        character["strength"] = character.get("strength", 0) + value
        return value

    if stat == "magic":
        character["magic"] = character.get("magic", 0) + value
        return value

    raise InvalidItemTypeError(f"Unknown stat '{stat}'.")


# ---------------------------------------------------------------------------
# USING ITEMS
# ---------------------------------------------------------------------------

def use_item(character, item_id, item_data):
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    if item_data.get("type") != "consumable":
        raise InvalidItemTypeError("Only consumables can be used.")

    stat, val = parse_item_effect(item_data.get("effect", "health:0"))
    healed = apply_stat_effect(character, stat, val)

    remove_item_from_inventory(character, item_id)

    return healed


# ---------------------------------------------------------------------------
# EQUIPPING ITEMS
# ---------------------------------------------------------------------------

def equip_weapon(character, item_id, item_data):
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("Not a weapon.")

    # Unequip old weapon
    if "equipped_weapon" in character:
        old_stat, old_val = character["equipped_weapon_bonus"]
        character[old_stat] -= old_val
        inv.append(character["equipped_weapon"])

    stat, val = parse_item_effect(item_data["effect"])
    character[stat] += val

    character["equipped_weapon"] = item_id
    character["equipped_weapon_bonus"] = (stat, val)

    inv.remove(item_id)
    return True


def equip_armor(character, item_id, item_data):
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("Not armor.")

    if "equipped_armor" in character:
        old_stat, old_val = character["equipped_armor_bonus"]
        apply_stat_effect(character, old_stat, -old_val)
        inv.append(character["equipped_armor"])

    stat, val = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, val)

    character["equipped_armor"] = item_id
    character["equipped_armor_bonus"] = (stat, val)

    inv.remove(item_id)
    return True


# ---------------------------------------------------------------------------
# SHOP
# ---------------------------------------------------------------------------

def purchase_item(character, item_id, item_data):
    cost = item_data.get("cost", 0)
    gold = character.get("gold", 0)

    if gold < cost:
        raise InsufficientResourcesError("Not enough gold")

    inv = _ensure_inventory(character)
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full")

    character["gold"] = gold - cost
    inv.append(item_id)
    return True


def sell_item(character, item_id, item_data):
    inv = _ensure_inventory(character)

    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    sell_price = item_data.get("cost", 0) // 2
    inv.remove(item_id)
    character["gold"] = character.get("gold", 0) + sell_price
    return sell_price

