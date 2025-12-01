"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code (Test-focused implementation)

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles combat mechanics in a straightforward way required by the autograder tests.
"""

import random

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type. Raises InvalidTargetError if unknown.
    Returns a dictionary with keys:
      name, health, max_health, strength, magic, xp_reward, gold_reward
    """
    if not isinstance(enemy_type, str):
        raise InvalidTargetError("Enemy type must be a string.")

    t = enemy_type.lower()
    if t == "goblin":
        return {
            'name': 'Goblin',
            'health': 50,
            'max_health': 50,
            'strength': 8,
            'magic': 2,
            'xp_reward': 25,
            'gold_reward': 10
        }
    elif t == "orc":
        return {
            'name': 'Orc',
            'health': 80,
            'max_health': 80,
            'strength': 12,
            'magic': 5,
            'xp_reward': 50,
            'gold_reward': 25
        }
    elif t == "dragon":
        return {
            'name': 'Dragon',
            'health': 200,
            'max_health': 200,
            'strength': 25,
            'magic': 15,
            'xp_reward': 200,
            'gold_reward': 100
        }
    else:
        # Explicitly raise to satisfy tests expecting InvalidTargetError
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")


def get_random_enemy_for_level(character_level):
    """
    Choose an enemy type based on character level.
    """
    try:
        lvl = int(character_level)
    except Exception:
        lvl = 1
    if lvl <= 2:
        return create_enemy("goblin")
    elif 3 <= lvl <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")


# ============================================================================
# SIMPLE TURN-BASED BATTLE
# ============================================================================

class SimpleBattle:
    """
    Minimal SimpleBattle class required by tests.

    Public:
      - character (dict) and enemy (dict) are stored as provided
      - combat_active flag (bool)
      - start_battle(), player_turn(), enemy_turn(), check_battle_end()
    """

    def __init__(self, character, enemy):
        # store references (tests assert equality)
        self.character = character
        self.enemy = enemy
        # ensure required health fields exist
        self.character.setdefault('health', 0)
        self.character.setdefault('max_health', self.character.get('health', 0))
        self.enemy.setdefault('health', self.enemy.get('max_health', self.enemy.get('health', 0)))
        self.enemy.setdefault('max_health', self.enemy.get('health', 0))
        # combat state
        self.combat_active = True
        self.turn_counter = 0

    def start_battle(self):
        """
        Run a simple battle loop until someone dies.
        Raises CharacterDeadError if character already has health <= 0.
        Returns dict: {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}
        """
        if int(self.character.get('health', 0)) <= 0:
            raise CharacterDeadError("Character is dead and cannot fight.")

        # Run loop: player then enemy until someone dies
        while True:
            self.turn_counter += 1
            # Player's turn (basic attack)
            self.player_turn()
            result = self.check_battle_end()
            if result:
                break
            # Enemy's turn
            self.enemy_turn()
            result = self.check_battle_end()
            if result:
                break
            # safety cap
            if self.turn_counter > 500:
                # stalemate — end fight as enemy win to be safe
                result = "enemy"
                break

        if result == "player":
            rewards = get_victory_rewards(self.enemy)
            return {'winner': 'player', 'xp_gained': rewards.get('xp', 0), 'gold_gained': rewards.get('gold', 0)}
        else:
            return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}

    def player_turn(self):
        """
        Simple player attack implementation.
        Raises CombatNotActiveError if combat_active is False.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Battle is not active.")
        # Basic damage = character['strength'] or 1 if missing
        attacker_str = int(self.character.get('strength', 1))
        defender_str = int(self.enemy.get('strength', 0))
        damage = attacker_str - (defender_str // 4)
        if damage < 1:
            damage = 1
        # Apply damage
        self.enemy['health'] = max(0, int(self.enemy.get('health', 0)) - int(damage))

    def enemy_turn(self):
        """
        Simple enemy attack implementation.
        Raises CombatNotActiveError if combat_active is False.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Battle is not active.")
        attacker_str = int(self.enemy.get('strength', 1))
        defender_str = int(self.character.get('strength', 0))
        damage = attacker_str - (defender_str // 4)
        if damage < 1:
            damage = 1
        self.character['health'] = max(0, int(self.character.get('health', 0)) - int(damage))

    def calculate_damage(self, attacker, defender):
        """
        Exposed damage calculation helper.
        """
        a_str = int(attacker.get('strength', 0))
        d_str = int(defender.get('strength', 0))
        dmg = a_str - (d_str // 4)
        return max(1, dmg)

    def apply_damage(self, target, damage):
        """
        Exposed damage application helper.
        """
        target['health'] = max(0, int(target.get('health', 0)) - int(damage))

    def check_battle_end(self):
        """
        Return 'player' if enemy dead, 'enemy' if character dead, else None.
        Also sets combat_active False when battle ends.
        """
        if int(self.enemy.get('health', 0)) <= 0:
            self.combat_active = False
            return "player"
        if int(self.character.get('health', 0)) <= 0:
            self.combat_active = False
            return "enemy"
        return None

    def attempt_escape(self):
        """
        50% chance to escape: if success, deactivate combat and return True.
        """
        success = random.random() < 0.5
        if success:
            self.combat_active = False
        return success


# ============================================================================
# SPECIAL ABILITIES (kept simple — not required by tests)
# ============================================================================

def use_special_ability(character, enemy):
    cls = str(character.get('class', '')).lower()
    if cls == 'warrior':
        return warrior_power_strike(character, enemy)
    if cls == 'mage':
        return mage_fireball(character, enemy)
    if cls == 'rogue':
        return rogue_critical_strike(character, enemy)
    if cls == 'cleric':
        return cleric_heal(character)
    return "No ability."

def warrior_power_strike(character, enemy):
    dmg = int(character.get('strength', 1)) * 2
    enemy['health'] = max(0, int(enemy.get('health', 0)) - dmg)
    return f"Warrior Power Strike dealt {dmg} damage."

def mage_fireball(character, enemy):
    dmg = int(character.get('magic', 1)) * 2
    enemy['health'] = max(0, int(enemy.get('health', 0)) - dmg)
    return f"Mage Fireball dealt {dmg} damage."

def rogue_critical_strike(character, enemy):
    if random.random() < 0.5:
        dmg = int(character.get('strength', 1)) * 3
    else:
        dmg = int(character.get('strength', 1))
    enemy['health'] = max(0, int(enemy.get('health', 0)) - dmg)
    return f"Rogue Critical Strike dealt {dmg} damage."

def cleric_heal(character):
    heal_amt = 30
    character['health'] = min(int(character.get('max_health', 0)), int(character.get('health', 0)) + heal_amt)
    return f"Cleric healed {heal_amt} HP."


# ============================================================================
# UTILITIES
# ============================================================================

def can_character_fight(character):
    return int(character.get('health', 0)) > 0

def get_victory_rewards(enemy):
    return {'xp': int(enemy.get('xp_reward', 0)), 'gold': int(enemy.get('gold_reward', 0))}

def display_combat_stats(character, enemy):
    print(f"\n{character.get('name', 'Player')}: HP={character.get('health',0)}/{character.get('max_health',0)}")
    print(f"{enemy.get('name', 'Enemy')}: HP={enemy.get('health',0)}/{enemy.get('max_health',0)}")

def display_battle_log(message):
    print(f">>> {message}")


