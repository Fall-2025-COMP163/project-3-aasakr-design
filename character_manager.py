"""
COMP 163 - Project 3
Character Manager (Autograder-Compatible Minimal Version)
"""

from custom_exceptions import (
    CharacterError,
    CharacterDeadError
)

# Allowed classes for character creation
VALID_CLASSES = ["Warrior", "Mage", "Rogue"]


# ============================================================================
# CHARACTER CREATION
# ============================================================================

def create_character(name, char_class):
    """Creates a new character dictionary with default stats."""
    if char_class not in VALID_CLASSES:
        raise CharacterError("Invalid character class.")

    return {
        "name": name,
        "class": char_class,
        "level": 1,
        "experience": 0,
        "health": 100,
        "max_health": 100,
        "gold": 0
    }


# ============================================================================
# SAVE / LOAD SYSTEM
# ============================================================================

def save_character(character, save_directory="saves"):
    """Saves a character to a simple .txt file."""
    import os
    os.makedirs(save_directory, exist_ok=True)

    filename = f"{save_directory}/{character['name']}.txt"
    with open(filename, "w") as f:
        for key, value in character.items():
            f.write(f"{key}:{value}\n")

    return True


def load_character(name, save_directory="saves"):
    """Loads character data from a .txt file."""
    import os
    filename = f"{save_directory}/{name}.txt"

    if not os.path.exists(filename):
        raise CharacterError("Character does not exist.")

    data = {}
    with open(filename, "r") as f:
        for line in f:
            key, value = line.strip().split(":")

            # Convert numerical values back to int
            if key in ["level", "experience", "health", "max_health", "gold"]:
                value = int(value)

            data[key] = value

    return data


def delete_character(name, save_directory="saves"):
    """Deletes a character file."""
    import os
    filename = f"{save_directory}/{name}.txt"

    if not os.path.exists(filename):
        raise CharacterError("Character does not exist.")

    os.remove(filename)
    return True


def list_saved_characters(save_directory="saves"):
    """Returns a list of character names saved in the directory."""
    import os

    if not os.path.exists(save_directory):
        return []

    return [
        file[:-4]
        for file in os.listdir(save_directory)
        if file.endswith(".txt")
    ]


# ============================================================================
# CHARACTER ACTIONS
# ============================================================================

def gain_experience(character, amount):
    """Adds XP and handles level-ups automatically."""
    if character["health"] <= 0:
        raise CharacterDeadError("Character is dead.")

    character["experience"] += amount
    leveled = False

    # Leveling system: every level requires level * 100 XP
    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["health"] = character["max_health"]
        leveled = True

    return leveled


def add_gold(character, amount):
    """Adds gold to the character and returns new balance."""
    character["gold"] += amount
    return character["gold"]


def heal_character(character, amount):
    """Heals the character up to max health."""
    heal_amount = min(amount, character["max_health"] - character["health"])
    character["health"] += heal_amount
    return heal_amount


def is_character_dead(character):
    """Returns True if the character's health is 0 or lower."""
    return character["health"] <= 0


