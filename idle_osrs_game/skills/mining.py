import time

# Define rock types and their properties
# Merged ROCKS dictionary, prioritizing feature branch's more extensive list
# and adjusting Iron Ore respawn time to align with feature branch.
ROCKS = {
    "Copper Ore":   {"level_req": 1,  "xp": 17.5, "ore_id": "copper_ore",   "respawn_time": 3},
    "Tin Ore":      {"level_req": 1,  "xp": 17.5, "ore_id": "tin_ore",      "respawn_time": 3},
    "Iron Ore":     {"level_req": 15, "xp": 35,   "ore_id": "iron_ore",     "respawn_time": 6}, # Adjusted from main's 7 to feature's 6
    "Coal Ore":     {"level_req": 30, "xp": 50,   "ore_id": "coal_ore",     "respawn_time": 10},
    "Gold Ore":     {"level_req": 40, "xp": 65,   "ore_id": "gold_ore",     "respawn_time": 15},
    "Mithril Ore":  {"level_req": 55, "xp": 80,   "ore_id": "mithril_ore",  "respawn_time": 25},
    # Adamantite Ore (Level 70) would be after this, can be added.
    # Runite Ore (Level 85) would be even later.
}

class Mining:
    def __init__(self, player):
        self.player = player
        self.is_mining = False
        self.current_rock = None
        self.rock_depleted_at = 0

    def start_mining(self, rock_name):
        if rock_name not in ROCKS:
            print(f"No such rock: {rock_name}. Available: {', '.join(ROCKS.keys())}")
            return

        rock_data = ROCKS[rock_name]
        if self.player.get_skill_level("Mining") < rock_data["level_req"]:
            print(f"You need level {rock_data['level_req']} Mining to mine {rock_name}.")
            return

        self.is_mining = True
        self.current_rock = rock_name
        self.player.set_active_skill("Mining")
        self.rock_depleted_at = 0 # Reset depletion timer for the new rock
        print(f"You start mining {rock_name}...")

    def stop_mining(self):
        if self.is_mining:
            self.is_mining = False
            # self.current_rock = None # Optional: clear current_rock, or leave for UI
            self.player.clear_active_skill()
            print("You stop mining.")

    def update(self):
        if not self.is_mining or not self.current_rock:
            return

        rock_data = ROCKS[self.current_rock]

        if time.time() < self.rock_depleted_at:
            return # Rock hasn't respawned yet

        # Simulate mining action
        self.player.add_xp("Mining", rock_data["xp"])
        self.player.add_item_to_inventory(rock_data["ore_id"], 1)
        # Player's add_item_to_inventory should handle the success message now

        self.rock_depleted_at = time.time() + rock_data["respawn_time"]
        print(f"The {self.current_rock} is depleted. It will respawn in {rock_data['respawn_time']} seconds.")

        # If continuous mining is desired, do nothing here to stop.
        # If stop after one ore:
        # self.stop_mining()
        # print(f"The {self.current_rock} has been depleted.")
