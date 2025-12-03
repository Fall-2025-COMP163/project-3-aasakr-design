"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Test-focused implementation

Name: [Your Name Here]
AI Usage: [Document any AI assistance used]
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError,
)

import character_manager

# ---------------------------------------------------------------------------
# INTERNAL HELPER
# ---------------------------------------------------------------------------

def _get_quest(quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")
    return quest_data_dict[quest_id]


# ---------------------------------------------------------------------------
# QUEST MANAGEMENT
# ---------------------------------------------------------------------------

def accept_quest(character, quest_id, quest_data_dict):
    """Accept quest if requirements met; raise appropriate custom exceptions."""
    quest = _get_quest(quest_id, quest_data_dict)

    # Already completed?
    if quest_id in character.get("completed_quests", []):
        raise QuestAlreadyCompletedError("Quest already completed")

    # Already active?
    if quest_id in character.get("active_quests", []):
        raise QuestRequirementsNotMetError("Quest already active")

    # Level requirement
    if character.get("level", 1) < quest.get("required_level", 1):
        raise InsufficientLevelError("Character level too low for this quest")

    # Prerequisite
    prereq = quest.get("prerequisite", "NONE")
    if prereq and prereq.upper() != "NONE":
        if prereq not in character.get("completed_quests", []):
            raise QuestRequirementsNotMetError(
                f"Prerequisite quest '{prereq}' not completed"
            )

    character.setdefault("active_quests", []).append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """Complete an active quest, granting XP and gold.

    Raises QuestNotFoundError or QuestNotActiveError.
    """
    quest = _get_quest(quest_id, quest_data_dict)

    if quest_id not in character.get("active_quests", []):
        raise QuestNotActiveError("Quest is not active")

    # Remove from active, add to completed
    character["active_quests"].remove(quest_id)
    if quest_id not in character.get("completed_quests", []):
        character.setdefault("completed_quests", []).append(quest_id)

    xp = int(quest.get("reward_xp", 0))
    gold = int(quest.get("reward_gold", 0))

    # Apply rewards using character_manager helpers
    character_manager.gain_experience(character, xp)
    character_manager.add_gold(character, gold)

    return {"xp": xp, "gold": gold}


def abandon_quest(character, quest_id):
    """Remove quest from active_quests without completing.

    Raises QuestNotActiveError if it's not active.
    """
    if quest_id not in character.get("active_quests", []):
        raise QuestNotActiveError("Quest is not active")
    character["active_quests"].remove(quest_id)
    return True


def get_active_quests(character, quest_data_dict):
    """Return full data dicts of active quests."""
    active_ids = character.get("active_quests", [])
    return [quest_data_dict[qid] for qid in active_ids if qid in quest_data_dict]


def get_completed_quests(character, quest_data_dict):
    """Return full data dicts of completed quests."""
    done_ids = character.get("completed_quests", [])
    return [quest_data_dict[qid] for qid in done_ids if qid in quest_data_dict]


def get_available_quests(character, quest_data_dict):
    """Return quests that the character can currently accept."""
    available = []
    for qid in quest_data_dict:
        if can_accept_quest(character, qid, quest_data_dict):
            available.append(quest_data_dict[qid])
    return available


# ---------------------------------------------------------------------------
# QUEST TRACKING / UTILS
# ---------------------------------------------------------------------------

def is_quest_completed(character, quest_id):
    return quest_id in character.get("completed_quests", [])


def is_quest_active(character, quest_id):
    return quest_id in character.get("active_quests", [])


def can_accept_quest(character, quest_id, quest_data_dict):
    """Boolean version of accept_quest (no exceptions)."""
    if quest_id not in quest_data_dict:
        return False
    quest = quest_data_dict[quest_id]

    if quest_id in character.get("completed_quests", []):
        return False
    if quest_id in character.get("active_quests", []):
        return False

    if character.get("level", 1) < quest.get("required_level", 1):
        return False

    prereq = quest.get("prerequisite", "NONE")
    if prereq and prereq.upper() != "NONE":
        if prereq not in character.get("completed_quests", []):
            return False

    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """Return chain of prerequisites ending with quest_id."""
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")

    chain = []
    current = quest_id
    while True:
        if current not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{current}' not found in chain")
        quest = quest_data_dict[current]
        chain.insert(0, current)
        prereq = quest.get("prerequisite", "NONE")
        if not prereq or prereq.upper() == "NONE":
            break
        current = prereq
    return chain


def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    if total == 0:
        return 0.0
    completed = len(character.get("completed_quests", []))
    return (completed / total) * 100.0


def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = 0
    total_gold = 0
    for qid in character.get("completed_quests", []):
        quest = quest_data_dict.get(qid)
        if quest:
            total_xp += int(quest.get("reward_xp", 0))
            total_gold += int(quest.get("reward_gold", 0))
    return {"total_xp": total_xp, "total_gold": total_gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    result = []
    for quest in quest_data_dict.values():
        lvl = int(quest.get("required_level", 1))
        if min_level <= lvl <= max_level:
            result.append(quest)
    return result


# ---------------------------------------------------------------------------
# DISPLAY & VALIDATION (not directly tested, but harmless)
# ---------------------------------------------------------------------------

def display_quest_info(quest_data):
    print(f"\n=== {quest_data.get('title', 'Quest')} ===")
    print(f"Description: {quest_data.get('description', '')}")
    print(f"Required Level: {quest_data.get('required_level', 1)}")
    print(f"Rewards: {quest_data.get('reward_xp', 0)} XP, {quest_data.get('reward_gold', 0)} gold")
    print(f"Prerequisite: {quest_data.get('prerequisite', 'NONE')}")


def display_quest_list(quest_list):
    for q in quest_list:
        print(f"- {q.get('title', 'Quest')} (Lvl {q.get('required_level', 1)}) "
              f"XP: {q.get('reward_xp', 0)}, Gold: {q.get('reward_gold', 0)}")


def display_character_quest_progress(character, quest_data_dict):
    active = len(character.get("active_quests", []))
    completed = len(character.get("completed_quests", []))
    pct = get_quest_completion_percentage(character, quest_data_dict)
    totals = get_total_quest_rewards_earned(character, quest_data_dict)
    print(f"Active quests: {active}")
    print(f"Completed quests: {completed}")
    print(f"Completion: {pct:.1f}%")
    print(f"Total rewards: {totals['total_xp']} XP, {totals['total_gold']} gold")


def validate_quest_prerequisites(quest_data_dict):
    for qid, quest in quest_data_dict.items():
        prereq = quest.get("prerequisite", "NONE")
        if prereq and prereq.upper() != "NONE":
            if prereq not in quest_data_dict:
                raise QuestNotFoundError(
                    f"Quest '{qid}' has invalid prerequisite '{prereq}'"
                )
    return True


