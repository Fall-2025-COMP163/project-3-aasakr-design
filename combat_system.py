"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles combat mechanics
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
    enemy_type = enemy_type.lower()

    enemies = {
        "goblin": {
            'name': 'Goblin',
            'health': 50,
            'max_health': 50,
            'strength': 8,
            'magic': 2,
            'xp_reward': 25,
            'gold_reward': 10
        },
        "orc": {
            'name': 'Orc',
            'health': 80,
            'max_health': 80,
            'strength': 12,
            'magic': 5,
            'xp_reward': 50,
            'gold_reward': 25
        },
        "dragon": {
            'name': 'Dragon',
            'health': 200,
            'max_health': 200,
            'strength': 25,
            'magic': 15,
            'xp_reward': 200,
            'gold_reward': 100
        }
    }

    if enemy_type not in enemies:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")

    return enemies[enemy_type].copy()


def get_random_enemy_for_level(character_level):
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn_counter = 1

    def start_battle(self):
        if self.character['health'] <= 0:
            raise CharacterDeadError("Character is dead.")

        while self.combat_active:
            # Player attacks first
            self.player_turn()
            result = self.check_battle_end()
            if result:
                return self._battle_result(result)

            # Enemy attacks second
            self.enemy_turn()
            result = self.check_battle_end()
            if result:
                return self._battle_result(result)

            self.turn_counter += 1

    def _battle_result(self, winner):
        if winner == "player":
            rewards = get_victory_rewards(self.enemy)
            return {
                'winner': 'player',
                'xp_gained': rewards['xp'],
                'gold_gained': rewards['gold']
            }
        else:
            return {
                'winner': 'enemy',
                'xp_gained': 0,
                'gold_gained': 0
            }

    def player_turn(self):
        if not self.combat_active:
            raise CombatNotActiveError()

        # Simple version (required by tests):
        damage = self.calculate_damage(self.character, self.enemy)
        self.apply_damage(self.enemy, damage)

    def enemy_turn(self):
        if not self.combat_active:
            raise CombatNotActiveError()

        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)

    def calculate_damage(self, attacker, defender):
        base = attacker.get('strength', 5)
        reduction = defender.get('strength', 5) // 4
        dmg = base - reduction
        return max(1, dmg)

    def apply_damage(self, target, damage):
        target['health'] -= damage
        if target['health'] < 0:
            target['health'] = 0

    def check_battle_end(self):
        if self.enemy['health'] <= 0:
            self.combat_active = False
            return "player"
        if self.character['health'] <= 0:
            self.combat_active = False
            return "enemy"
        return None

    def attempt_escape(self):
        if random.random() < 0.5:
            self.combat_active = False
            return True
        return False


# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """Simplified for assignment—no cooldown system needed"""
    cclass = character['class'].lower()

    if cclass == "warrior":
        return warrior_power_strike(character, enemy)
    elif cclass == "mage":
        return mage_fireball(character, enemy)
    elif cclass == "rogue":
        return rogue_critical_strike(character, enemy)
    elif cclass == "cleric":
        return cleric_heal(character)
    else:
        return "Unknown class ability."


def warrior_power_strike(character, enemy):
    dmg = character['strength'] * 2
    enemy['health'] -= dmg
    if enemy['health'] < 0:
        enemy['health'] = 0
    return f"Warrior Power Strike deals {dmg} damage!"


def mage_fireball(character, enemy):
    dmg = character['magic'] * 2
    enemy['health'] -= dmg
    if enemy['health'] < 0:
        enemy['health'] = 0
    return f"Mage Fireball deals {dmg} damage!"


def rogue_critical_strike(character, enemy):
    if random.random() < 0.5:
        dmg = character['strength'] * 3
    else:
        dmg = character['strength']

    enemy['health'] -= dmg
    if enemy['health'] < 0:
        enemy['health'] = 0

    return f"Rogue Critical Strike deals {dmg} damage!"


def cleric_heal(character):
    heal_amt = 30
    character['health'] += heal_amt
    if character['health'] > character['max_health']:
        character['health'] = character['max_health']
    return f"Cleric heals for {heal_amt} HP!"


# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    return character['health'] > 0


def get_victory_rewards(enemy):
    return {
        'xp': enemy.get('xp_reward', 0),
        'gold': enemy.get('gold_reward', 0)
    }


def display_combat_stats(character, enemy):
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")


def display_battle_log(message):
    print(f">>> {message}")


