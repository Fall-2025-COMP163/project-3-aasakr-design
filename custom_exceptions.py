"""
COMP 163 - Project 3: Quest Chronicles
Custom Exception Definitions

This module defines all custom exceptions used throughout the game.
"""

# ============================================================================
# BASE GAME EXCEPTIONS
# ============================================================================

# Base exception
class GameError(Exception):
    """Base exception for all game-related errors."""
    pass

# Character-related
class CharacterError(GameError):
    """Base for character-related issues."""
    pass

class CharacterDeadError(CharacterError):
    """Raised when character tries to act but is dead."""
    pass

# Combat-related
class CombatError(GameError):
    """Base for combat-related issues."""
    pass

class InvalidTargetError(CombatError):
    """Raised when the chosen combat target is invalid."""
    pass

class CombatNotActiveError(CombatError):
    """Raised when an action is attempted outside active combat."""
    pass

class AbilityOnCooldownError(CombatError):
    """Raised when a special ability is still cooling down."""
    pass

# Inventory-related
class InventoryError(GameError):
    """Base for inventory-related issues."""
    pass

# ============================================================================
# SPECIFIC EXCEPTIONS
# ============================================================================

# Data Loading Exceptions
class InvalidDataFormatError(DataError):
    """Raised when data file has incorrect format"""
    pass

class MissingDataFileError(DataError):
    """Raised when required data file is not found"""
    pass

class CorruptedDataError(DataError):
    """Raised when data file is corrupted or unreadable"""
    pass

# Character Exceptions
class InvalidCharacterClassError(CharacterError):
    """Raised when an invalid character class is specified"""
    pass

class CharacterNotFoundError(CharacterError):
    """Raised when trying to load a character that doesn't exist"""
    pass

class CharacterDeadError(CharacterError):
    """Raised when trying to perform actions with a dead character"""
    pass

class InsufficientLevelError(CharacterError):
    """Raised when character level is too low for an action"""
    pass

# Combat Exceptions
class InvalidTargetError(CombatError):
    """Raised when trying to target an invalid enemy"""
    pass

class CombatNotActiveError(CombatError):
    """Raised when trying to perform combat actions outside of battle"""
    pass

class AbilityOnCooldownError(CombatError):
    """Raised when trying to use an ability that's on cooldown"""
    pass

# Quest Exceptions
class QuestNotFoundError(QuestError):
    """Raised when trying to access a quest that doesn't exist"""
    pass

class QuestRequirementsNotMetError(QuestError):
    """Raised when trying to start a quest without meeting requirements"""
    pass

class QuestAlreadyCompletedError(QuestError):
    """Raised when trying to accept an already completed quest"""
    pass

class QuestNotActiveError(QuestError):
    """Raised when trying to complete a quest that isn't active"""
    pass

# Inventory Exceptions
class InventoryFullError(InventoryError):
    """Raised when trying to add items to a full inventory"""
    pass

class ItemNotFoundError(InventoryError):
    """Raised when trying to use an item that doesn't exist"""
    pass

class InsufficientResourcesError(InventoryError):
    """Raised when player doesn't have enough gold or items"""
    pass

class InvalidItemTypeError(InventoryError):
    """Raised when item type is not recognized"""
    pass

# Save/Load Exceptions
class SaveFileCorruptedError(GameError):
    """Raised when save file cannot be loaded due to corruption"""
    pass

class InvalidSaveDataError(GameError):
    """Raised when save file contains invalid data"""
    pass

