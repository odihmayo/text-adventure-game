import json
import art
import os
import pygame 
pygame.mixer.init()   

class Room:
    """A class representing a room in the text adventure game.
    
    Attributes:
    name (str): The name of the room.
    description (str): A dictionary of direction of the room.
    exits (dict): A dictionary of directions (e.g, 'north') to room names (e.g., 'Kitchen').
    items (list): A list of items in the room. 
    trap(bool: Whether the room has a trap.
    chest_locked (bool): Whether the room has a locked chest.
    guard_present (bool): Whether a guard is present in the room.
    """
    def __init__(self, name, description, exits=None, items=None, trap=False, chest_locked=False, guard_present=False):
        self.name = name
        self.description = description
        self.exits = exits if exits is not None else {}
        self.items = items if items is not None else []
        self.trap = trap
        self.chest_locked = chest_locked
        self.guard_present = guard_present

    def get_description(self):
        """Get a formatted description of the room, including exists, items, traps, chest, and guard.
        Returns:
        str: The formatted description of the room.
        """
        desc = self.description
        if self.exits:
            desc += f" Exits: {' , '.join(self.exits.keys())}."
        if self.items:
            desc += f" You see: {', '.join(item.name + ' ' + item.description for item in self.items)}."
        else:
            desc += f"The room is now empty."
        if self.trap:
            desc += " Watch out! there's a trap here!"
        if self.chest_locked:
            desc += " There's a locked chest here."
        elif self.name == "Treasure Room" and not self.chest_locked:
            desc += "The chest is now open."
        if self.guard_present:
            desc += "A guard is blocking the chest!"
        elif self.name == "Treasure Room" and not self.guard_present:
            desc += "The guard is gone."
        return desc

    def save(self):
        """Save the room's state to a dictionary for serialization.
        Returns:
                dict: A dictionary containing the room's state.
        """
        return{
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "items": [{"type": item.__class__.__name__, "name":item.name, "description":item.description} for item in self.items],
            "trap": self.trap,
            "chest_locked": self.chest_locked,
            "guard_present": self.guard_present
        }

    @staticmethod
    def load(data):
        """Load a room from a dictionary of saved data.
        Args:
        data (dict): A dictionary containig the saved room data.
        
        Returns:
        Room: A new Room object with the loaded state.
        """

        item_classes = {"Item": Item, "Tool": Tool, "Treasure": Treasure, "Map": Map, "Weapon": Weapon}
        items = []
        for item_data in data["items"]:
            item_type = item_data["type"]
            item_name = item_data["name"]
            item_description = item_data.get("description", "A generic item.")
            item_class = item_classes.get(item_type, Item)
            items.append(item_class(item_name, item_description))
        return Room(
            name=data["name"],
            description=data["description"],
            exits=data["exits"],
            items=items,
            trap=data["trap"],
            chest_locked=data["chest_locked"],
            guard_present=data.get("guard_present", False)
        )

class Player:
    """ A class representing the player in the text adventure game.
    Attributes:
    current_room (Room): The player's current room.
    inventory (list): A list of items the player is carrying.
    score (int): The player's current score.
    """

    def __init__(self, current_room):
        self.current_room = current_room
        self.inventory = []
        self.score = 0
    
    def move(self, direction):
        """Move the player in a specified direction if possible.

        Args:
        direction (str): The direction to move (e.g., 'north', 'east').

        Returns:
        str or None: The name of the next room if the move is possible, None otherwise.
        """
        if direction in self.current_room.exits:
            return self.current_room.exits[direction]
        return None

    def take(self, item):
        """Take an item from the current room and add it to the player's inventory.
        Args:
        item (str): The name of the item to take.
        Returns:
        bool: True if the item was taken, False otherwise.
        """
        for room_item in self.current_room.items:
            if room_item.name == item:
                self.current_room.items.remove(room_item)
                self.inventory.append(room_item)
                if isinstance(room_item, Treasure):
                    self.add_score(20)
                else:
                    self.add_score(10)
                print(f"You picked up the {room_item.name}: {room_item.description}.")
                return True
        return False

    def get_inventory(self):
        """Get a list of item names in the player's inventory.
        Return:
        list or str: A list of item names if the inventory is not empty, a message if it is.
        """ 
        if self.inventory:
            return[item.name for item in self.inventory]
        return "Your inventory is empty."

    def save(self):
        """Save the player's state to dictionary for serialization.
        Return:
        dict: A dictionary containing the player's state.
        """
        return {
            "current_room": self.current_room.name,
            "inventory": [{"type": item.__class__.__name__, "name": item.name, "description": item.description} for item in self.inventory],
            "score": self.score
        }
    
    @staticmethod
    def load(data, rooms):
        """Load a player from a dictionary of saved data.
        Args:
        data (dict): A dictionary containing the saved player data.
        rooms (dict): A dictionary of loaded rooms.

        Returns:
        Player: A new player object with the loaded state.
        """
        player = Player(rooms[data["current_room"]])
        item_classes = {"Item": Item, "Tool": Tool, "Treasure": Treasure, "Map": Map, "Weapon": Weapon}
        player.inventory = []
        for item_data in data["inventory"]:
            item_type = item_data["type"]
            item_name = item_data["name"]
            item_description = item_data.get("description", "A generic item.")
            item_class = item_classes.get(item_type, Item)
            player.inventory.append(item_class(item_name, item_description))
        player.score = data["score"]
        return player

    def hint(self, rooms):
        """Provide a hint to the player based on thier current room and inventory.
        Args:
        rooms (dict): A dictionary of the rooms in the game.

        Returns:
        str: A hint message to guide the player.
        """
        room = self.current_room
        inv_names = [item.name for item in self.inventory]
        if room.name == "Hall" and "map" not in inv_names:
            return "There's a map here-maybe it reveals something usefull."
        elif room.name =="Kitchen" and "shield" not in inv_names:
            return "A shield in this room can protect you from danger elsewhere."
        elif room.name == "Living Room" and map in inv_names and "east" not in room.exits:
            return "Try using the map to uncover hidden path."
        elif room.name == "Garden" and  "shield" not in inv_names:
            return "This place looks dangerous. A shield might help you aviod the trap."
        elif room.name == "Treasure Room" and room.guard_present:
            return "The guard is blocking the chest! You might need a weapon to fight or a tool to distract them."
        elif room.name == "Treasure Room" and room.chest_locked:
            return "The chest is locked you will need a lockpick and crowbar to open it."
        elif room.name == "Treasure Room" and not room.chest_locked and "golden crown" not in inv_names:
            return "The chest is open! Make sure to take the golden crown."
        elif room.name == "Secret Room" and ("gem" not in inv_names or "lockpick" not in inv_names):
            return "Look around-there might be something valuable or useful here."
        elif "golden crown" in inv_names:
            return "You have got the golden crown! You've won-congratulations!"
        else:
            return "Explore your surroundings or check your inventory for clues."
    
    def add_score(self, points):
        """Add points to the player's score and display the updated total.
        Args:
        points (int): The number of points to add.
        """
        self.score += points
        print(f"You earned {points} points! Total score: {self.score}")

    def load_leaderboard(self):
        """Load the leaderboard from leaderboard.json.
        Returns:
        list: A list of dictionaries containing names and scores.
        """
        if os.path.exists("leaderboard.json"):
            with open("leaderboard.json", "r") as f:
                return json.load(f)
        return[]

    def save_leaderboard(self, leaderboard):
        """Save the leaderboard to leaderboard.json.
        Args:
        leaderboard (list): A list of dictionaries containing names and scores.
        """
        with open("leaderboard.json", "w") as f:
            json.dump(leaderboard, f)
    def update_leaderboard(self, player_name):
        """Add the player's score to the leaderboard and keep the top 5 scores.
        Args:
        player_name (str): The name of the player.
        """
        leaderboard = self.load_leaderboard()
        leaderboard.append({"name": player_name, "score": self.score})
        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:5]
        self.save_leaderboard(leaderboard)

    def display_leaderboard(self):
        """Display the current leaderboard.
        Return:
        str: A formatted string of the leaderboard.
        """
        leaderboard = self.load_leaderboard()
        if not leaderboard:
            return "Leaderboard is empty."
        result = "Leaderboard:\n"
        for i, entry in enumerate(leaderboard, 1):
            result += f"{i}.{entry['name']}: {entry['score']} points\n"
        return result

class Item:
    """A base class for items in the text adventure game.
    Attributes:
    name(str):The name of the item.
    description(str): A description of the item.
    """
    def __init__(self, name, description="A generic item."):
        self.name = name
        self.description = description

    def use(self, player, rooms):
        """Use the item (default behaviour for generic item).
        Args:
        player(Player): The player using the item.
        rooms(dict): A dictionary of the rooms in the game.

        Returns:
        str: A message indicating the result of using the item.
        """
        return f"You can't use the {self.name} right now."

class Tool(Item):
    """A class for tools, which have specific use (e.g., lockpick, crowbar, bell).
    Inherits from Item.
    """
    def __init__(self, name, description="A sturdy tool for specific tasks."):
        super().__init__(name, description)

    def use(self, player, rooms):
        """Use the tool based on its type and the current room.
        Args:
        player(Player): The player using the tool.
        rooms (dict): A dictionary of all rooms in the game.
        
        Returns:
        str: A message indicating the result of using the tool.
        """
        if player.current_room.name == "Treasure Room":
            has_lockpick = any(isinstance(item, Tool) and item.name == "lockpick" for item in player.inventory)
            has_crowbar = any(isinstance(item, Tool) and item.name == "crowbar" for item in player.inventory)
            if self.name == "bell" and player.current_room.guard_present:
                player.current_room.guard_present = False
                player.add_score(20)
                return "You rang the bell creating a loud noise. The guard is distracted and leaves the room!"
            if has_lockpick and has_crowbar and not player.current_room.guard_present:
                player.current_room.chest_locked = False
                player.current_room.items.append(Treasure("golden crown", "A shimmering crown encrusted with jewels."))
                player.add_score(50)
                return "You use the lockpick and the crowbar to pry open the chest! Inside, you find a golden crown."
                if has_lockpick and has_crowbar and player.current_room.guard_present:
                    return "The guard is blocking the chest! You need to deal with the guard first."
                if not has_lockpick and not has_crowbar:
                    return"You need both a lockpick and a crowbar to open the chest. You're missing both."
                if not has_lockpick:
                    return "You need a lockpick to open the chest."
                    return "You need a crowbar to open the chest."
                    return f"You can't use the {self.name} right now."

class Treasure(Item):
    """A class for treasure items, which award points when taken.
    inherits from item.
    """
    def __init__(self, name, description="A valuable treasure that gleams with worth."):
        super().__init__(name, description)

    def use(self, player, rooms):
        """Use the treasure item (provides a hint to take it for points).
        Args:
        player(Player): The player using the item.
        rooms(dict): A dictionary of all rooms in the game.

        Return:
        str:A message indicating the result of using the item.
        """
        return f"The {self.name} is a valuable treasure! You should take it to add to your score."

class Map(Item):
    """A class for the map item, which reveals hidden passages.
    Inherits from Item.
    """
    def __init__(self, name, description="An old map that might reveal hidden paths."):
        super().__init__(name, description)

    def use(self, player, rooms):
        """Use the map to reveal a hidden paasage in the Living Room.
        Args.
        player(Player): The player using the map.
        room (dict): A dictionary of all the rooms in the game.

        Rteurns:
        str:A message indicating the result of using the map.
        """
        if "east" not in rooms["Living Room"].exits:
            rooms["Living Room"].exits["east"] = "Secret Room"
            player.add_score(20)
            return "You use the map and discover a hidden passage! An east exit appears in the Living Room"
        return "You've already used the map to reveal the hidden passage."

class Weapon(Item):
    """A class for weapons, which can be used to fight enemies(e.g., the guard).
    Inherits from Item.
    """
    def __init__(self, name, description="A sharp weapon for combat."):
        super().__init__(name, description)
   
    def use(self, player, rooms):
        """Use the weapon to fight the guard in the treasure Room.
           Args.
        player(Player): The player using the weapon.
        room (dict): A dictionary of all the rooms in the game.

        Rteurns:
        str:A message indicating the result of using the weapon.
        """
        if player.current_room.name == "Treasure Room" and player.current_room.guard_present:
            player.current_room.guard_present = False
            player.add_score(30)
            return "You use the sword to defeat the guard! The path to the chest is now clear."
        return f"You can't use the {self.name} right now."
                    
def create_room():
    """Created a dictionary of rooms for the game, ensuring a fresh state for each session.
    Returns:
    dict: A dictionary mapping room names to Room objects.
    """  
    return {
        "Hall": Room(
            name="Hall",
            description="You are in a dusty hall.",
            exits={"north": "Kitchen", "east": "Living Room"},
            items=[Map("map", "An old parchment map with faded marking.")]
        ),

        "Kitchen": Room(
            name="Kitchen",
            description="You are in a small kithchen. There is a table here.",
            exits={"south": "Hall", "west": "Garden", "north": "Treasure Room"},
            items=[Item("shield", "A sturdy wooden shield for protection.")]
        ),

        "Living Room": Room(
            name="Living Room",
            description="You are in a cozy living room with a sofa.",
            exits={"west": "Hall"},
            items=[Tool("bell", "A small bell that makes a loud noise.")]
        ),

        "Garden": Room(
            name="Garden",
            description="You are in a sunny garden.",
            exits={"east": "Kitchen"},
            items=[Tool("crowbar", "A heavy iron crowbar, perfect for prying things open.")],
            trap=True
        ),

        "Treasure Room": Room(
            name="Treasure Room",
            description="You are in a dimly lit treasure room. A large chest sits in the corner.\n"
            "  ----\n"
            "  /    \\\n"
            " /------\\\n"
            " | ***  | \n"
            " |------|",
            exits={"south": "Kitchen"},
            chest_locked=True,
            guard_present=True
        ),

        "Secret Room": Room(
            name="Secret Room",
            description="You are in a hidden secrect room. The air is musty, but you see some valuable items.",
            exits={"west": "Living Room"},
            items=[
                Treasure("gem", "A sparkling ruby that glows faintly."), 
                Tool("lockpick", "A small metal tool for picking locks."), 
                Weapon("sword", "A sharp steel sword for combat.")
            ]
        ),
    }
def save_game(player, rooms, filename="savegame.json"):
    """ Save the current game state (player and rooms) to a JSON file.
    Args:
    player (Player): The player object to save.
    rooms (dict): The dictionary of room object to save.
    filename (str): The name of the file to save to (default: 'savegame.json').
    Returns:
    str: A message indicating success or failure.
    """
    
    game_state = {
        "player": player.save(),
        "rooms": {name: room.save() for name, room in rooms.items()}
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(game_state, f)
        return "Game saved successfully!"
    except PermissionError as e:
        return f"Error saving game: Permission denied. Check if you have write access to {filename} ({str(e)})."
    except IOError as e:
        return f"Error saving game: File error. The disk might be full or the file might be in use ({str(e)})."
    except json.JSONEncodeError as e:
        return f"Error saving game: Failed to serialize game state to JSON ({str(e)})."
    except Exception as e:
        return f"Error saving game: An unexpected error occurred ({str(e)})."


def load_game(filename="savegame.json"):
    """Load a saved game state from a JSON file.
    Args:
    filename (str): The name of the file to load from (default: 'savegame.json').
    
    Returns:
    tuple: (Player, rooms, message) where player and rooms are the loaded game state,
            or(None, None, error_message) if loading fails.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                game_state = json.load(f)
                try:
                    loaded_rooms = {name: Room.load(room) for name, room in game_state["rooms"].items()}
                    player = Player.load(game_state["player"], loaded_rooms)
                    return player, loaded_rooms, "Game loaded succesfully!"
                except KeyError as e:
                    return None, None, f"Error loading game: Missing key in save file ({str(e)})."
            except json.JSONDecodeError as e:
                return None, None, f"Error loading game: Corrupted save file (invalid JSON, {str(e)})."           
    except FileNotFoundError:
        return None, None, "No saved game found."
    except PermissionError as e:
        return None, None, f"Error loadig game: Permission denied. Check if you have read access to {filename} ({str(e)})."    
    except IOError as e:
        return None, None, f"Error loading game: File error ({str(e)})."
    except Exception as e:
        return None, None, f"Error loading game: An unexpected error occurred ({str(e)})."
        

def play_game():
    """Start a new game session, allowing the player to explore rooms and interact with items.
    Args: None.
    
    Returns:
    str or bool: A message if the game ends (e.g., ' Thanks for playing!') or False if the 
    player wins/losses.
    """
    rooms = create_room()
    player = Player(rooms["Hall"])
    print(art.text2art("Text Adventure"))
    print("Welcome to the Text Adventure Game!")
    print("You goal: Find the golden crown and escape with it!")
    player_name = input("Please enter your name:").strip()
    while not player_name:
        player_name = input("Name cannot be empty. Please enter your name:").strip()
    
    print("\nAvialable Commands:")
    print("-Movement: north, east, south, west")
    print("-Actions: take <item>, use <item>, inventory, hint, save, load, help, quit")
    print("Example: 'take map' or 'use sword' or 'leaderboard'")
    print("-----")

    while True:
        print("-----")
        print(player.current_room.get_description())
        if player.current_room.name == "Treasure Room":
            pygame.mixer.Sound("sound/chest.wav").play()
        print("-----")

        if any(item.name == "golden crown" for item in player.inventory):
            player.add_score(100)
            print(art.text2art("You win!"))
            try:
                pygame.mixer.Sound("sound/victory.wav").play()
                pygame.time.wait(2000)
            except pygame.error as e:
                print(f"Error playing trap sound: {e}")
            print("\nCongratulation! You have obtained the golden crown and won the game!")
            print(f"Final score: {player.score}")
            player.update_leaderboard(player_name)
            print(player.display_leaderboard())
            return False

        if player.current_room.trap and "shield" not in [item.name for item in player.inventory]:
            print("\nYou triggered a trap in the Garden and lost!")
            print(f"Final score: {player.score}")
            try:
                pygame.mixer.Sound("sound/trap.wav").play()
                pygame.time.wait(2000)
            except pygame.error as e:
                print(f"Error playing trap sound:{e}")
            player.update_leaderboard(player_name)
            print(player.display_leaderboard())
            return False

        command = input("What do you want to do? ").strip().lower()  
        command = command.strip()
        if not command:
            print("\nPlease enter a command. Type 'help' for a list of commands.")
            continue
        if command.lower() == "leaderboard":
            print(player.display_leaderboard())
            continue
        valid_single_commands = ["north", "east", "south", "west", "quit", "inventory", "hint", "save", "load", "help"]
        if command in valid_single_commands:
            pass
        elif command.startswith("take ") or command == "take":
            pass
        elif command == "use" or (command.startswith("use ") and not command[4:].strip()):
            print("\nPlease specify an item to use (e.g.,'use map').")
            continue
        elif not command.replace(" ", "").isalnum():
            print("\nCommand can only contain letters, numbers, and spaces.") 
            print("\nTry a direction like 'north' or a command like 'take map'.")
            continue
        if command == "quit":
            print("\nThanks for playing!")
            return False
        elif command == "inventory":
            inv = player.get_inventory()
            if isinstance(inv, list) and inv:
                print("\nYour inventory:")
                for i, item in enumerate(inv, 1):
                    print(f"{i}. {item}")
            else:
                print("\nYour inventory is empty")
        elif command == "hint": 
            print("\n" + player.hint(rooms))
        elif command == "help":
            print("\nAvialable Commands:")
            print("- Movement: north, east, south, west")
            print("- Action: take <item>, use <item>, inventory, hint, save, load, help, quit")
            print("Goal: Find the golden crown and escape with it!")
        elif command == "save":
            print("\n" + save_game(player, rooms))
        elif command == "load":
            loaded_player, loaded_rooms, message = load_game()
            if loaded_player and loaded_rooms:
                player = loaded_player
                rooms.clear()
                rooms.update(create_room())
                rooms.update(loaded_rooms)
                player.current_room = rooms[player.current_room.name]
                print("\nGame loaded successfully!")
            else:
                print("\n" + message)
        elif command.startswith("take "):
            item_name = command[5:].strip()
            if not item_name:
                print("\nPlease specify an item to take (e.g, 'take map').")
                continue
            if not item_name.replace(" ", "" ).isalnum():
                print("\nItem names can only contain letters, numbers, and spaces.")
                continue
            if player.take(item_name):
                print(f"\nYou picked up the {item_name}.")
            else:
                print(f"\nThere's no {item_name} here to take.")
        elif command.startswith("use "):
            item_name = command[4:].strip()
            if not item_name:
                print("\nPlease specify an item to use (e.g 'use map').")
                continue
            if not item_name.replace(" ", "").isalnum():
                print("\nItem names can only contain letters, numbers, and spaces.")
                continue
            result = next((item.use(player, rooms) for item in player.inventory if item.name == item_name), None)
            if result:
                print(f"\n{result}")
            else:
                temp_item = Item(item_name)
                print(f"\n{temp_item.use(player, rooms)}")
        else:
            next_room_name = player.move(command)
            if next_room_name:
                player.current_room = rooms[next_room_name]
            else:
                print("\nYou can't go that way! Try a direction like 'north' or 'east'.")

def main():
    while True:
        play_again = play_game()
        if not play_again:
            break
if __name__== "__main__":
    main()