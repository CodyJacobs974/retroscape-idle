# Main entry point for the game.
import time
from core.player import Player
from core.game_io import save_game, initialize_player_from_load
from skills.woodcutting import Woodcutting, TREES
from skills.mining import Mining, ROCKS
from skills.fishing import Fishing, FISH_DATA # Import Fishing skill

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

    initialize_player_from_load(player) # game_io now handles adding missing skills including Fishing

    # Ensure core skills exist if not loaded or if it's a new game.
    # This is a fallback/secondary check; primary is in game_io.initialize_player_from_load
    default_skills = {
        "Woodcutting": {"level": 1, "xp": 0},
        "Mining": {"level": 1, "xp": 0},
        "Fishing": {"level": 1, "xp": 0}
    }
    for skill_name, defaults in default_skills.items():
        if skill_name not in player.skills:
            player.skills[skill_name] = defaults.copy() # Use .copy()
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

    print("Game ready.")
    print("More trees, rocks, and fishing spots are available as you level up!")
    print("Base commands: 'wc <tree name>', 'mine <rock name>', 'fish <spot name>', 'stop', 'save', 'load', 'exit'")


def process_input():
    """Handles player input (simplified)."""
    # In a real game, this would come from a proper input handler.
    # For now, we can simulate or use a very basic command prompt.
    # This function will be called less frequently or driven by actual input.
    if not game_state["running"]: # Don't process input if game is stopping
        return

    try:
        # Non-blocking input check can be complex.
        # For this iteration, let's assume input is checked outside the main tight loop,
        # or we explicitly call for it.
        # For testing, we can hardcode actions or use a simpler input mechanism.
        pass # We'll add a simple command handler later.
    except Exception as e:
        print(f"Error processing input: {e}")


def update_game_state():
    """Updates the game state."""
    current_time = time.time()
    delta_time = current_time - game_state["last_update"]
    game_state["last_update"] = current_time

    # Update active skills
    if game_state["player"].active_skill:
        skill_name = game_state["player"].active_skill
        if skill_name in game_state["active_managers"]:
            game_state["active_managers"][skill_name].update()
    # else:
        # print(f"Game updated. Delta time: {delta_time:.2f}s. No active skill.")


def render_ui():
    """Renders the game UI."""
    player = game_state["player"]
    wc_level = player.get_skill_level("Woodcutting")
    wc_xp = player.get_skill_xp("Woodcutting")
    xp_needed = player.xp_for_next_level(wc_level)

    # Basic clearing of the console for a cleaner look (works on most systems)
    # For more sophisticated UIs, a library like 'curses' would be needed.
    # print("\033c", end="") # Clears console - might be too aggressive for some terminals/OS

    print("\n" + "="*30)
    print("      🌳 Idle OSRS Lite 🌳")
    print("="*30)

    # Player Skills
    print("\n--- Skills ---")
    for skill_name in player.skills.keys(): # Iterate through all available skills
        level = player.get_skill_level(skill_name)
        xp = player.get_skill_xp(skill_name)
        xp_needed_for_next = player.xp_for_next_level(level)
        print(f"{skill_name}: Level {level} (XP: {xp}/{xp_needed_for_next})")

    # Inventory Display
    print("\n--- Inventory ---")
    print(player.get_inventory_display())

    # Current Activity
    print("\n--- Activity ---")
    if player.active_skill:
        current_activity_details = "Unknown Action"
        manager = game_state["active_managers"].get(player.active_skill)
        if manager:
            if player.active_skill == "Woodcutting":
                if manager.is_cutting and manager.current_tree:
                    item_name = manager.current_tree
                    action_verb = "Chopping"
                    depleted_at = manager.tree_depleted_at
                    current_activity_details = f"{action_verb} {item_name}"
                    if time.time() < depleted_at:
                        respawn_in = depleted_at - time.time()
                        current_activity_details += f" (Depleted, respawns in {respawn_in:.1f}s)"
            elif player.active_skill == "Mining":
                if manager.is_mining and manager.current_rock:
                    item_name = manager.current_rock
                    action_verb = "Mining"
                    depleted_at = manager.rock_depleted_at # Depletion for rocks
                    current_activity_details = f"{action_verb} {item_name}"
                    if time.time() < depleted_at:
                        respawn_in = depleted_at - time.time()
                        current_activity_details += f" (Depleted, respawns in {respawn_in:.1f}s)"
            elif player.active_skill == "Fishing":
                if manager.is_fishing and manager.current_spot_name:
                    item_name = manager.current_spot_name
                    action_verb = "Fishing at"
                    # Fishing spots don't "deplete" in the same way, more of a catch cooldown
                    cooldown_end = manager.spot_depleted_at
                    current_activity_details = f"{action_verb} {item_name}"
                    if time.time() < cooldown_end:
                        catch_in = cooldown_end - time.time()
                        current_activity_details += f" (Next catch in {catch_in:.1f}s)"

        print(f"Current: {player.active_skill} - {current_activity_details}")
    else:
        print("Current: Idle. Available commands: wc <tree name>, mine <rock name>, fish <spot name>, 'stop', 'save', 'load', 'exit")

    print("="*30 + "\n")


def handle_command(command_str):
    """Handles text commands."""
    parts = command_str.lower().split()
    if not parts:
        return

    action = parts[0]
    player = game_state["player"]
    wc_manager = game_state["active_managers"]["Woodcutting"]
    mining_manager = game_state["active_managers"]["Mining"]
    fishing_manager = game_state["active_managers"]["Fishing"] # Get fishing manager

    # Helper to stop any active skill
    def stop_all_actions():
        if player.active_skill:
            active_manager = game_state["active_managers"].get(player.active_skill)
            if active_manager:
                if hasattr(active_manager, 'stop_cutting'):
                    active_manager.stop_cutting()
                elif hasattr(active_manager, 'stop_mining'):
                    active_manager.stop_mining()
                elif hasattr(active_manager, 'stop_fishing'): # Add fishing
                    active_manager.stop_fishing()
            # player.clear_active_skill() # This is now handled by individual stop methods.
            # It's good to ensure it's cleared if a manager lacks a stop method,
            # but our current ones should handle it.

    if action == "wc":
        if len(parts) > 1:
            # Join all parts after 'wc' then capitalize, to handle multi-word tree names
            name_input = " ".join(parts[1:])
            # The TREES keys are already capitalized properly, so direct comparison after input capitalization
            # For more robust matching, could iterate keys and compare lowercased.
            # For now, assume user types it reasonably close, or we make FISH_DATA keys also well-capitalized.
            # The current fishing.py start_fishing has a loop to find match, which is better.
            # Let's refine woodcutting and mining to use similar flexible name matching.

            # For now, simple capitalization of input:
            capitalized_name_input = " ".join([p.capitalize() for p in name_input.split()])

            if capitalized_name_input in TREES:
                stop_all_actions()
                wc_manager.start_cutting(capitalized_name_input)
            else:
                print(f"Unknown tree: '{capitalized_name_input}'. Available: {', '.join(TREES.keys())}")
        else:
            print("Usage: wc <tree name> (e.g., wc Normal Tree)")
    elif action == "mine":
        if len(parts) > 1:
            name_input = " ".join(parts[1:])
            capitalized_name_input = " ".join([p.capitalize() for p in name_input.split()])
            if capitalized_name_input in ROCKS:
                stop_all_actions()
                mining_manager.start_mining(capitalized_name_input)
            else:
                print(f"Unknown rock: '{capitalized_name_input}'. Available: {', '.join(ROCKS.keys())}")
        else:
            print("Usage: mine <rock name> (e.g., mine Copper Ore)")
    elif action == "fish": # New command for fishing
        if len(parts) > 1:
            spot_name_input = " ".join(parts[1:])
            # Fishing manager's start_fishing handles finding the spot name from FISH_DATA keys
            # (it iterates and compares lowercased versions)
            stop_all_actions()
            fishing_manager.start_fishing(spot_name_input) # Pass the raw input
        else:
            print("Usage: fish <spot name> (e.g., fish Netting Spot)")
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
        game_state["active_managers"]["Woodcutting"] = Woodcutting(player)
        game_state["active_managers"]["Mining"] = Mining(player)
        game_state["active_managers"]["Fishing"] = Fishing(player) # Re-initialize fishing manager
        print("Attempted to load game. Check messages for status.")

    elif action == "exit":
        stop_all_actions()
        # Ask to save before exiting
        save_choice = input("Save before exiting? (yes/no): ").lower()
        if save_choice == 'yes' or save_choice == 'y':
            save_game(game_state["player"])
        game_state["running"] = False
        print("Exiting game...")
    else:
        print(f"Unknown command: {action}. Available: wc, stop, save, load, exit")


def game_loop():
    """The main game loop."""
    initialize_game()
    last_ui_render_time = 0

    while game_state["running"]:
        current_time = time.time()

        # Process input (e.g., from a separate thread or non-blocking input)
        # For now, we'll simulate by asking for input periodically or on demand
        # This part is tricky for a simple single-threaded console app.
        # A better approach would be a dedicated input thread or using libraries like `select` or `asyncio`.
        # For this iteration, let's use a simple input prompt within the loop, but less frequently.

        update_game_state() # Update game logic (e.g., skill actions)

        if current_time - last_ui_render_time >= 1.0: # Render UI every 1 second
            render_ui()
            last_ui_render_time = current_time

        # Simulate getting a command periodically to avoid blocking the game loop too much
        # In a real idle game, input might be checked less often or via a UI event
        if current_time - game_state.get("last_input_check", 0) > 2: # Check for input every 2s
            try:
                # This is a blocking call, which is not ideal for an idle game's main loop.
                # For a console version, this might be acceptable for simplicity.
                # Consider `inputimeout` library for non-blocking input in console.
                # For now, let's make it very infrequent or triggered differently.
                # Or, we can run the game for a few iterations then ask for input.
                # Let's try a simple prompt that blocks but the game logic still "ticks" based on real time.
                # The `update_game_state` uses `delta_time`, so even if input blocks,
                # the next update will process the accumulated time.
                pass # We will call handle_command from main try-except block for now
            except Exception as e:
                print(f"Input error: {e}") # Should not happen with basic input
            game_state["last_input_check"] = current_time


        time.sleep(0.1) # Loop tick rate - affects responsiveness of skill updates.
                        # Skill actions themselves (like getting a log) might have their own internal timers.

def main():
    print("Welcome to Idle OSRS!")
    game_loop_running = True

    # Initialize outside the loop that handles commands if game_loop handles its own start
    # initialize_game() # Moved into game_loop

    # Command processing loop
    # The actual game logic (ticks, skill updates) will happen in game_loop's update_game_state
    # This outer loop is just for user commands.

    # Start the game loop in a conceptual way.
    # The `game_loop` function now contains the primary loop.
    # We need a way to feed commands into it.

    # Let's adjust: main will primarily handle commands and the game_loop will run.
    # This means game_loop needs to be non-blocking for input, or input handled separately.

    # Simpler model for now: game_loop runs, and we periodically allow input.
    initialize_game() # Initialize once

    last_ui_render_time = time.time()
    last_logic_update_time = time.time()

    while game_state["running"]:
        current_time = time.time()

        # Handle input if available (non-blocking ideally)
        # For this console version, we'll use a blocking input but control its frequency.
        # A better way for console might be a separate input thread.

        # Let's run game updates frequently
        if current_time - last_logic_update_time >= 0.1: # Update logic 10 times a second
            update_game_state()
            last_logic_update_time = current_time

        # Render UI less frequently
        if current_time - last_ui_render_time >= 1.0:
            render_ui()
            last_ui_render_time = current_time

            # Ask for command after rendering UI
            try:
                # This is blocking. The game won't "tick" during this input.
                # This is a simplification for now.
                # `update_game_state` uses delta_time, so it will catch up.

                # Only prompt for input if the player is idle or the current tree has respawned
                # and the player is still notionally cutting it (i.e. hasn't typed 'stop').
                wc_manager = game_state["active_managers"]["Woodcutting"]
                player_is_idle = game_state["player"].active_skill is None
                tree_is_ready_for_input = False
                if wc_manager.is_cutting and wc_manager.current_tree:
                    # Check if tree is depleted and ready for next action (or input)
                    if time.time() > wc_manager.tree_depleted_at:
                         tree_is_ready_for_input = True # Tree has respawned, player might want to change action

                if player_is_idle or tree_is_ready_for_input :
                    prompt_message = "Enter command (wc, mine, fish, stop, save, load, exit): "
                    if not player_is_idle :
                        active_item_name = ""
                        current_skill_manager = game_state["active_managers"].get(player.active_skill)
                        if player.active_skill == "Woodcutting" and current_skill_manager and current_skill_manager.current_tree:
                            active_item_name = current_skill_manager.current_tree
                        elif player.active_skill == "Mining" and current_skill_manager and current_skill_manager.current_rock:
                            active_item_name = current_skill_manager.current_rock
                        elif player.active_skill == "Fishing" and current_skill_manager and current_skill_manager.current_spot_name:
                             active_item_name = current_skill_manager.current_spot_name # This is a spot, not an item

                        if active_item_name:
                             # For fishing, "respawned" isn't quite right, "ready" or "next catch ready" is better.
                             action_specific_message = "respawned"
                             if player.active_skill == "Fishing":
                                 action_specific_message = "ready for next catch"
                             prompt_message = f"{active_item_name} {action_specific_message}. Enter command or will continue: "

                    command = input(prompt_message)
                    if command:
                         handle_command(command)
                    # If no command, and they were cutting a respawned tree, it will just continue on next update.




            except EOFError: # Handle Ctrl+D or redirected input ending
                print("\nEOF received, exiting...")
                game_state["running"] = False
            except KeyboardInterrupt:
                print("\nExiting game (Ctrl+C)...")
                game_state["running"] = False

        if not game_state["running"]:
            break

        time.sleep(0.05) # Main loop polling frequency


    print("Game has ended.")


if __name__ == "__main__":
    main()
