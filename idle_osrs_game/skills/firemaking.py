import time

# LOG_FIRE_DATA: Maps log_id to its firemaking properties
# "level_req": Required Firemaking level to burn this log
# "xp": XP gained from burning this log
# "duration": How long the fire lasts in seconds
LOG_FIRE_DATA = {
    "normal_log": {"level_req": 1, "xp": 40, "duration": 30},
    "oak_log": {"level_req": 15, "xp": 60, "duration": 45},
    "willow_log": {"level_req": 30, "xp": 90, "duration": 60},
    "teak_log": {"level_req": 35, "xp": 105, "duration": 70},
    "maple_log": {"level_req": 45, "xp": 135, "duration": 90},
    "mahogany_log": {"level_req": 50, "xp": 157.5, "duration": 100},
    "yew_log": {"level_req": 60, "xp": 202.5, "duration": 120},
    # Add more logs like Magic, Redwood as needed
}

class Firemaking:
    def __init__(self, player):
        self.player = player
        self.is_burning = False  # True if currently tending to a fire (though FM is often one-off)
        self.current_log_id = None # The ID of the log currently burning
        self.fire_ends_at = 0    # Timestamp when the current fire will burn out

    def start_burning(self, log_id_param):
        log_id = log_id_param.lower().replace(" ", "_") # Normalize, e.g. "Normal Log" -> "normal_log"

        if self.is_burning:
            # For simplicity, one fire at a time by this manager.
            # Real OSRS allows multiple fires, but that's more complex for an idle game's active skill.
            print("You are already tending to a fire.")
            return

        if log_id not in LOG_FIRE_DATA:
            print(f"You can't burn '{log_id_param}'. Unknown log type.")
            return

        log_data = LOG_FIRE_DATA[log_id]

        if self.player.get_skill_level("Firemaking") < log_data["level_req"]:
            print(f"You need level {log_data['level_req']} Firemaking to burn {log_id.replace('_', ' ')}.")
            return

        # Attempt to remove one log from inventory
        if not self.player.remove_item_from_inventory(log_id, 1):
            print(f"You don't have any {log_id.replace('_', ' ')} to burn.")
            return

        # Successfully removed log, now start fire
        self.is_burning = True
        self.current_log_id = log_id
        self.fire_ends_at = time.time() + log_data["duration"]

        self.player.set_active_skill("Firemaking") # Set active skill
        self.player.add_xp("Firemaking", log_data["xp"]) # XP is granted upfront in OSRS

        print(f"You light the {self.current_log_id.replace('_', ' ')}. It will burn for {log_data['duration']} seconds.")
        # The active skill will be Firemaking, but the player might be free to do other things
        # while the fire burns. For an idle game, we might clear active_skill after starting
        # or let it be cleared by the update when fire ends. Let's clear it after starting.
        # However, the `main.py` structure assumes active_skill is set while something is "managed".
        # So, we'll leave active_skill as "Firemaking" and let update handle its lifecycle.


    def stop_burning(self):
        # This might be called if player manually changes action.
        # The fire itself will continue to burn until its time is up.
        if self.is_burning:
            print("You step away from the fire.") # Or no message needed
            # Don't clear is_burning or fire_ends_at here, as the fire itself is still going.
            # Only clear the player's *focus* on this skill if that's the desired mechanic.
            # For now, clearing active_skill is handled by main loop's stop_all_actions.
            pass


    def update(self):
        if not self.is_burning:
            return

        if time.time() >= self.fire_ends_at:
            print(f"The {self.current_log_id.replace('_', ' ')} fire has burned out.")
            self.is_burning = False
            self.current_log_id = None
            self.fire_ends_at = 0
            # If Firemaking was the active skill, clear it as the managed action is over.
            if self.player.active_skill == "Firemaking":
                self.player.clear_active_skill()
        else:
            # Fire is still burning. UI should reflect this.
            # No continuous XP or items from Firemaking in basic OSRS style.
            pass
