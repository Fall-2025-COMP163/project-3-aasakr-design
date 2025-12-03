"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Corrected Implementation
"""

import os

# Using the standard 'json' library for robust character saving/loading 
# is better practice than manual key:value parsing, as it handles complex types 
# like lists and dictionaries without issues. However, since the prompt implies 
# simple file I/O, we'll stick to the manual parsing but make it safe.
import json # Import json for reliable data handling, if allowed. 
# NOTE: If 'json' is outside the scope of "Exceptions and Modules," 
# you should revert to the file format you used previously, but the 
# exception handling below remains correct.

from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================
# SAVE DIRECTORY & SETUP
# ============================================================

SAVE_DIR = os.path.join("data", "save_games")
os.makedirs(SAVE_DIR, exist_ok=True)

# ============================================================
# CHARACTER CLASS DEFINITIONS (Required for Project)
# ============================================================

_VALID_CLASSES = {
    "Warrior": {"max_health": 120, "strength": 15, "magic": 5},
    "Mage":      {"max_health": 80,  "strength": 8,   "magic": 20},
    "Rogue":   {"max_health": 90,  "strength": 12, "magic": 10},
    "Cleric":  {"max_health": 100, "strength": 10, "magic": 15},
}

# ============================================================
# CHARACTER CREATION
# ============================================================

def create_character(name, character_class):
    """Create a new character dictionary with base stats."""
    # Check 1: Validate character class
    if character_class not in _VALID_CLASSES:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}. Must be one of {list(_VALID_CLASSES.keys())}.")

    base = _VALID_CLASSES[character_class]

    return {
        "name": name,
        "class": character_class,
        "level": 1,
        "experience": 0,
        "health": base["max_health"],
        "max_health": base["max_health"],
        "strength": base["strength"],
        "magic": base["magic"],
        "gold": 0,
        "inventory": [],  # List of item IDs
        "equipped_gear": {}, # Dictionary for equipped item IDs/objects
        "active_quests": [],
        "completed_quests": []
    }

# ============================================================
# FILE HELPERS
# ============================================================

def _save_path(name):
    """Generates the full save file path."""
    return os.path.join(SAVE_DIR, f"{name}_save.json") # Using JSON is recommended for data integrity

# ============================================================
# SAVE CHARACTER
# ============================================================

def save_character(character):
    """Save character to a file using JSON for robustness."""
    if not isinstance(character, dict):
        raise InvalidSaveDataError("Character data is not a dictionary.")

    path = _save_path(character["name"])

    try:
        # Use JSON to reliably save the complex dictionary structure
        with open(path, "w") as f:
            json.dump(character, f, indent=4)
        return True
    # Catch specific I/O errors (e.g., permission denied)
    except (IOError, OSError) as e:
        raise SaveFileCorruptedError(f"Could not save character to file: {e}")
    except Exception as e:
        # Catch errors during serialization (e.g., non-JSON serializable data)
        raise InvalidSaveDataError(f"Serialization error during save: {e}")

# ============================================================
# LOAD CHARACTER
# ============================================================

def load_character(name):
    """Load a saved character from a file."""
    path = _save_path(name)

    if not os.path.exists(path):
        raise CharacterNotFoundError(f"Save file for '{name}' is missing.")

    try:
        with open(path, "r") as f:
            data = json.load(f)
            
    # Catch file reading errors (e.g., file exists but cannot be read)
    except (IOError, OSError) as e:
        raise SaveFileCorruptedError(f"Cannot read file: {e}")
    # Catch JSON parsing errors (file is corrupt)
    except json.JSONDecodeError as e:
        raise SaveFileCorruptedError(f"Save file is corrupt (JSON error): {e}")

    # --- Post-Load Validation ---
    required = [
        "name", "class", "level", "experience", "health", "max_health",
        "strength", "magic", "gold", "inventory", "active_quests",
        "completed_quests"
    ]

    for field in required:
        if field not in data:
            raise InvalidSaveDataError(f"Loaded data is missing required field: '{field}'.")
        
    # Ensure key numeric fields are integers (crucial for combat/inventory math)
    try:
        for key in ["level", "experience", "health", "max_health", "strength", "magic", "gold"]:
            data[key] = int(data[key])
    except (TypeError, ValueError):
        raise InvalidSaveDataError("Corrupted data type: Numeric field found non-numeric value.")
        
    return data

# ============================================================
# DELETE CHARACTER
# ============================================================

def delete_character(name):
    """Delete saved character."""
    path = _save_path(name)
    if not os.path.exists(path):
        raise CharacterNotFoundError(f"Save file for '{name}' is missing.")
    
    try:
        os.remove(path)
    # Catch OS errors (e.g., permission denied to delete)
    except OSError as e:
        raise SaveFileCorruptedError(f"Could not delete save file due to OS error: {e}")

# ============================================================
# CHARACTER STAT FUNCTIONS
# ============================================================

def gain_experience(character, xp):
    """Gain XP and handle level up."""
    if character.get("health", 0) <= 0:
        raise CharacterDeadError("Character is dead and cannot gain experience.")

    character["experience"] += xp

    leveled = False
    # Level-up formula (based on your provided logic)
    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]
        leveled = True

    return leveled

def add_gold(character, amount):
    """Add or subtract gold."""
    if not isinstance(amount, int) or amount == 0:
        return character["gold"]
        
    new = character.get("gold", 0) + amount
    
    # Check 1: Ensure gold doesn't go below zero
    if new < 0:
        raise ValueError("Gold cannot be negative after transaction.")
        
    character["gold"] = new
    return new

def heal_character(character, amount):
    """Heal character without exceeding max health."""
    # Ensure health and max_health are treated as integers
    current_health = int(character.get("health", 0))
    max_health = int(character.get("max_health", 0))
    
    if current_health <= 0:
        raise CharacterDeadError("Cannot heal a dead character.")
        
    healed = min(amount, max_health - current_health)
    character["health"] = current_health + healed
    return healed

def display_status(character):
    """Prints the character's current status and statistics."""
    # This is a presentation function, ensuring all stats are displayed cleanly
    
    print("\n--- Character Status ---")
    print(f"Name: {character.get('name', 'N/A')}")
    print(f"Class: {character.get('class', 'N/A')}")
    print(f"Level: {character.get('level', 0)}")
    print(f"Experience: {character.get('experience', 0)}")
    print(f"Health: {character.get('health', 0)} / {character.get('max_health', 0)}")
    print(f"Strength: {character.get('strength', 0)}")
    print(f"Magic: {character.get('magic', 0)}")
    print(f"Gold: {character.get('gold', 0)}")
    print("------------------------\n")
