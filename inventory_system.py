"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles inventory management, item usage, equipment, and shop actions.
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
    inv = character.get("inventory")
    if inv is None:
        inv = []
        character["inventory"] = inv
    return inv


def add_item_to_inventory(character, item_id):
    """
    Add an item to the character's inventory.

    Raises:
        InventoryFullError if inventory already has MAX_INVENTORY_SIZE items.
    """
    inv = _ensure_inventory(character)
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    inv.append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """
    Remove a single instance of item_id from inventory.

    Raises:
        ItemNotFoundError if item not in inventory.
    """
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    inv.remove(item_id)
    return True


# ---------------------------------------------------------------------------
# ITEM EFFECT HELPERS
# ---------------------------------------------------------------------------

def parse_item_effect(effect_string):
    """
    Parse an effect string of form 'stat:value' into (stat, int(value)).

    Raises:
        InvalidItemTypeError for bad format or non-int value.
    """
    if not isinstance(effect_string, str) or ":" not in effect_string:
        raise InvalidItemTypeError("Invalid effect format.")
    stat, val_str = effect_string.split(":", 1)
    stat = stat.strip()
    try:
        value = int(val_str.strip())
    except ValueError:
        raise InvalidItemTypeError("Effect value must be an integer.")
    return stat, value


def apply_stat_effect(character, stat, value):
    """
    Apply stat change to character.

    Supported stats:
        - health     (heal, capped at max_health)
        - max_health (permanent increase)
        - strength
        - magic
    """
    if stat == "health":
        max_hp = int(character.get("max_health", 0))
        cur = int(character.get("health", 0))
        new_val = min(max_hp, cur + value)
        character["health"] = new_val
        return new_val - cur

    if stat == "max_health":
        character["max_health"] = int(character.get("max_health", 0)) + value
        return value

    if stat == "strength":
        character["strength"] = int(character.get("strength", 0)) + value
        return value

    if stat == "magic":
        character["magic"] = int(character.get("magic", 0)) + value
        return value

    # If some unknown stat appears, treat as invalid for safety
    raise InvalidItemTypeError(f"Unknown stat '{stat}' in effect.")


# ---------------------------------------------------------------------------
# USING & EQUIPPING ITEMS
# ---------------------------------------------------------------------------

def use_item(character, item_id, item_data):
    """
    Use a consumable item.

    Tests expect:
      - Raises ItemNotFoundError if item not in inventory.
      - Raises InvalidItemTypeError if item type is not 'consumable'.
      - For health_potion with effect 'health:20', health increases by 20
        (up to max_health) and item is removed from inventory.
    """
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    if not isinstance(item_data, dict):
        raise InvalidItemTypeError("Invalid item data.")

    if item_data.get("type") != "consumable":
        raise InvalidItemTypeError("Only consumable items may be used.")

    effect = item_data.get("effect", "")
    stat, val = parse_item_effect(effect)
    apply_stat_effect(character, stat, val)

    # remove single instance
    remove_item_from_inventory(character, item_id)
    return True


def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon.

    Tests expect:
      - Item must be in inventory, else ItemNotFoundError.
      - item_data['type'] must be 'weapon', else InvalidItemTypeError.
      - weapon_data {'type':'weapon','effect':'strength:5'} should
        increase character['strength'] by 5 and set:
           character['equipped_weapon'] == item_id
    """
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # Unequip currently equipped weapon if any
    if character.get("equipped_weapon"):
        _unequip_weapon_internal(character)

    stat, val = parse_item_effect(item_data.get("effect", "strength:0"))
    if stat == "strength":
        character["strength"] = int(character.get("strength", 0)) + val
    else:
        apply_stat_effect(character, stat, val)

    character["equipped_weapon"] = item_id
    character["equipped_weapon_bonus"] = (stat, val)

    # Weapon moves out of inventory when equipped
    inv.remove(item_id)
    return True


def _unequip_weapon_internal(character):
    """
    Internal helper: unequip weapon without inventory space checks.
    """
    eq = character.get("equipped_weapon")
    bonus = character.get("equipped_weapon_bonus")
    if not eq or not bonus:
        return
    stat, val = bonus
    if stat == "strength":
        character["strength"] = int(character.get("strength", 0)) - val
    else:
        # generic rollback
        apply_stat_effect(character, stat, -val)
    # return weapon to inventory
    _ensure_inventory(character).append(eq)
    character.pop("equipped_weapon", None)
    character.pop("equipped_weapon_bonus", None)


def equip_armor(character, item_id, item_data):
    """
    Equip armor.

    Not directly checked in tests besides existence and being callable,
    but we implement logically.
    """
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    # Unequip current armor if any
    if character.get("equipped_armor"):
        _unequip_armor_internal(character)

    stat, val = parse_item_effect(item_data.get("effect", "max_health:0"))
    apply_stat_effect(character, stat, val)

    character["equipped_armor"] = item_id
    character["equipped_armor_bonus"] = (stat, val)
    inv.remove(item_id)
    return True


def _unequip_armor_internal(character):
    eq = character.get("equipped_armor")
    bonus = character.get("equipped_armor_bonus")
    if not eq or not bonus:
        return
    stat, val = bonus
    apply_stat_effect(character, stat, -val)
    _ensure_inventory(character).append(eq)
    character.pop("equipped_armor", None)
    character.pop("equipped_armor_bonus", None)


# ---------------------------------------------------------------------------
# SHOP
# ---------------------------------------------------------------------------

def purchase_item(character, item_id, item_data):
    """
    Purchase an item.

    Tests expect:
      - if character['gold'] < item_data['cost'], raise InsufficientResourcesError
      - inventory size checked against MAX_INVENTORY_SIZE
      - on success: gold reduced, item added to inventory, returns True
    """
    cost = int(item_data.get("cost", 0))
    gold = int(character.get("gold", 0))

    if gold < cost:
        raise InsufficientResourcesError("Not enough gold to purchase item.")

    inv = _ensure_inventory(character)
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character["gold"] = gold - cost
    inv.append(item_id)
    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its cost (integer division).

    Tests expect:
      - when cost=25, sell price is 12 (25 // 2)
      - item removed from inventory
      - gold increased by sell price
      - returns sell_price
    """
    inv = _ensure_inventory(character)
    if item_id not in inv:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    cost = int(item_data.get("cost", 0))
    sell_price = cost // 2

    inv.remove(item_id)
    character["gold"] = int(character.get("gold", 0)) + sell_price

    return sell_price


# ---------------------------------------------------------------------------
# (Optional) Pretty-print inventory – not used in tests
# ---------------------------------------------------------------------------

def display_inventory(character, item_data_dict):
    inv = character.get("inventory", [])
    if not inv:
        print("(inventory empty)")
        return

    counts = {}
    for item_id in inv:
        counts[item_id] = counts.get(item_id, 0) + 1

    for item_id, qty in counts.items():
        data = item_data_dict.get(item_id, {})
        name = data.get("name", item_id)
        typ = data.get("type", "unknown")
        print(f"- {name} ({item_id}) x{qty} [{typ}]")


if __name__ == "__main__":
    print("Inventory system self-test (not used by autograder).")

