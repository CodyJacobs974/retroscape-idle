import time

# Define rock types and their properties
ROCKS = {
    "Copper Ore": {"level_req": 1, "xp": 17.5, "ore_id": "copper_ore", "respawn_time": 3},
    "Tin Ore": {"level_req": 1, "xp": 17.5, "ore_id": "tin_ore", "respawn_time": 3},
    "Iron Ore": {"level_req": 15, "xp": 35, "ore_id": "iron_ore", "respawn_time": 7},
    # Add more rocks later: Coal, Mithril, Adamantite, Runite etc.
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
        # Reset depletion timer for the new rock, in case player switches rocks
        self.rock_depleted_at = 0
        print(f"You start mining {rock_name}...")

    def stop_mining(self):
        if self.is_mining:
            self.is_mining = False
            # self.current_rock = None # Keep current_rock to show what was last mined until new action
            self.player.clear_active_skill()
            print("You stop mining.")

    def update(self):
        if not self.is_mining or not self.current_rock:
            return

        rock_data = ROCKS[self.current_rock]

        # Check if rock is depleted and needs to respawn
        if time.time() < self.rock_depleted_at:
            # Rock hasn't respawned yet, UI should ideally show this.
            return

        # Simulate mining action
        # print(f"You swing your pickaxe at the {self.current_rock}.") # Optional flavour text
        self.player.add_xp("Mining", rock_data["xp"])
        self.player.add_item_to_inventory(rock_data["ore_id"], 1) # Add 1 ore to inventory
        # Message updated in player.add_item_to_inventory
        # print(f"You get an {rock_data['ore_id']} and gain {rock_data['xp']} Mining XP.")

        # Rock gets depleted
        self.rock_depleted_at = time.time() + rock_data["respawn_time"]
        print(f"The {self.current_rock} is depleted. It will respawn in {rock_data['respawn_time']} seconds.")

        # If we want it to stop after one ore:
        # self.stop_mining()
        # print(f"The {self.current_rock} has been depleted.")
