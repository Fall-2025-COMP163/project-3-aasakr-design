"""
COMP 163 - Project 3: Quest Chronicles
Custom Exception Definitions
"""

# ============================================================================
# BASE GAME EXCEPTIONS
# ============================================================================

class GameError(Exception):
    """Base exception for all game-related errors"""
    pass

class DataError(GameError):
    """Base exception for data-related errors"""
    pass

class CharacterError(GameError):
    """Base exception for character-related errors"""
    pass

class CombatError(GameError):
    """Base exception for combat-related errors"""
    pass

class QuestError(GameError):
    """Base exception for quest-related errors"""
    pass

class InventoryError(GameError):
    """Base exception for inventory-related errors"""
    pass

# ============================================================================
# DATA EXCEPTIONS
# ============================================================================

class InvalidDataFormatError(DataError):
    """Raised when data file has incorrect format"""
    pass

class MissingDataFileError(DataError):
    """Raised when required data file is not found"""
    pass

class CorruptedDataError(DataError):
    """Raised when data file is corrupted or unreadable"""
    pass

# ============================================================================
# CHARACTER EXCEPTIONS
# ============================================================================

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

# ============================================================================
# COMBAT EXCEPTIONS
# ============================================================================

class InvalidTargetError(CombatError):
    """Raised when trying to target an invalid enemy"""
    pass

class CombatNotActiveError(CombatError):
    """Raised when trying to perform combat actions outside of battle"""
    pass

class AbilityOnCooldownError(CombatError):
    """Raised when trying to use an ability that's on cooldown"""
    pass

# ============================================================================
# QUEST EXCEPTIONS
# ============================================================================

class QuestNotFoundError(QuestError):
    """Raised when trying to access a quest that doesn't exist"""
    pass

class QuestRequirementsNotMetError(QuestError):
    """Raised when prerequisites are not met"""
    pass

class QuestAlreadyCompletedError(QuestError):
    """Raised when trying to accept an already completed quest"""
    pass

class QuestNotActiveError(QuestError):
    """Raised when trying to complete a quest that isn't active"""
    pass

# ============================================================================
# INVENTORY EXCEPTIONS
# ============================================================================

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
    """Raised when an item type is not recognized"""
    pass

# ============================================================================
# SAVE/LOAD EXCEPTIONS
# ============================================================================

class SaveFileCorruptedError(GameError):
    """Raised when save file is corrupted"""
    pass

class InvalidSaveDataError(GameError):
    """Raised when save file contains invalid data"""
    pass


