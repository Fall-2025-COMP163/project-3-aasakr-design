"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Test-focused implementation

Name: [Your Name Here]
AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

import random

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError,
)

# ---------------------------------------------------------------------------
# ENEMY DEFINITIONS
# ---------------------------------------------------------------------------

def create_enemy(enemy_type):
    """Create an enemy dict based on type, or raise InvalidTargetError."""
    t = str(enemy_type).lower()

    if t == "goblin":
        return {
            "name": "Goblin",
            "health": 50,
            "max_health": 50,
            "strength": 8,
            "magic": 2,
            "xp_reward": 25,
            "gold_reward": 10,
        }
    elif t == "orc":
        return {
            "name": "Orc",
            "health": 80,
            "max_health": 80,
            "strength": 12,
            "magic": 5,
            "xp_reward": 50,
            "gold_reward": 25,
        }
    elif t == "dragon":
        return {
            "name": "Dragon",
            "health": 200,
            "max_health": 200,
            "strength": 25,
            "magic": 15,
            "xp_reward": 200,
            "gold_reward": 100,
        }
    else:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")


def get_random_enemy_for_level(character_level):
    """Pick a suitable enemy type by character level."""
    lvl = int(character_level)
    if lvl <= 2:
        return create_enemy("goblin")
    elif 3 <= lvl <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")


# ---------------------------------------------------------------------------
# SIMPLE BATTLE
# ---------------------------------------------------------------------------

class SimpleBattle:
    """Simple turn-based battle between a character and an enemy."""

    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy

        # Ensure health/max_health keys exist
        self.character.setdefault("health", 0)
        self.character.setdefault("max_health", self.character["health"])
        self.enemy.setdefault("health", 0)
        self.enemy.setdefault("max_health", self.enemy["health"])

        self.combat_active = True
        self.turn_counter = 0

    def calculate_damage(self, attacker, defender):
        """Damage formula: attacker.strength - defender.strength // 4, min 1."""
        a = int(attacker.get("strength", 1))
        d = int(defender.get("strength", 0))
        dmg = a - (d // 4)
        return max(1, dmg)

    def apply_damage(self, target, damage):
        hp = int(target.get("health", 0)) - int(damage)
        if hp < 0:
            hp = 0
        target["health"] = hp

    def check_battle_end(self):
        """Return 'player', 'enemy', or None."""
        if self.enemy.get("health", 0) <= 0:
            self.combat_active = False
            return "player"
        if self.character.get("health", 0) <= 0:
            self.combat_active = False
            return "enemy"
        return None

    def start_battle(self):
        """Loop until someone dies; return winner & rewards."""
        if self.character.get("health", 0) <= 0:
            raise CharacterDeadError("Character is already dead")

        while self.combat_active:
            self.turn_counter += 1
            # Player turn
            self.player_turn()
            result = self.check_battle_end()
            if result:
                break
            # Enemy turn
            self.enemy_turn()
            result = self.check_battle_end()
            if result:
                break
            if self.turn_counter > 500:
                # just in case
                result = "enemy"
                self.combat_active = False
                break

        if result == "player":
            rewards = get_victory_rewards(self.enemy)
            return {
                "winner": "player",
                "xp_gained": rewards["xp"],
                "gold_gained": rewards["gold"],
            }
        else:
            return {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}

    def player_turn(self):
        """Basic attack from character to enemy. Raises if combat not active."""
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active")

        dmg = self.calculate_damage(self.character, self.enemy)
        self.apply_damage(self.enemy, dmg)

    def enemy_turn(self):
        """Basic attack from enemy to character. Raises if combat not active."""
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active")

        dmg = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, dmg)

    def attempt_escape(self):
        """50% chance to escape; deactivates combat on success."""
        success = random.random() < 0.5
        if success:
            self.combat_active = False
        return success


# ---------------------------------------------------------------------------
# SPECIAL ABILITIES (not needed by tests, but implemented)
# ---------------------------------------------------------------------------

def use_special_ability(character, enemy):
    """Use class-based ability. Not used by tests but provided for completeness."""
    cls = character.get("class", "").lower()
    if cls == "warrior":
        return warrior_power_strike(character, enemy)
    elif cls == "mage":
        return mage_fireball(character, enemy)
    elif cls == "rogue":
        return rogue_critical_strike(character, enemy)
    elif cls == "cleric":
        return cleric_heal(character)
    else:
        raise AbilityOnCooldownError("No special ability available")


def warrior_power_strike(character, enemy):
    dmg = character.get("strength", 1) * 2
    enemy["health"] = max(0, enemy.get("health", 0) - dmg)
    return dmg


def mage_fireball(character, enemy):
    dmg = character.get("magic", 1) * 2
    enemy["health"] = max(0, enemy.get("health", 0) - dmg)
    return dmg


def rogue_critical_strike(character, enemy):
    base = character.get("strength", 1)
    if random.random() < 0.5:
        dmg = base * 3
    else:
        dmg = base
    enemy["health"] = max(0, enemy.get("health", 0) - dmg)
    return dmg


def cleric_heal(character):
    heal_amount = 30
    new_hp = character.get("health", 0) + heal_amount
    if new_hp > character.get("max_health", 0):
        new_hp = character["max_health"]
    character["health"] = new_hp
    return heal_amount


# ---------------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------------

def can_character_fight(character):
    """True if the character has >0 health."""
    return character.get("health", 0) > 0


def get_victory_rewards(enemy):
    """Return xp/gold rewards from enemy dict."""
    return {
        "xp": int(enemy.get("xp_reward", 0)),
        "gold": int(enemy.get("gold_reward", 0)),
    }


def display_combat_stats(character, enemy):
    print(f"\n{character.get('name', 'Hero')}: HP={character.get('health', 0)}/{character.get('max_health', 0)}")
    print(f"{enemy.get('name', 'Enemy')}: HP={enemy.get('health', 0)}/{enemy.get('max_health', 0)}")


def display_battle_log(message):
    print(f">>> {message}")


