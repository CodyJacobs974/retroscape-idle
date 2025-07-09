import time
import random

# Define fish types, their properties, and the "spot" they are caught at.
# For simplicity, spot name can be the primary fish type available there.
# XP values are loosely based on OSRS. Catch rates are simplified.
FISH_SPOTS = {
    "Net Small Fish":   {"level_req": 1,  "xp": 10, "fish_id": "raw_shrimps",   "respawn_time": 2, "alternate_fish_id": "raw_anchovies", "alternate_chance": 0.2}, # Shrimps, occasional Anchovies
    "Bait Fishing Spot":{"level_req": 5,  "xp": 20, "fish_id": "raw_sardine",   "respawn_time": 3, "alternate_fish_id": "raw_herring", "alternate_chance": 0.3}, # Sardines, occasional Herring (Lvl 10)
    "Fly Fishing Spot": {"level_req": 20, "xp": 50, "fish_id": "raw_trout",     "respawn_time": 4, "alternate_fish_id": "raw_salmon", "alternate_chance": 0.4}, # Trout (Lvl 20), occasional Salmon (Lvl 30)
    "Lobster Cage":     {"level_req": 40, "xp": 90, "fish_id": "raw_lobster",   "respawn_time": 7},
    "Harpoon Big Fish": {"level_req": 35, "xp": 80, "fish_id": "raw_tuna",      "respawn_time": 8, "alternate_fish_id": "raw_swordfish", "alternate_chance": 0.25} # Tuna (Lvl 35), occasional Swordfish (Lvl 50)
    # Monkfish (Lvl 62) would be next. For "up to 60", this is sufficient.
    # Let's adjust Harpoon spot to better reflect levels. Swordfish is a good target for up to L60.
    # Let's make a distinct spot for Swordfish for clarity.
}

# Re-evaluating structure slightly for clarity in commands:
# Player will type "fish <spot_name>"
# Example: "fish Net Small Fish" or "fish Lobster Cage"

FISH_DATA = {
    # Spot Name: {level_req, base_xp, fish: [{fish_id, xp (overrides base if needed), chance}, ...], "tool_needed"(optional)}
    "Netting Spot": {
        "level_req": 1, "base_xp": 10, "respawn_time": 2,
        "fish": [
            {"fish_id": "raw_shrimps", "level": 1, "xp": 10, "chance": 0.8},
            {"fish_id": "raw_anchovies", "level": 1, "xp": 15, "chance": 0.2} # Anchovies are better
        ]
    },
    "Baiting Spot": {
        "level_req": 5, "base_xp": 20, "respawn_time": 3,
        "fish": [
            {"fish_id": "raw_sardine", "level": 5, "xp": 20, "chance": 0.7},
            {"fish_id": "raw_herring", "level": 10, "xp": 30, "chance": 0.3}
        ]
    },
    "Fly Fishing River": {
        "level_req": 20, "base_xp": 50, "respawn_time": 4, # Lvl 20 for Trout
        "fish": [
            {"fish_id": "raw_trout", "level": 20, "xp": 50, "chance": 0.6},
            {"fish_id": "raw_salmon", "level": 30, "xp": 70, "chance": 0.4}
        ]
    },
    "Lobster Pot Spot": {
        "level_req": 40, "base_xp": 90, "respawn_time": 7, # Lvl 40 for Lobster
        "fish": [
            {"fish_id": "raw_lobster", "level": 40, "xp": 90, "chance": 1.0}
        ]
    },
    "Harpoon Spot": { # For Tuna & Swordfish
        "level_req": 35, "base_xp": 80, "respawn_time": 8, # Lvl 35 for Tuna
        "fish": [
            {"fish_id": "raw_tuna", "level": 35, "xp": 80, "chance": 0.7},
            {"fish_id": "raw_swordfish", "level": 50, "xp": 100, "chance": 0.3}
        ]
    }
    # Max level fish here is Swordfish at 50, suitable for training towards 60.
}


class Fishing:
    def __init__(self, player):
        self.player = player
        self.is_fishing = False
        self.current_spot_name = None
        self.spot_depleted_at = 0 # Represents when the next catch can occur

    def start_fishing(self, spot_name_input):
        # Find the spot key that matches input (case-insensitive partial match perhaps, or exact for now)
        found_spot_name = None
        for name in FISH_DATA.keys():
            if spot_name_input.lower() == name.lower():
                found_spot_name = name
                break

        if not found_spot_name:
            available_spots = [name for name, data in FISH_DATA.items() if self.player.get_skill_level("Fishing") >= data["level_req"]]
            if not available_spots:
                available_spots = list(FISH_DATA.keys()) # Show all if none are accessible yet
            print(f"No such fishing spot: '{spot_name_input}'. Available at your level: {', '.join(available_spots) or 'None yet'}. All spots: {', '.join(FISH_DATA.keys())}")
            return

        spot_data = FISH_DATA[found_spot_name]

        # Check overall spot level requirement
        if self.player.get_skill_level("Fishing") < spot_data["level_req"]:
            print(f"You need level {spot_data['level_req']} Fishing to fish at {found_spot_name}.")
            return

        # Check if player can catch any fish at this spot with their current level
        can_catch_anything = False
        for fish_info in spot_data["fish"]:
            if self.player.get_skill_level("Fishing") >= fish_info["level"]:
                can_catch_anything = True
                break
        if not can_catch_anything:
            min_level_for_spot = min(f["level"] for f in spot_data["fish"])
            print(f"You need a higher Fishing level for the fish at {found_spot_name}. Minimum level for any fish here is {min_level_for_spot}.")
            return

        self.is_fishing = True
        self.current_spot_name = found_spot_name
        self.player.set_active_skill("Fishing")
        self.spot_depleted_at = 0 # Allow immediate first attempt
        print(f"You start fishing at {found_spot_name}...")

    def stop_fishing(self):
        if self.is_fishing:
            self.is_fishing = False
            # self.current_spot_name = None # Keep for UI until new action
            self.player.clear_active_skill()
            print("You stop fishing.")

    def update(self):
        if not self.is_fishing or not self.current_spot_name:
            return

        if time.time() < self.spot_depleted_at:
            # Waiting for next catch attempt
            return

        spot_data = FISH_DATA[self.current_spot_name]

        # Determine what fish can be caught based on player level and chances
        possible_catches = []
        for fish_info in spot_data["fish"]:
            if self.player.get_skill_level("Fishing") >= fish_info["level"]:
                possible_catches.append(fish_info)

        if not possible_catches:
            # This should ideally be caught by start_fishing, but as a fallback:
            print(f"You don't have the required level to catch anything at {self.current_spot_name} currently.")
            self.stop_fishing()
            return

        # Weighted random choice from possible catches
        # This is a simple model; OSRS has more complex mechanics (e.g. tools, bait)
        # For now, sum of chances can exceed 1.0, we'll pick one based on relative weights.

        total_weight = sum(f['chance'] for f in possible_catches)
        rand_val = random.uniform(0, total_weight)
        cumulative_weight = 0
        caught_fish_info = None

        for fish_info in possible_catches:
            cumulative_weight += fish_info['chance']
            if rand_val <= cumulative_weight:
                caught_fish_info = fish_info
                break

        if not caught_fish_info: # Fallback if something went wrong with weighting or no possible catches
            # This might happen if all chances are 0, or only one fish with chance 0
            # For simplicity, pick the first possible one if logic fails (should not happen with current data)
            if possible_catches:
                 caught_fish_info = possible_catches[0]
            else: # Should be impossible to reach here due to earlier checks
                 print("No fish could be caught. Stopping.")
                 self.stop_fishing()
                 return


        # Simulate fishing action
        xp_to_add = caught_fish_info["xp"]
        fish_id_to_add = caught_fish_info["fish_id"]

        self.player.add_xp("Fishing", xp_to_add)
        self.player.add_item_to_inventory(fish_id_to_add, 1)
        # Item add message is handled by add_item_to_inventory
        # print(f"You catch a {fish_id_to_add.replace('_', ' ')} and gain {xp_to_add} Fishing XP.")

        # Set time for next possible catch
        self.spot_depleted_at = time.time() + spot_data["respawn_time"]
        # print(f"The fishing spot needs a moment. Next catch in {spot_data['respawn_time']}s.") # Optional flavour
        # The "depletion" here is more like a cooldown for the player's next catch attempt at this spot.
        # Unlike trees/rocks, the spot itself doesn't "disappear" in this simplified model.
        # A more complex model could have spots temporarily deplete or move.

        # For continuous fishing until stopped by player.
        # If we want it to stop after one fish (e.g. for some types of fishing), add self.stop_fishing() here.
        pass
