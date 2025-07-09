import time

# Define tree types and their properties
# Merged TREES dictionary, prioritizing feature branch's more extensive list
# and adjusting Oak Tree respawn time to align with feature branch.
TREES = {
    "Normal Tree":  {"level_req": 1,  "xp": 25,    "log_id": "normal_log",   "respawn_time": 5},
    "Oak Tree":     {"level_req": 15, "xp": 37.5,  "log_id": "oak_log",      "respawn_time": 8}, # Adjusted from main's 10 to feature's 8
    "Willow Tree":  {"level_req": 30, "xp": 67.5,  "log_id": "willow_log",   "respawn_time": 12},
    "Teak Tree":    {"level_req": 35, "xp": 85,    "log_id": "teak_log",     "respawn_time": 15},
    "Maple Tree":   {"level_req": 45, "xp": 100,   "log_id": "maple_log",    "respawn_time": 20},
    "Mahogany Tree":{"level_req": 50, "xp": 125,   "log_id": "mahogany_log", "respawn_time": 25},
    "Yew Tree":     {"level_req": 60, "xp": 175,   "log_id": "yew_log",      "respawn_time": 30},
}

class Woodcutting:
    def __init__(self, player):
        self.player = player
        self.is_cutting = False
        self.current_tree = None
        self.tree_depleted_at = 0

    def start_cutting(self, tree_name):
        if tree_name not in TREES:
            print(f"No such tree: {tree_name}. Available: {', '.join(TREES.keys())}")
            return

        tree_data = TREES[tree_name]
        if self.player.get_skill_level("Woodcutting") < tree_data["level_req"]:
            print(f"You need level {tree_data['level_req']} Woodcutting to cut {tree_name}.")
            return

        self.is_cutting = True
        self.current_tree = tree_name
        self.player.set_active_skill("Woodcutting")
        self.tree_depleted_at = 0 # Reset depletion timer for the new tree
        print(f"You start cutting {tree_name}...")

    def stop_cutting(self):
        if self.is_cutting:
            self.is_cutting = False
            # self.current_tree = None # Optional: clear current_tree, or leave for UI
            self.player.clear_active_skill()
            print("You stop cutting.")

    def update(self):
        if not self.is_cutting or not self.current_tree:
            return

        tree_data = TREES[self.current_tree]

        if time.time() < self.tree_depleted_at:
            return # Tree hasn't respawned yet

        # Simulate cutting action
        self.player.add_xp("Woodcutting", tree_data["xp"])
        self.player.add_item_to_inventory(tree_data["log_id"], 1)
        # Player's add_item_to_inventory should handle the success message

        self.tree_depleted_at = time.time() + tree_data["respawn_time"]
        print(f"The {self.current_tree} is depleted. It will respawn in {tree_data['respawn_time']} seconds.")

        # For continuous cutting until stopped by player (desired behavior for idle game):
        # Do nothing here to stop it. It will continue on the same tree after respawn.
        # If stop after one log:
        # self.stop_cutting()
        # print(f"The {self.current_tree} has been felled.")
