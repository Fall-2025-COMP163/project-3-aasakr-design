"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Implementation compatible with provided tests.

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles quest management, dependencies, and completion.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError,
)
import character_manager

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest.

    Requirements:
      - quest exists
      - character level >= required_level
      - prerequisite quest completed (if any)
      - quest not already completed
      - quest not already active

    Returns True if accepted.
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    quest = quest_data_dict[quest_id]
    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    # Level requirement
    level = character.get("level", 1)
    required_level = quest.get("required_level", 1)
    if level < required_level:
        raise InsufficientLevelError("Character level too low for this quest.")

    # Prerequisite requirement
    prereq = quest.get("prerequisite", "NONE")
    if prereq not in ("NONE", None, ""):
        if prereq not in character["completed_quests"]:
            raise QuestRequirementsNotMetError(
                f"Prerequisite quest '{prereq}' not completed."
            )

    # Already completed?
    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError("Quest already completed.")

    # Already active?
    if quest_id in character["active_quests"]:
        # For this project, just don't add again; no exception required by tests.
        return False

    character["active_quests"].append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards.

    Rewards:
      - experience: reward_xp
      - gold: reward_gold

    Returns dict with reward info.
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError("Quest is not currently active.")

    quest = quest_data_dict[quest_id]

    # Move from active to completed
    character["active_quests"].remove(quest_id)
    if quest_id not in character["completed_quests"]:
        character["completed_quests"].append(quest_id)

    # Grant rewards
    xp = int(quest.get("reward_xp", 0))
    gold = int(quest.get("reward_gold", 0))

    # Use character_manager helpers (tests rely on experience/gold changing)
    if xp > 0:
        character_manager.gain_experience(character, xp)
    if gold != 0:
        character_manager.add_gold(character, gold)

    return {"xp": xp, "gold": gold}


def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it.

    Returns True if abandoned.
    Raises QuestNotActiveError if quest not active.
    """
    character.setdefault("active_quests", [])
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError("Quest is not currently active.")
    character["active_quests"].remove(quest_id)
    return True


def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests.

    Returns list of quest dicts.
    """
    active_ids = character.get("active_quests", [])
    return [quest_data_dict[qid] for qid in active_ids if qid in quest_data_dict]


def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests.

    Returns list of quest dicts.
    """
    completed_ids = character.get("completed_quests", [])
    return [quest_data_dict[qid] for qid in completed_ids if qid in quest_data_dict]


def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept.

    Available if:
      - meets level requirement
      - prerequisite quest completed (if any)
      - not completed
      - not active
    """
    available = []
    for qid, quest in quest_data_dict.items():
        if not can_accept_quest(character, qid, quest_data_dict):
            continue
        available.append(quest)
    return available

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """Return True if quest_id is in character's completed_quests."""
    return quest_id in character.get("completed_quests", [])


def is_quest_active(character, quest_id):
    """Return True if quest_id is in character's active_quests."""
    return quest_id in character.get("active_quests", [])


def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest.

    Returns True/False only, does NOT raise exceptions.
    """
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]
    level = character.get("level", 1)
    required_level = quest.get("required_level", 1)
    if level < required_level:
        return False

    prereq = quest.get("prerequisite", "NONE")
    if prereq not in ("NONE", None, ""):
        if prereq not in character.get("completed_quests", []):
            return False

    if is_quest_completed(character, quest_id):
        return False

    if is_quest_active(character, quest_id):
        return False

    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get ordered list of quest IDs from earliest prerequisite to quest_id.

    Raises QuestNotFoundError if any quest in the chain doesn't exist.
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    chain = []
    current_id = quest_id
    while True:
        if current_id not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{current_id}' not found in chain.")
        chain.insert(0, current_id)
        prereq = quest_data_dict[current_id].get("prerequisite", "NONE")
        if prereq in ("NONE", None, ""):
            break
        current_id = prereq

    return chain

# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed.

    Returns float between 0 and 100.
    """
    total = len(quest_data_dict)
    if total == 0:
        return 0.0
    completed = len(character.get("completed_quests", []))
    return (completed / total) * 100.0


def get_total_quest_rewards_earned(character, quest_data_dict):
    """
    Calculate total XP and gold earned from completed quests.

    Returns dict with 'total_xp' and 'total_gold'.
    """
    total_xp = 0
    total_gold = 0
    for qid in character.get("completed_quests", []):
        quest = quest_data_dict.get(qid)
        if not quest:
            continue
        total_xp += int(quest.get("reward_xp", 0))
        total_gold += int(quest.get("reward_gold", 0))
    return {"total_xp": total_xp, "total_gold": total_gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests whose required_level is within [min_level, max_level].
    """
    results = []
    for quest in quest_data_dict.values():
        lvl = int(quest.get("required_level", 1))
        if min_level <= lvl <= max_level:
            results.append(quest)
    return results

# ============================================================================
# DISPLAY FUNCTIONS (for playing, not used by tests)
# ============================================================================

def display_quest_info(quest_data):
    """Display formatted quest information."""
    print(f"\n=== {quest_data.get('title', 'Unknown Quest')} ===")
    print(f"Description: {quest_data.get('description', '')}")
    print(f"Required Level: {quest_data.get('required_level', 1)}")
    print(f"Prerequisite: {quest_data.get('prerequisite', 'NONE')}")
    print(f"Rewards: {quest_data.get('reward_xp', 0)} XP, "
          f"{quest_data.get('reward_gold', 0)} gold")


def display_quest_list(quest_list):
    """Display a list of quests in summary format."""
    if not quest_list:
        print("No quests to show.")
        return
    for quest in quest_list:
        print(f"- {quest.get('title', 'Unknown')} "
              f"(Level {quest.get('required_level', 1)}) "
              f"[{quest.get('reward_xp', 0)} XP, {quest.get('reward_gold', 0)} gold]")


def display_character_quest_progress(character, quest_data_dict):
    """Display quest statistics and progress for the character."""
    active = len(character.get("active_quests", []))
    completed = len(character.get("completed_quests", []))
    pct = get_quest_completion_percentage(character, quest_data_dict)
    totals = get_total_quest_rewards_earned(character, quest_data_dict)

    print(f"Active quests: {active}")
    print(f"Completed quests: {completed}")
    print(f"Completion: {pct:.1f}%")
    print(f"Total rewards earned: {totals['total_xp']} XP, {totals['total_gold']} gold")

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites (not NONE) exist as quest IDs.

    Returns True if all valid.
    Raises QuestNotFoundError if an invalid prerequisite is found.
    """
    for qid, quest in quest_data_dict.items():
        prereq = quest.get("prerequisite", "NONE")
        if prereq not in ("NONE", None, "") and prereq not in quest_data_dict:
            raise QuestNotFoundError(
                f"Quest '{qid}' has invalid prerequisite '{prereq}'."
            )
    return True

# ============================================================================
# TESTING (manual)
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    test_char = {
        "level": 1,
        "active_quests": [],
        "completed_quests": [],
        "experience": 0,
        "gold": 0,
    }
    test_quests = {
        "first_quest": {
            "quest_id": "first_quest",
            "title": "First Steps",
            "description": "Complete your first quest",
            "reward_xp": 50,
            "reward_gold": 25,
            "required_level": 1,
            "prerequisite": "NONE",
        }
    }
    accept_quest(test_char, "first_quest", test_quests)
    print("Active quests:", test_char["active_quests"])



