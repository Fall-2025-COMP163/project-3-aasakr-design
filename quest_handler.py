"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module
"""

from custom_exceptions import (
    QuestError,
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

import character_manager


# ============================================================================
# INTERNAL HELPER
# ============================================================================

def _get_quest(quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")
    return quest_data_dict[quest_id]


# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    quest = _get_quest(quest_id, quest_data_dict)

    # Level check
    if character.get("level", 1) < quest.get("required_level", 1):
        raise InsufficientLevelError("Level too low for this quest.")

    # Prerequisite check
    prereq = quest.get("prerequisite", "NONE")
    if prereq and prereq.upper() != "NONE":
        if prereq not in character.get("completed_quests", []):
            raise QuestRequirementsNotMetError("Prerequisite quest not completed.")

    # Already completed
    if quest_id in character.get("completed_quests", []):
        raise QuestAlreadyCompletedError("Quest already completed.")

    # Already active
    if quest_id in character.get("active_quests", []):
        raise QuestRequirementsNotMetError("Quest already active.")

    character.setdefault("active_quests", []).append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    quest = _get_quest(quest_id, quest_data_dict)

    # Must be active
    if quest_id not in character.get("active_quests", []):
        raise QuestNotActiveError("Quest is not active.")

    # Move from active → completed
    character["active_quests"].remove(quest_id)
    character.setdefault("completed_quests", []).append(quest_id)

    # Rewards
    xp = int(quest.get("reward_xp", 0))
    gold = int(quest.get("reward_gold", 0))

    character_manager.gain_experience(character, xp)
    character_manager.add_gold(character, gold)

    return {"xp": xp, "gold": gold}


def abandon_quest(character, quest_id):
    if quest_id not in character.get("active_quests", []):
        raise QuestNotActiveError("Quest is not active.")
    character["active_quests"].remove(quest_id)
    return True


def get_active_quests(character, quest_data_dict):
    return [
        quest_data_dict[qid]
        for qid in character.get("active_quests", [])
        if qid in quest_data_dict
    ]


def get_completed_quests(character, quest_data_dict):
    return [
        quest_data_dict[qid]
        for qid in character.get("completed_quests", [])
        if qid in quest_data_dict
    ]


def get_available_quests(character, quest_data_dict):
    available = []
    for qid, quest in quest_data_dict.items():
        if can_accept_quest(character, qid, quest_data_dict):
            available.append(quest)
    return available


# ============================================================================
# TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    return quest_id in character.get("completed_quests", [])


def is_quest_active(character, quest_id):
    return quest_id in character.get("active_quests", [])


def can_accept_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]

    # Level
    if character.get("level", 1) < quest.get("required_level", 1):
        return False

    # Completed
    if quest_id in character.get("completed_quests", []):
        return False

    # Active
    if quest_id in character.get("active_quests", []):
        return False

    # Prerequisite
    prereq = quest.get("prerequisite", "NONE")
    if prereq and prereq.upper() != "NONE":
        if prereq not in character.get("completed_quests", []):
            return False

    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    chain = []
    current = quest_id

    while True:
        quest = quest_data_dict[current]
        chain.insert(0, current)

        prereq = quest.get("prerequisite", "NONE")
        if prereq.upper() == "NONE":
            break

        if prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite '{prereq}' not found.")

        current = prereq

    return chain


# ============================================================================
# STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    if total == 0:
        return 0.0
    completed = len(character.get("completed_quests", []))
    return (completed / total) * 100.0


def get_total_quest_rewards_earned(character, quest_data_dict):
    xp = 0
    gold = 0
    for qid in character.get("completed_quests", []):
        quest = quest_data_dict.get(qid)
        if quest:
            xp += int(quest.get("reward_xp", 0))
            gold += int(quest.get("reward_gold", 0))
    return {"total_xp": xp, "total_gold": gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    return [
        quest for quest in quest_data_dict.values()
        if min_level <= quest.get("required_level", 1) <= max_level
    ]


# ============================================================================
# PREREQUISITE VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    for qid, quest in quest_data_dict.items():
        prereq = quest.get("prerequisite", "NONE")
        if prereq.upper() != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(
                f"Quest '{qid}' has invalid prerequisite '{prereq}'."
            )
    return True

