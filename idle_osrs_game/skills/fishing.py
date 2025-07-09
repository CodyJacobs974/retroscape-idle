import time
import random

# Define fishing spots, fish types, level requirements, XP, and tools.
# Tools can be simple strings for now. More complex item system could be added later.
FISH_DATA = {
    "Netting Spot": { # A common early fishing spot type
        "level_req": 1,
        "tool": "Small Fishing Net", # Example tool
        "xp_per_fish": 10,
        "fish": [
            {"id": "shrimp", "name": "Shrimp", "level_req": 1, "chance": 0.7},
            {"id": "anchovies", "name": "Anchovies", "level_req": 1, "chance": 0.3}
        ],
        "action_time": 5 # Time in seconds for one fishing attempt cycle
    },
    "Bait Spot": { # Another common fishing spot type
        "level_req": 5,
        "tool": "Fishing Rod",
        "bait": "Fishing Bait", # Example: requires bait
        "xp_per_fish": 20, # Average XP, could be fish-specific
        "fish": [
            {"id": "sardine", "name": "Sardine", "level_req": 5, "chance": 0.5},
            {"id": "herring", "name": "Herring", "level_req": 10, "chance": 0.5} # Player might catch this less if below level 10
        ],
        "action_time": 7
    },
    # Add more spots like "Lure Spot", "Cage Spot", "Harpoon Spot" later
}

class Fishing:
    def __init__(self, player):
        self.player = player
        self.is_fishing = False
        self.current_spot_name = None
        self.current_spot_data = None
        self.last_action_time = 0

    def start_fishing(self, spot_name):
        if spot_name not in FISH_DATA:
            print(f"Unknown fishing spot: {spot_name}. Available: {', '.join(FISH_DATA.keys())}")
            return

        spot_data = FISH_DATA[spot_name]
        if self.player.get_skill_level("Fishing") < spot_data["level_req"]:
            print(f"You need level {spot_data['level_req']} Fishing to fish at {spot_name}.")
            return

        # Basic tool check (assumes tools are just strings for now, not actual inventory items)
        # In a more complex system, self.player.inventory.has_item(spot_data["tool"]) would be used.
        if "tool" in spot_data:
            # For now, let's assume player has tools. A real check would be needed.
            print(f"You need a {spot_data['tool']} to fish here.") # This is more of a notice
            pass # Add actual tool check later if inventory supports it well

        if "bait" in spot_data:
            # Similar to tools, a real bait check from inventory would be needed.
            # if not self.player.inventory.has_item(spot_data["bait"], quantity_needed):
            # print(f"You need {spot_data['bait']} to fish here.")
            # return
            print(f"You'll need {spot_data['bait']}.") # Notice
            pass


        self.is_fishing = True
        self.current_spot_name = spot_name
        self.current_spot_data = spot_data
        self.player.set_active_skill("Fishing")
        self.last_action_time = time.time() # Start action timer immediately
        print(f"You start fishing at {self.current_spot_name}...")

    def stop_fishing(self):
        if self.is_fishing:
            self.is_fishing = False
            # self.current_spot_name = None # Optional to clear or keep for UI
            # self.current_spot_data = None
            self.player.clear_active_skill()
            print("You stop fishing.")

    def update(self):
        if not self.is_fishing or not self.current_spot_data:
            return

        current_time = time.time()
        action_time = self.current_spot_data["action_time"]

        if current_time - self.last_action_time >= action_time:
            self.last_action_time = current_time # Reset timer for next action

            # Determine which fish can be caught based on player's fishing level
            possible_fish_to_catch = []
            total_chance_weight = 0
            for fish_info in self.current_spot_data["fish"]:
                if self.player.get_skill_level("Fishing") >= fish_info["level_req"]:
                    possible_fish_to_catch.append(fish_info)
                    total_chance_weight += fish_info["chance"]

            if not possible_fish_to_catch:
                print("You don't have the required level to catch anything here.")
                # self.stop_fishing() # Optionally stop if nothing can be caught
                return

            # Randomly select a fish based on weighted chances
            rand_val = random.uniform(0, total_chance_weight)
            cumulative_chance = 0
            caught_fish_info = None

            for fish_info in possible_fish_to_catch:
                cumulative_chance += fish_info["chance"]
                if rand_val <= cumulative_chance:
                    caught_fish_info = fish_info
                    break

            if caught_fish_info:
                xp_gain = self.current_spot_data.get("xp_per_fish", 0) # Default XP or fish-specific
                if "xp" in caught_fish_info: # Allow fish-specific XP override
                    xp_gain = caught_fish_info["xp"]

                self.player.add_xp("Fishing", xp_gain)
                self.player.add_item_to_inventory(caught_fish_info["id"], 1)
                # The add_item_to_inventory method should ideally print the success message.
                # If not, uncomment below:
                # print(f"You catch a {caught_fish_info['name']} and gain {xp_gain} Fishing XP.")
            else:
                print("You fail to catch anything this time.")
                # Optionally, add a small amount of "failed attempt" XP
                # self.player.add_xp("Fishing", 1)
        else:
            # Not time for action yet, can add a "waiting" or "fishing..." message if desired,
            # but this might become spammy. UI should handle ongoing activity display.
            pass
