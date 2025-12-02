"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Implementation compatible with provided tests.

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError,
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory.

    Raises InventoryFullError if full.
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
    Remove an item from character's inventory.

    Raises ItemNotFoundError if not present.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    inv = character.setdefault("inventory", [])
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    inv.remove(item_id)
    return True


def has_item(character, item_id):
    """Return True if character has item_id."""
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return item_id in character.get("inventory", [])


def count_item(character, item_id):
    """Return count of item_id in inventory."""
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return character.get("inventory", []).count(item_id)


def get_inventory_space_remaining(character):
    """Return how many more items can fit."""
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return MAX_INVENTORY_SIZE - len(character.get("inventory", []))


def clear_inventory(character):
    """Remove all items and return list of removed items."""
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    previous = list(character.get("inventory", []))
    character["inventory"] = []
    return previous

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory.

    Raises:
      ItemNotFoundError if item not in inventory
      InvalidItemTypeError if item is not consumable
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    if not isinstance(item_data, dict):
        raise InvalidItemTypeError("Invalid item_data provided.")
    if item_data.get("type") != "consumable":
        # exactly what the test_invalid_item_type_exception expects
        raise InvalidItemTypeError("Only consumable items can be used.")

    effect_str = item_data.get("effect", "")
    stat, value = parse_item_effect(effect_str)
    apply_stat_effect(character, stat, value)

    # remove exactly one copy
    remove_item_from_inventory(character, item_id)
    return f"Used {item_data.get('name', item_id)}: {stat} +{value}"

# ============================================================================
# EQUIPMENT
# ============================================================================

def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon.

    If a weapon is already equipped:
      - unequip it (remove bonus, return to inventory)

    Raises:
      ItemNotFoundError if item not in inventory
      InvalidItemTypeError if item type is not 'weapon'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # Unequip current weapon if any
    if character.get("equipped_weapon"):
        unequip_weapon(character)

    stat, bonus = parse_item_effect(item_data.get("effect", "strength:0"))
    # assume weapon modifies strength
    if stat == "strength":
        character["strength"] = character.get("strength", 0) + bonus
    else:
        apply_stat_effect(character, stat, bonus)

    character["equipped_weapon"] = item_id
    character["equipped_weapon_bonus"] = bonus

    # Remove from inventory now that it's equipped
    remove_item_from_inventory(character, item_id)
    return f"Equipped weapon {item_data.get('name', item_id)} (+{bonus} strength)"


def equip_armor(character, item_id, item_data):
    """
    Equip armor.

    If armor is already equipped:
      - unequip it (remove bonus, return to inventory)

    Raises:
      ItemNotFoundError if item not in inventory
      InvalidItemTypeError if item type is not 'armor'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    # Unequip current armor if any
    if character.get("equipped_armor"):
        unequip_armor(character)

    stat, bonus = parse_item_effect(item_data.get("effect", "max_health:0"))
    if stat == "max_health":
        character["max_health"] = character.get("max_health", 0) + bonus
        # ensure health not above new max
        if character.get("health", 0) > character["max_health"]:
            character["health"] = character["max_health"]
    else:
        apply_stat_effect(character, stat, bonus)

    character["equipped_armor"] = item_id
    character["equipped_armor_bonus"] = bonus

    remove_item_from_inventory(character, item_id)
    return f"Equipped armor {item_data.get('name', item_id)} (+{bonus} {stat})"


def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory.

    Raises InventoryFullError if inventory is full.
    """
    weapon_id = character.get("equipped_weapon")
    if not weapon_id:
        return None

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot unequip weapon: inventory is full.")

    bonus = character.get("equipped_weapon_bonus", 0)
    character["strength"] = max(0, character.get("strength", 0) - bonus)

    add_item_to_inventory(character, weapon_id)
    character.pop("equipped_weapon", None)
    character.pop("equipped_weapon_bonus", None)
    return weapon_id


def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory.

    Raises InventoryFullError if inventory is full.
    """
    armor_id = character.get("equipped_armor")
    if not armor_id:
        return None

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot unequip armor: inventory is full.")

    bonus = character.get("equipped_armor_bonus", 0)
    character["max_health"] = max(1, character.get("max_health", 0) - bonus)
    if character.get("health", 0) > character["max_health"]:
        character["health"] = character["max_health"]

    add_item_to_inventory(character, armor_id)
    character.pop("equipped_armor", None)
    character.pop("equipped_armor_bonus", None)
    return armor_id

# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop.

    Raises:
      InsufficientResourcesError if not enough gold
      InventoryFullError if inventory is full
    """
    cost = int(item_data.get("cost", 0))
    gold = character.get("gold", 0)

    if gold < cost:
        raise InsufficientResourcesError("Not enough gold to purchase item.")

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    character["gold"] = gold - cost
    add_item_to_inventory(character, item_id)
    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its purchase cost.

    Raises ItemNotFoundError if character does not have the item.
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
    Parse item effect string "stat:value" into (stat, int(value)).

    Raises InvalidItemTypeError for bad formats.
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

    Valid stats: health, max_health, strength, magic

    Note: health cannot exceed max_health.
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")

    if stat_name == "health":
        max_hp = character.get("max_health", 0)
        current = character.get("health", 0)
        new_val = current + value
        if new_val > max_hp:
            new_val = max_hp
        character["health"] = new_val
        return new_val - current

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
        # For this project we treat unknown stats as invalid item type
        raise InvalidItemTypeError(f"Unknown stat '{stat_name}'.")


def display_inventory(character, item_data_dict):
    """
    Display character's inventory in a simple formatted way.
    Not used by tests, but helpful for playing.
    """
    inv = character.get("inventory", [])
    if not inv:
        print("(Inventory is empty)")
        return

    counts = {}
    for item_id in inv:
        counts[item_id] = counts.get(item_id, 0) + 1

    for item_id, qty in counts.items():
        data = item_data_dict.get(item_id, {})
        name = data.get("name", item_id)
        typ = data.get("type", "unknown")
        print(f"- {name} ({item_id}) x{qty} [{typ}]")

# ============================================================================
# TESTING (manual)
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    test_char = {"inventory": [], "gold": 100, "health": 50, "max_health": 100}
    add_item_to_inventory(test_char, "health_potion")
    print("Inventory after add:", test_char["inventory"])

