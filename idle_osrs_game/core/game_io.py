import json
import os
from .player import Player # Assuming Player class is in player.py

SAVE_FILE_DIR = "idle_osrs_game/data"
SAVE_FILE_PATH = os.path.join(SAVE_FILE_DIR, "savegame.json")

def ensure_save_dir_exists():
    """Ensures the save directory exists."""
    if not os.path.exists(SAVE_FILE_DIR):
        os.makedirs(SAVE_FILE_DIR)

def save_game(player):
    """Saves the player's game state to a file."""
    ensure_save_dir_exists()
    data_to_save = {
        "skills": player.skills,
        "inventory": player.inventory
    }
    try:
        with open(SAVE_FILE_PATH, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print("Game saved successfully!")
    except IOError as e:
        print(f"Error saving game: {e}")

def load_game(player_instance):
    """Loads the player's game state from a file.
    Modifies the provided player_instance directly.
    Returns True if load was successful, False otherwise.
    """
    if not os.path.exists(SAVE_FILE_PATH):
        print("No save file found. Starting a new game.")
        return False

    try:
        with open(SAVE_FILE_PATH, 'r') as f:
            loaded_data = json.load(f)

        player_instance.skills = loaded_data.get("skills", {})
        player_instance.inventory = loaded_data.get("inventory", {}) # Load inventory

        # Ensure default structure for skills if loading older save or partial data
        for skill_name, skill_data in player_instance.skills.items():
            if "level" not in skill_data: # Basic integrity check
                skill_data["level"] = 1
            if "xp" not in skill_data:
                skill_data["xp"] = 0

        print("Game loaded successfully!")
        return True
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading game: {e}. Starting a new game.")
        # Reset player to a default state if load fails
        player_instance.skills = {} # Or re-initialize as new
        # player_instance.inventory = []
        return False

def initialize_player_from_load(player):
    """Wrapper to load game data into an existing player object."""
    if not load_game(player): # load_game returns True on success, False on failure/no file
        # If load failed or no save file, ensure default skills and inventory are initialized
        player.inventory = {} # Ensure inventory is an empty dict for new game
        default_skills = {
            "Woodcutting": {"level": 1, "xp": 0},
            "Mining": {"level": 1, "xp": 0},
            "Fishing": {"level": 1, "xp": 0} # Add Fishing
        }
        for skill_name, defaults in default_skills.items():
            if skill_name not in player.skills:
                 player.skills[skill_name] = defaults.copy()
    else:
        # If load was successful, ensure all expected skills are present,
        # and inventory is correctly a dict.
        player_instance_dict = player.__dict__ # Helper for checking if inventory was loaded
        if "inventory" not in player_instance_dict or not isinstance(player_instance_dict["inventory"], dict):
            player.inventory = {} # Initialize if missing or wrong type

        default_skills = {
            "Woodcutting": {"level": 1, "xp": 0},
            "Mining": {"level": 1, "xp": 0},
            "Fishing": {"level": 1, "xp": 0} # Add Fishing
        }
        for skill_name, defaults in default_skills.items():
            if skill_name not in player.skills:
                print(f"Adding missing skill '{skill_name}' to loaded game profile.")
                player.skills[skill_name] = defaults.copy()
            else: # Skill exists, verify its structure
                if "level" not in player.skills[skill_name]:
                    player.skills[skill_name]["level"] = defaults["level"]
                if "xp" not in player.skills[skill_name]:
                    player.skills[skill_name]["xp"] = defaults["xp"]

    # Ensure inventory is initialized if somehow missed (e.g. very old save)
    if not hasattr(player, 'inventory') or player.inventory is None:
        player.inventory = {}


    # Recalculate levels based on XP if necessary, or ensure consistency.
    # For now, our add_xp handles leveling up, but on load, we might need to verify.
    # This is more for complex games where level isn't purely derived from XP at runtime.
    # For this game, direct load of level and XP is fine.
    pass
