class Player:
    def __init__(self):
        self.skills = {}  # Stores skill levels and XP: {"Woodcutting": {"level": 1, "xp": 0}}
        self.inventory = {} # Stores items: {"item_id": quantity}
        self.active_skill = None

    def add_item_to_inventory(self, item_id, quantity=1):
        """Adds items to the player's inventory."""
        if item_id in self.inventory:
            self.inventory[item_id] += quantity
        else:
            self.inventory[item_id] = quantity
        print(f"Added {quantity}x {item_id} to inventory.")

    def remove_item_from_inventory(self, item_id, quantity=1):
        """Removes items from the player's inventory. Returns True if successful."""
        if item_id in self.inventory and self.inventory[item_id] >= quantity:
            self.inventory[item_id] -= quantity
            if self.inventory[item_id] == 0:
                del self.inventory[item_id]
            print(f"Removed {quantity}x {item_id} from inventory.")
            return True
        else:
            print(f"Could not remove {quantity}x {item_id}. Item not found or insufficient quantity.")
            return False

    def get_inventory_display(self):
        """Returns a string representation of the inventory."""
        if not self.inventory:
            return "Inventory: Empty"

        items_str = ", ".join([f"{item_id.replace('_', ' ').title()}: {qty}" for item_id, qty in self.inventory.items()])
        return f"Inventory: {items_str}"

    def get_skill_level(self, skill_name):
        return self.skills.get(skill_name, {}).get("level", 1)

    def get_skill_xp(self, skill_name):
        return self.skills.get(skill_name, {}).get("xp", 0)

    def add_xp(self, skill_name, xp_amount):
        if skill_name not in self.skills:
            self.skills[skill_name] = {"level": 1, "xp": 0}

        self.skills[skill_name]["xp"] += xp_amount
        # Simple XP to level conversion (example: 100 XP per level)
        # In a real game, this would be a more complex formula
        while self.skills[skill_name]["xp"] >= self.xp_for_next_level(self.skills[skill_name]["level"]):
            self.skills[skill_name]["level"] += 1
            print(f"Congratulations! Your {skill_name} level is now {self.skills[skill_name]['level']}!")

    def xp_for_next_level(self, current_level):
        # Example: level 1 needs 100 XP, level 2 needs 200 XP, etc.
        # This should be replaced with OSRS's actual XP curve eventually.
        return current_level * 100

    def set_active_skill(self, skill_name):
        self.active_skill = skill_name

    def clear_active_skill(self):
        self.active_skill = None
