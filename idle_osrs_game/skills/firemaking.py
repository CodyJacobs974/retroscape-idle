# Data for burning logs: log_id maps to Firemaking level requirement and XP gained.
# XP values are based on OSRS Wiki.
LOG_FIRE_DATA = {
    "normal_log":   {"level_req": 1,  "xp": 40},
    "oak_log":      {"level_req": 15, "xp": 60},
    "willow_log":   {"level_req": 30, "xp": 90},
    "teak_log":     {"level_req": 35, "xp": 105},
    "maple_log":    {"level_req": 45, "xp": 135},
    "mahogany_log": {"level_req": 50, "xp": 157.5},
    "yew_log":      {"level_req": 60, "xp": 202.5},
    # Future: Magic logs (75), Redwood logs (90)
}

class Firemaking:
    def __init__(self, player):
        self.player = player

    def get_available_logs_to_burn(self):
        """Returns a list of log types the player has and can burn."""
        available = []
        for log_id, data in LOG_FIRE_DATA.items():
            if log_id in self.player.inventory and self.player.inventory[log_id] > 0:
                if self.player.get_skill_level("Firemaking") >= data["level_req"]:
                    available.append(log_id)
        return available

    def burn_log(self, log_id_input):
        """Attempts to burn a specified log type from the player's inventory."""

        # Normalize input log_id (e.g., "normal log" or "normal_log" -> "normal_log")
        normalized_log_id = log_id_input.lower().replace(" ", "_")
        if not normalized_log_id.endswith("_log"): # Ensure it's in "item_id" format
            normalized_log_id += "_log"


        if normalized_log_id not in LOG_FIRE_DATA:
            # Try to find a partial match if full name not used e.g. user types "oak" instead of "oak_log"
            matched_log_id = None
            for key in LOG_FIRE_DATA.keys():
                if normalized_log_id.split('_')[0] == key.split('_')[0]: # Compare "oak" with "oak"
                    matched_log_id = key
                    break
            if matched_log_id:
                normalized_log_id = matched_log_id
            else:
                print(f"Unknown log type: '{log_id_input}'. Cannot burn.")
                print(f"Known burnable log types: {', '.join([l.replace('_', ' ').title() for l in LOG_FIRE_DATA.keys()])}")
                return

        log_data = LOG_FIRE_DATA[normalized_log_id]

        # Check Firemaking level
        if self.player.get_skill_level("Firemaking") < log_data["level_req"]:
            print(f"You need level {log_data['level_req']} Firemaking to burn {normalized_log_id.replace('_', ' ').title()}.")
            return

        # Check if player has the log
        if not self.player.remove_item_from_inventory(normalized_log_id, 1):
            # remove_item_from_inventory already prints "Item not found or insufficient quantity."
            # So, we might not need an additional print here, or a more specific one.
            print(f"You don't have any {normalized_log_id.replace('_', ' ').title()} to burn.")
            return

        # Grant XP
        xp_gained = log_data["xp"]
        self.player.add_xp("Firemaking", xp_gained)
        # Player.add_item_to_inventory prints the item gain, Player.add_xp prints level ups.
        # We need a message for successful burn and XP gain here.
        log_display_name = normalized_log_id.replace('_', ' ').title()
        print(f"You burn the {log_display_name} and gain {xp_gained} Firemaking XP.")

        # Firemaking is typically a quick action, not a continuous one like gathering.
        # So, it doesn't set an active skill in the player state.
        # If we wanted a "bonfire" effect or something, this would change.
        pass
