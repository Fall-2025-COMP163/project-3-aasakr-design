"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory

    Raises InventoryFullError if inventory is full.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    inv = character.setdefault("inventory", [])
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    inv.append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """
    Remove one occurrence of item_id from inventory

    Raises ItemNotFoundError if the item is not present.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    inv = character.setdefault("inventory", [])
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    inv.remove(item_id)
    return True


def has_item(character, item_id):
    """
    Check if character has a specific item.

    Returns True if item_id is in inventory.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return item_id in character.get("inventory", [])


def count_item(character, item_id):
    """
    Count how many of a specific item the character has.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return character.get("inventory", []).count(item_id)


def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return MAX_INVENTORY_SIZE - len(character.get("inventory", []))


def clear_inventory(character):
    """
    Remove all items from inventory.

    Returns the list of removed items.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    prev = list(character.get("inventory", []))
    character["inventory"] = []
    return prev


# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory.

    Args:
        character: Character dict
        item_id: ID in inventory
        item_data: dict with at least 'type' and 'effect'

    Raises:
        ItemNotFoundError if not in inventory
        InvalidItemTypeError if not a consumable
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    if not isinstance(item_data, dict):
        raise InvalidItemTypeError("Invalid item_data provided.")

    typ = item_data.get("type")
    if typ != "consumable":
        raise InvalidItemTypeError("Only consumable items can be used.")

    effect = item_data.get("effect", "")
    stat, val = parse_item_effect(effect)
    apply_stat_effect(character, stat, val)

    # remove one instance
    remove_item_from_inventory(character, item_id)
    return f"Used {item_data.get('name', item_id)}: {stat} +{val}"


def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon: apply its effect (usually a strength bonus).

    character will have keys:
        - equipped_weapon (item_id)
        - equipped_weapon_bonus (int)

    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type != 'weapon'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # Unequip current weapon if present
    if character.get("equipped_weapon"):
        unequip_weapon(character)

    # Parse effect
    stat, val = parse_item_effect(item_data.get("effect", "strength:0"))

    # Apply effect (typically to strength)
    apply_stat_effect(character, stat, val)

    character["equipped_weapon"] = item_id
    character["equipped_weapon_bonus"] = val

    # Remove equipped weapon from inventory
    remove_item_from_inventory(character, item_id)
    return f"Equipped weapon {item_data.get('name', item_id)} (+{val} {stat})"


def equip_armor(character, item_id, item_data):
    """
    Equip armor: apply its effect (usually max_health bonus).

    character will have keys:
        - equipped_armor (item_id)
        - equipped_armor_bonus (int)

    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type != 'armor'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    # Unequip current armor if present
    if character.get("equipped_armor"):
        unequip_armor(character)

    # Parse effect (usually "max_health:10")
    stat, val = parse_item_effect(item_data.get("effect", "max_health:0"))
    apply_stat_effect(character, stat, val)

    character["equipped_armor"] = item_id
    character["equipped_armor_bonus"] = val

    # Remove equipped armor from inventory
    remove_item_from_inventory(character, item_id)
    return f"Equipped armor {item_data.get('name', item_id)} (+{val} {stat})"


def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory.

    Returns item_id or None if nothing equipped.
    Raises InventoryFullError if inventory has no space.
    """
    if not character.get("equipped_weapon"):
        return None

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot unequip: inventory is full.")

    item_id = character["equipped_weapon"]
    bonus = character.get("equipped_weapon_bonus", 0)

    # Remove stat bonus
    character["strength"] = max(0, character.get("strength", 0) - bonus)

    # Return weapon to inventory
    add_item_to_inventory(character, item_id)

    # Clear equipped fields
    character.pop("equipped_weapon", None)
    character.pop("equipped_weapon_bonus", None)
    return item_id


def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory.

    Returns item_id or None if nothing equipped.
    Raises InventoryFullError if inventory has no space.
    """
    if not character.get("equipped_armor"):
        return None

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot unequip: inventory is full.")

    item_id = character["equipped_armor"]
    bonus = character.get("equipped_armor_bonus", 0)

    # Remove max_health bonus
    character["max_health"] = max(1, character.get("max_health", 0) - bonus)

    # Ensure health doesn't exceed new max
    if character.get("health", 0) > character["max_health"]:
        character["health"] = character["max_health"]

    add_item_to_inventory(character, item_id)

    character.pop("equipped_armor", None)
    character.pop("equipped_armor_bonus", None)
    return item_id


# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item.

    Raises:
        InsufficientResourcesError if not enough gold
        InventoryFullError if inventory is full
    """
    cost = int(item_data.get("cost", 0))
    if character.get("gold", 0) < cost:
        raise InsufficientResourcesError("Not enough gold to purchase item.")
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    # Deduct gold and add item
    character["gold"] = character.get("gold", 0) - cost
    add_item_to_inventory(character, item_id)
    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its cost.

    Raises:
        ItemNotFoundError if character doesn't have the item
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    cost = int(item_data.get("cost", 0))
    sell_price = cost // 2

    remove_item_from_inventory(character, item_id)
    character["gold"] = character.get("gold", 0) + sell_price
    return sell_price


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse item effect string in the form "stat:value" into (stat, value).

    Raises InvalidItemTypeError if format or value is invalid.
    """
    if not isinstance(effect_string, str) or ":" not in effect_string:
        raise InvalidItemTypeError("Invalid effect format.")
    stat_part, value_part = effect_string.split(":", 1)
    stat = stat_part.strip()
    try:
        value = int(value_part.strip())
    except Exception:
        raise InvalidItemTypeError("Effect value must be an integer.")
    return stat, value


def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character.

    Valid stats:
        - health      (heals up to max_health)
        - max_health  (changes max_health)
        - strength
        - magic
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")

    if stat_name == "health":
        max_hp = character.get("max_health", 0)
        current = character.get("health", 0)
        healed = min(value, max_hp - current)
        character["health"] = current + healed
        return healed
    elif stat_name == "max_health":
        character["max_health"] = character.get("max_health", 0) + value
        return value
    elif stat_name == "strength":
        character["strength"] = character.get("strength", 0) + value
        return value
    elif stat_name == "magic":
        character["magic"] = character.get("magic", 0) + value
        return value
    else:
        raise InvalidItemTypeError(f"Unknown stat '{stat_name}'.")


def display_inventory(character, item_data_dict):
    """
    Display character's inventory in a readable format.
    """
    inv = character.get("inventory", [])
    if not inv:
        print("  (empty)")
        return

    # Count occurrences
    counts = {}
    for item_id in inv:
        counts[item_id] = counts.get(item_id, 0) + 1

    for item_id, qty in counts.items():
        info = item_data_dict.get(item_id, {})
        name = info.get("name", item_id)
        typ = info.get("type", "unknown")
        print(f"- {name} ({item_id}) x{qty} [{typ}]")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    # You can add quick manual tests here if you want.

