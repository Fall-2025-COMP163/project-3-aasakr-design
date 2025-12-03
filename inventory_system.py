"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Test-focused implementation

Name: [Your Name Here]
AI Usage: [Document any AI assistance used]
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError,
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ---------------------------------------------------------------------------
# INVENTORY MANAGEMENT
# ---------------------------------------------------------------------------

def add_item_to_inventory(character, item_id):
    """Add an item to character's inventory or raise InventoryFullError."""
    inv = character.setdefault("inventory", [])
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")
    inv.append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """Remove one occurrence of item_id or raise ItemNotFoundError."""
    inv = character.setdefault("inventory", [])
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not found")
    inv.remove(item_id)
    return True


def has_item(character, item_id):
    return item_id in character.get("inventory", [])


# ---------------------------------------------------------------------------
# ITEM EFFECT HELPERS
# ---------------------------------------------------------------------------

def parse_item_effect(effect_string):
    """Parse 'stat:value' into (stat, value:int)."""
    if not isinstance(effect_string, str) or ":" not in effect_string:
        raise InvalidItemTypeError("Invalid effect format")
    stat, val = effect_string.split(":", 1)
    stat = stat.strip()
    try:
        val_int = int(val.strip())
    except ValueError:
        raise InvalidItemTypeError("Effect value must be an integer")
    return stat, val_int


def apply_stat_effect(character, stat_name, value):
    """Apply stat change to character based on effect."""
    if stat_name == "health":
        # healing but not above max_health
        max_hp = character.get("max_health", 0)
        current = character.get("health", 0)
        new = current + value
        if new > max_hp:
            new = max_hp
        character["health"] = new
    elif stat_name == "max_health":
        character["max_health"] = character.get("max_health", 0) + value
    elif stat_name == "strength":
        character["strength"] = character.get("strength", 0) + value
    elif stat_name == "magic":
        character["magic"] = character.get("magic", 0) + value
    else:
        # Unknown stat – treat as invalid for this project
        raise InvalidItemTypeError(f"Unknown stat '{stat_name}'")
    return True


# ---------------------------------------------------------------------------
# ITEM USAGE
# ---------------------------------------------------------------------------

def use_item(character, item_id, item_data):
    """Use a consumable item; raises InvalidItemTypeError for non-consumables."""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory")

    if not isinstance(item_data, dict):
        raise InvalidItemTypeError("Item data must be a dictionary")

    if item_data.get("type") != "consumable":
        # tests rely on this raising for 'weapon' passed into use_item
        raise InvalidItemTypeError("Only consumable items can be used")

    effect = item_data.get("effect", "")
    stat, value = parse_item_effect(effect)
    apply_stat_effect(character, stat, value)

    # Remove one instance after use
    remove_item_from_inventory(character, item_id)
    return True


# ---------------------------------------------------------------------------
# EQUIPMENT
# ---------------------------------------------------------------------------

def equip_weapon(character, item_id, item_data):
    """Equip a weapon: increases strength based on effect."""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory")

    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("Item is not a weapon")

    # Unequip previous weapon, if any
    if character.get("equipped_weapon"):
        unequip_weapon(character)

    stat, value = parse_item_effect(item_data.get("effect", "strength:0"))

    # apply strength bonus
    if stat == "strength":
        character["strength"] = character.get("strength", 0) + value
    else:
        apply_stat_effect(character, stat, value)

    character["equipped_weapon"] = item_id
    character["equipped_weapon_bonus"] = value

    # remove weapon from inventory (now equipped)
    remove_item_from_inventory(character, item_id)
    return True


def unequip_weapon(character):
    """Unequip weapon and return it to inventory, reducing stats."""
    if not character.get("equipped_weapon"):
        return None

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full; cannot unequip weapon")

    item_id = character["equipped_weapon"]
    bonus = character.get("equipped_weapon_bonus", 0)

    # remove bonus
    character["strength"] = character.get("strength", 0) - bonus
    if character["strength"] < 0:
        character["strength"] = 0

    # return to inventory
    add_item_to_inventory(character, item_id)

    character.pop("equipped_weapon", None)
    character.pop("equipped_weapon_bonus", None)
    return item_id


def equip_armor(character, item_id, item_data):
    """Equip armor: typically affects max_health or magic; test only checks existence."""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory")

    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("Item is not armor")

    # Unequip existing armor
    if character.get("equipped_armor"):
        unequip_armor(character)

    stat, value = parse_item_effect(item_data.get("effect", "max_health:0"))

    if stat == "max_health":
        character["max_health"] = character.get("max_health", 0) + value
        # keep current health within new max
        if character.get("health", 0) > character["max_health"]:
            character["health"] = character["max_health"]
    else:
        apply_stat_effect(character, stat, value)

    character["equipped_armor"] = item_id
    character["equipped_armor_bonus"] = value

    remove_item_from_inventory(character, item_id)
    return True


def unequip_armor(character):
    """Unequip armor and return it to inventory."""
    if not character.get("equipped_armor"):
        return None

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full; cannot unequip armor")

    item_id = character["equipped_armor"]
    bonus = character.get("equipped_armor_bonus", 0)

    character["max_health"] = character.get("max_health", 0) - bonus
    if character["max_health"] < 1:
        character["max_health"] = 1
    if character.get("health", 0) > character["max_health"]:
        character["health"] = character["max_health"]

    add_item_to_inventory(character, item_id)

    character.pop("equipped_armor", None)
    character.pop("equipped_armor_bonus", None)
    return item_id


# ---------------------------------------------------------------------------
# SHOP SYSTEM
# ---------------------------------------------------------------------------

def purchase_item(character, item_id, item_data):
    """Buy an item: subtract gold, add to inventory. Checks cost and space."""
    cost = int(item_data.get("cost", 0))
    if character.get("gold", 0) < cost:
        raise InsufficientResourcesError("Not enough gold")

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")

    character["gold"] = character.get("gold", 0) - cost
    add_item_to_inventory(character, item_id)
    return True


def sell_item(character, item_id, item_data):
    """Sell item for half its cost, rounding down, and remove from inventory."""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory")

    cost = int(item_data.get("cost", 0))
    sell_price = cost // 2

    remove_item_from_inventory(character, item_id)
    character["gold"] = character.get("gold", 0) + sell_price
    return sell_price

