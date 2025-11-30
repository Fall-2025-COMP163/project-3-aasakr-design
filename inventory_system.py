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
    """
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    inv = character.setdefault("inventory", [])
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    inv.remove(item_id)
    return True

def has_item(character, item_id):
    """Return True if inventory contains item_id"""
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return item_id in character.get("inventory", [])

def count_item(character, item_id):
    """Return count of item_id in inventory"""
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return character.get("inventory", []).count(item_id)

def get_inventory_space_remaining(character):
    """Return how many more items can fit"""
    if not isinstance(character, dict):
        raise ValueError("Invalid character object.")
    return MAX_INVENTORY_SIZE - len(character.get("inventory", []))

def clear_inventory(character):
    """Remove all items, return list of removed items"""
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
    item_data is a dict describing the item (contains 'type' and 'effect').
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
    Equip a weapon: apply its effect (strength bonus).
    character will have keys: equipped_weapon (item_id) and equipped_weapon_bonus (int)
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
    # apply effect (assume stat == 'strength')
    if stat != "strength":
        # still allow but won't map to strength
        apply_stat_effect(character, stat, val)
    else:
        character["strength"] = character.get("strength", 0) + val
    character["equipped_weapon"] = item_id
    character["equipped_weapon_bonus"] = val
    # remove from inventory (weapon moves to equipped slot)
    remove_item_from_inventory(character, item_id)
    return f"Equipped weapon {item_data.get('name', item_id)} (+{val} strength)"

def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon: apply its effect (strength bonus).
    character will have keys: equipped_weapon (item_id) and equipped_weapon_bonus (int)
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
    # apply effect (assume stat == 'strength')
    if stat != "strength":
        # still allow but won't map to strength
        apply_stat_effect(character, stat, val)
    else:
        character["strength"] = character.get("strength", 0) + val
    character["equipped_weapon"] = item_id
    character["equipped_weapon_bonus"] = val
    # remove from inventory (weapon moves to equipped slot)
    remove_item_from_inventory(character, item_id)
    return f"Equipped weapon {item_data.get('name', item_id)} (+{val} strength)"

def unequip_weapon(character):
    """
    Unequip weapon, return item_id to inventory.
    """
    if not character.get("equipped_weapon"):
        return None
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot unequip: inventory is full.")
    item_id = character["equipped_weapon"]
    bonus = character.get("equipped_weapon_bonus", 0)
    # remove bonus
    character["strength"] = max(0, character.get("strength", 0) - bonus)
    # return to inventory
    add_item_to_inventory(character, item_id)
    # clear equipped fields
    character.pop("equipped_weapon", None)
    character.pop("equipped_weapon_bonus", None)
    return item_id


def unequip_armor(character):
    """
    Unequip armor, return item_id to inventory.
    """
    if not character.get("equipped_armor"):
        return None
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot unequip: inventory is full.")
    item_id = character["equipped_armor"]
    bonus = character.get("equipped_armor_bonus", 0)
    character["max_health"] = max(1, character.get("max_health", 0) - bonus)
    # ensure current health doesn't exceed new max
    if character.get("health", 0) > character.get("max_health", 0):
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
    Purchase item (item_data must contain 'cost' integer)
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
    Sell item for half its cost
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
    Parse "stat:value" into (stat, int(value))
    """
    if not isinstance(effect_string, str) or ":" not in effect_string:
        raise InvalidItemTypeError("Invalid effect format.")
    parts = effect_string.split(":", 1)
    stat = parts[0].strip()
    try:
        val = int(parts[1].strip())
    except Exception:
        raise InvalidItemTypeError("Effect value must be an integer.")
    return stat, val

def apply_stat_effect(character, stat_name, value):
    """
    Apply stat change. Valid: health, max_health, strength, magic
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
    Print a formatted inventory list: item name (id) xqty
    """
    inv = character.get("inventory", [])
    if not inv:
        print("  (empty)")
        return
    # count items
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
    
    # Test adding items
    # test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    # 
    # try:
    #     add_item_to_inventory(test_char, "health_potion")
    #     print(f"Inventory: {test_char['inventory']}")
    # except InventoryFullError:
    #     print("Inventory is full!")
    
    # Test using items
    # test_item = {
    #     'item_id': 'health_potion',
    #     'type': 'consumable',
    #     'effect': 'health:20'
    # }
    # 
    # try:
    #     result = use_item(test_char, "health_potion", test_item)
    #     print(result)
    # except ItemNotFoundError:
    #     print("Item not found")

