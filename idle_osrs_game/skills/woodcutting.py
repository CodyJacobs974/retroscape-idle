import time

# Define tree types and their properties
TREES = {
    "Normal Tree": {"level_req": 1, "xp": 25, "log_id": "normal_log", "respawn_time": 5},
    "Oak Tree": {"level_req": 15, "xp": 37.5, "log_id": "oak_log", "respawn_time": 10},
    # Add more trees later
}

class Woodcutting:
    def __init__(self, player):
        self.player = player
        self.is_cutting = False
        self.current_tree = None
        self.tree_depleted_at = 0

    def start_cutting(self, tree_name):
        if tree_name not in TREES:
            print(f"No such tree: {tree_name}")
            return

        tree_data = TREES[tree_name]
        if self.player.get_skill_level("Woodcutting") < tree_data["level_req"]:
            print(f"You need level {tree_data['level_req']} Woodcutting to cut {tree_name}.")
            return

        self.is_cutting = True
        self.current_tree = tree_name
        self.player.set_active_skill("Woodcutting")
        print(f"You start cutting {tree_name}...")

    def stop_cutting(self):
        if self.is_cutting:
            self.is_cutting = False
            self.current_tree = None
            self.player.clear_active_skill()
            print("You stop cutting.")

    def update(self):
        if not self.is_cutting or not self.current_tree:
            return

        tree_data = TREES[self.current_tree]

        # Check if tree is depleted and needs to respawn
        if time.time() < self.tree_depleted_at:
            # print(f"{self.current_tree} is depleted. Waiting for respawn...")
            return # Tree hasn't respawned yet


        # Simulate cutting action (e.g., gain XP and logs periodically)
        # For simplicity, let's say one action per update call if not depleted

        # Action message will be handled by UI or more general message system if we add one.
        # For now, direct print is okay for testing.
        # print(f"You swing your axe at the {self.current_tree}.")

        self.player.add_xp("Woodcutting", tree_data["xp"])
        self.player.add_item_to_inventory(tree_data["log_id"], 1) # Add 1 log to inventory
        # Message updated in player.add_item_to_inventory
        # print(f"You get a {tree_data['log_id']} and gain {tree_data['xp']} Woodcutting XP.")


        # Tree gets depleted
        self.tree_depleted_at = time.time() + tree_data["respawn_time"]
        print(f"The {self.current_tree} is depleted. It will respawn in {tree_data['respawn_time']} seconds.")
        # print(f"{self.current_tree} depleted. It will respawn in {tree_data['respawn_time']} seconds.")

        # For continuous cutting until stopped by player:
        # If we want the player to automatically switch or stop, add logic here.
        # For now, it just waits for respawn and continues on the same tree.
        # If we want it to stop:
        # self.stop_cutting()
        # print(f"The {self.current_tree} has been felled.")
