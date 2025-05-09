 Text Adventure Game

 A Python-based text adventure game where you explore rooms, solve puzzles, and defeat a guard to obtain the golden crown and win! 

Installation:
 1. Ensure you have Python 3 installed on your computer. 

 2. Download or clone this repository. 

 3. Open a terminal and navigate to the project directory.

 4. Run the game by typing:

 How to Play 

 Navigate through rooms to find items, solve puzzles, interact with Npc  and avoid traps to win the golden crown. -

 Commands: - `north`, `east`, `south`, `west`: Move in a direction.
 take <item>: Pick up an item (e.g., `take map`).  
 
 use <item>: Use an item (e.g., `use map`).

 drop <item>: Use 'drop <item> (e.g., 'drop map') to remove an item from your inventory and place it back in the current room. 
 
 inventory: List your items with Limits. Player can carry up to 3 items at a time. if inventory is full, you must drop an item before taking another.  
 
 hint: Get a hint for the current room.  
 
 save: Save your progress.  
 
 load: Load a saved game. 
 
 help: Show the command list.
 
 talk: talk to Npc.

 solve: solve puzzles and riddles 
 
 quit: Exit the game. 
 
**Goal**: Find and take the golden crown to win. 

 Features  
 
 Explore interconnected rooms with unique items and puzzles.  
- Use items like the map to reveal hidden exits or the sword to fight a guard.
- Solve puzzles and interact with Npc. 
- Save and load your progress to a JSON file. 
- Earn points for actions like taking treasures or solving puzzles.
  ASCII art for the title screen, treasure chest, and win screen.
  A scoring leaderboard that tracks the top 5 high scores (viewable anytime with the 'leaderboard' command).
  Sound effects for key events: entering the treasure room, winning the game, and triggering a trap
  (requires '.wav' files in a sound\folder).
  Dynamic room description that update based on player actions, such as items being taken, the chest being 
  unlocked, or the guard being defeated.


Example Gameplay

 You start in the Hall: 
    
   You are in a grand hall with dusty furniture. You see: map A folded parchment map. Exits: north, west. 
     What do you want to do? take map 
     You picked up the map. 
     What do you want to do? north 

You move to the Living Room: 
     
    You are in a cozy living room with a fireplace. You see: bell A shiny brass bell. Exits: south, east.
    What do you want to do? use map
    You use the map and discover a hidden passage! An east exit appears in the Living Room.
    You earned 20 points! Total score: 30 
From here, you can explore further, collect items, and solve puzzles to win the golden crown!

The game saves progress to savegame.json in the same folder as adv.py. this file is not included in the repository
but will be created when you use the save command.

CREATED BY 
C.M. Odih
aided by Grok.
