# Main entry point for the game.
import time
import os # Import os for screen clearing
from core.player import Player
from core.game_io import save_game, initialize_player_from_load
from skills.woodcutting import Woodcutting, TREES
from skills.mining import Mining, ROCKS
from skills.fishing import Fishing, FISH_DATA # Assuming FISH_DATA exists in fishing.py
from skills.firemaking import Firemaking, LOG_FIRE_DATA # Assuming LOG_FIRE_DATA exists in firemaking.py

# Global game state
game_state = {
    "running": True,
    "last_update": time.time(),
    "player": Player(),
    "active_managers": {} # To store skill managers
}

def initialize_game():
    """Initializes the game state, player, skills, etc."""
    player = game_state["player"]

    initialize_player_from_load(player) # game_io now handles adding missing skills

    # Ensure core skills exist if not loaded or if it's a new game.
    # This is a fallback/secondary check; primary is in game_io.initialize_player_from_load
    # Merged default_skills
    default_skills = {
        "Woodcutting": {"level": 1, "xp": 0},
        "Mining": {"level": 1, "xp": 0},
        "Fishing": {"level": 1, "xp": 0},
        "Firemaking": {"level": 1, "xp": 0}
    }
    for skill_name, defaults in default_skills.items():
        if skill_name not in player.skills:
            player.skills[skill_name] = defaults.copy() # Use .copy() for dictionaries
            print(f"Initialized new {skill_name} skill.")
        else:
            # Verify loaded skill data integrity
            if "level" not in player.skills[skill_name]:
                player.skills[skill_name]["level"] = defaults["level"]
            if "xp" not in player.skills[skill_name]:
                player.skills[skill_name]["xp"] = defaults["xp"]

    # Setup skill managers
    game_state["active_managers"]["Woodcutting"] = Woodcutting(player)
    game_state["active_managers"]["Mining"] = Mining(player)
    game_state["active_managers"]["Fishing"] = Fishing(player) # Add Fishing manager
    game_state["active_managers"]["Firemaking"] = Firemaking(player) # Add Firemaking manager

    print("Game ready.")
    # Update available commands string if new commands are added for Fishing/Firemaking
    print("Try commands: 'wc <tree>', 'mine <rock>', 'fish <spot>', 'burn <log>', 'stop', 'save', 'load', 'exit'")


def process_input():
    """Handles player input (simplified)."""
    if not game_state["running"]:
        return
    try:
        pass
    except Exception as e:
        print(f"Error processing input: {e}")


def update_game_state():
    """Updates the game state."""
    current_time = time.time()
    delta_time = current_time - game_state["last_update"]
    game_state["last_update"] = current_time

    if game_state["player"].active_skill:
        skill_name = game_state["player"].active_skill
        if skill_name in game_state["active_managers"]:
            game_state["active_managers"][skill_name].update()


def render_ui():
    """Renders the game UI."""
    player = game_state["player"]

    # Basic clearing of the console
    # print("\033c", end="") # This might be too aggressive.
    # A simple way to create space without full clear:
    print("\n" * 2) # Print a few newlines

    print("="*30)
    print("      🌳 Idle OSRS Lite 🌳")
    print("="*30)

    print("\n--- Skills ---")
    for skill_name in player.skills.keys():
        level = player.get_skill_level(skill_name)
        xp = player.get_skill_xp(skill_name)
        xp_needed_for_next = player.xp_for_next_level(level) # Assuming xp_for_next_level is robust
        print(f"{skill_name}: Level {level} (XP: {xp}/{xp_needed_for_next})")

    print("\n--- Inventory ---")
    print(player.get_inventory_display())

    print("\n--- Activity ---")
    if player.active_skill:
        current_activity_details = "Unknown Action"
        manager = game_state["active_managers"].get(player.active_skill)
        if manager:
            # This part needs to be made more generic or expanded for new skills
            if player.active_skill == "Woodcutting":
                if hasattr(manager, 'is_cutting') and manager.is_cutting and manager.current_tree:
                    item_name = manager.current_tree
                    action_verb = "Chopping"
                    depleted_at = manager.tree_depleted_at
                    current_activity_details = f"{action_verb} {item_name}"
                    if time.time() < depleted_at:
                        respawn_in = depleted_at - time.time()
                        current_activity_details += f" (Depleted, respawns in {respawn_in:.1f}s)"
            elif player.active_skill == "Mining":
                if hasattr(manager, 'is_mining') and manager.is_mining and manager.current_rock:
                    item_name = manager.current_rock
                    action_verb = "Mining"
                    depleted_at = manager.rock_depleted_at
                    current_activity_details = f"{action_verb} {item_name}"
                    if time.time() < depleted_at:
                        respawn_in = depleted_at - time.time()
                        current_activity_details += f" (Depleted, respawns in {respawn_in:.1f}s)"
            elif player.active_skill == "Fishing":
                if hasattr(manager, 'is_fishing') and manager.is_fishing and hasattr(manager, 'current_spot_name') and manager.current_spot_name:
                    item_name = manager.current_spot_name
                    action_verb = "Fishing at"
                    current_activity_details = f"{action_verb} {item_name}"
                    # Could add more details like time until next catch attempt if desired
            elif player.active_skill == "Firemaking":
                 if hasattr(manager, 'is_burning') and manager.is_burning and hasattr(manager, 'current_log_id') and manager.current_log_id:
                    item_name = manager.current_log_id.replace('_', ' ').title() # Format for display
                    action_verb = "Burning"
                    current_activity_details = f"{action_verb} {item_name}"
                    if hasattr(manager, 'fire_ends_at') and manager.fire_ends_at > 0:
                        remaining_time = manager.fire_ends_at - time.time()
                        if remaining_time > 0:
                            current_activity_details += f" (ends in {remaining_time:.0f}s)"
                        else:
                            current_activity_details += " (ending)"


        print(f"Current: {player.active_skill} - {current_activity_details}")
    else:
        print("Current: Idle. Available commands: wc <tree>, mine <rock>, fish <spot>, burn <log>, stop, save, load, exit")

    print("="*30 + "\n")


def handle_command(command_str):
    """Handles text commands."""
    parts = command_str.lower().split()
    if not parts:
        return

    action = parts[0]
    player = game_state["player"]

    # Make managers easily accessible
    wc_manager = game_state["active_managers"].get("Woodcutting")
    mining_manager = game_state["active_managers"].get("Mining")
    fishing_manager = game_state["active_managers"].get("Fishing")
    firemaking_manager = game_state["active_managers"].get("Firemaking")


    def stop_all_actions():
        if player.active_skill:
            active_manager = game_state["active_managers"].get(player.active_skill)
            if active_manager:
                # Generic stop method if possible, or skill-specific
                if hasattr(active_manager, 'stop_action'): # Ideal generic method
                    active_manager.stop_action()
                elif hasattr(active_manager, 'stop_cutting'): # Woodcutting
                    active_manager.stop_cutting()
                elif hasattr(active_manager, 'stop_mining'): # Mining
                    active_manager.stop_mining()
                elif hasattr(active_manager, 'stop_fishing'): # Fishing
                    active_manager.stop_fishing()
                elif hasattr(active_manager, 'stop_burning'): # Firemaking
                    active_manager.stop_burning()
            player.clear_active_skill()
            # print("Stopped current action.") # Usually printed by manager's stop method

    if action == "wc" and wc_manager:
        if len(parts) > 1:
            tree_name_parts = [p.capitalize() for p in parts[1:]]
            tree_name = " ".join(tree_name_parts)
            if tree_name in TREES:
                stop_all_actions()
                wc_manager.start_cutting(tree_name)
            else:
                print(f"Unknown tree: '{tree_name}'. Available: {', '.join(TREES.keys())}")
        else:
            print("Usage: wc <tree name> (e.g., wc Normal Tree)")
    elif action == "mine" and mining_manager:
        if len(parts) > 1:
            rock_name_parts = [p.capitalize() for p in parts[1:]]
            rock_name = " ".join(rock_name_parts)
            if rock_name in ROCKS:
                stop_all_actions()
                mining_manager.start_mining(rock_name)
            else:
                print(f"Unknown rock: '{rock_name}'. Available: {', '.join(ROCKS.keys())}")
        else:
            print("Usage: mine <rock name> (e.g., mine Copper Ore)")
    elif action == "fish" and fishing_manager: # Add fish command
        if len(parts) > 1:
            spot_name_parts = [p.capitalize() for p in parts[1:]]
            spot_name = " ".join(spot_name_parts)
            if spot_name in FISH_DATA: # Assumes FISH_DATA is the dict of fishing spots
                stop_all_actions()
                fishing_manager.start_fishing(spot_name)
            else:
                print(f"Unknown fishing spot: '{spot_name}'. Available: {', '.join(FISH_DATA.keys())}")
        else:
            print("Usage: fish <spot name> (e.g., fish Shrimp Spot)")
    elif action == "burn" and firemaking_manager: # Add burn command
        if len(parts) > 1:
            log_name_parts = [p.capitalize() for p in parts[1:]] # Or parts[1] if log names are single words
            log_name = " ".join(log_name_parts) # e.g. "Normal Log"
            # We need to check if the log_name is valid (e.g. exists in LOG_FIRE_DATA or player inventory)
            # For simplicity, let's assume LOG_FIRE_DATA contains burnable logs
            if log_name.lower() in LOG_FIRE_DATA: # Check against defined burnable logs (e.g. "normal_log")
                stop_all_actions()
                firemaking_manager.start_burning(log_name.lower()) # Pass the ID-like key
            else:
                print(f"Cannot burn '{log_name}'. Available logs to burn: {', '.join(LOG_FIRE_DATA.keys())}")
        else:
            print("Usage: burn <log name> (e.g., burn Normal Log)")

    elif action == "stop":
        if player.active_skill:
            stop_all_actions()
        else:
            print("Not doing anything.")
    elif action == "save":
        save_game(player)
    elif action == "load":
        stop_all_actions()
        initialize_player_from_load(player)
        # Re-initialize all managers as player data might have changed
        game_state["active_managers"]["Woodcutting"] = Woodcutting(player)
        game_state["active_managers"]["Mining"] = Mining(player)
        game_state["active_managers"]["Fishing"] = Fishing(player)
        game_state["active_managers"]["Firemaking"] = Firemaking(player)
        print("Attempted to load game. Check messages for status.")

    elif action == "exit":
        stop_all_actions()
        save_choice = input("Save before exiting? (yes/no): ").lower()
        if save_choice == 'yes' or save_choice == 'y':
            save_game(game_state["player"])
        game_state["running"] = False
        print("Exiting game...")
    else:
        print(f"Unknown command: {action}. Available: wc, mine, fish, burn, stop, save, load, exit")


def game_loop(): # This function seems to be unused in the current main() structure.
    """The main game loop. (Potentially deprecated if main() handles loop directly)"""
    initialize_game()
    last_ui_render_time = 0

    while game_state["running"]:
        current_time = time.time()
        update_game_state()

        if current_time - last_ui_render_time >= 1.0:
            render_ui()
            last_ui_render_time = current_time

        # Input handling would be here if this loop was active.
        time.sleep(0.1)

def main():
    print("Welcome to Idle OSRS!")
    initialize_game()

    last_ui_render_time = time.time()
    last_logic_update_time = time.time()

    while game_state["running"]:
        current_time = time.time()

        if current_time - last_logic_update_time >= 0.1:
            update_game_state()
            last_logic_update_time = current_time

        if current_time - last_ui_render_time >= 1.0:
            render_ui()
            last_ui_render_time = current_time

            # Simplified input prompt mechanism
            player_is_idle = game_state["player"].active_skill is None
            prompt_ready = player_is_idle # Basic condition to prompt

            # More complex condition if we want to prompt when current action is "stuck" (e.g. tree depleted)
            # For example, for Woodcutting:
            active_wc_manager = game_state["active_managers"].get("Woodcutting")
            if active_wc_manager and game_state["player"].active_skill == "Woodcutting":
                 if hasattr(active_wc_manager, 'is_cutting') and active_wc_manager.is_cutting and \
                    hasattr(active_wc_manager, 'current_tree') and active_wc_manager.current_tree and \
                    hasattr(active_wc_manager, 'tree_depleted_at') and \
                    time.time() > active_wc_manager.tree_depleted_at:
                     prompt_ready = True


            if prompt_ready:
                try:
                    prompt_message = "Enter command: "
                    # Example of dynamic prompt message if desired
                    # if not player_is_idle and game_state["player"].active_skill == "Woodcutting" and prompt_ready:
                    #    prompt_message = f"Tree {active_wc_manager.current_tree} respawned. Enter command or will continue: "

                    command = input(prompt_message)
                    if command:
                         handle_command(command)
                except EOFError:
                    print("\nEOF received, exiting...")
                    game_state["running"] = False
                except KeyboardInterrupt:
                    print("\nExiting game (Ctrl+C)...")
                    game_state["running"] = False

        if not game_state["running"]:
            break

        time.sleep(0.05)

    print("Game has ended.")


if __name__ == "__main__":
    main()
