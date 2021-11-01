#!/usr/bin/env python

"""A simple Multi-User Dungeon (MUD) game. Players can talk to each
other, examine their surroundings and move between rooms.

Some ideas for things to try adding:
    * More rooms to explore
    * An 'emote' command e.g. 'emote laughs out loud' -> 'Mark laughs
        out loud'
    * A 'whisper' command for talking to individual players
    * A 'shout' command for yelling to players in all rooms
    * Items to look at in rooms e.g. 'look fireplace' -> 'You see a
        roaring, glowing fire'
    * Items to pick up e.g. 'take rock' -> 'You pick up the rock'
    * Monsters to fight
    * Loot to collect
    * Saving players accounts between sessions
    * A password login
    * A shop from which to buy items

author: Mark Frimston - mfrimston@gmail.com

modified by Giles Booth to add Bush House location, shouting, objects,
ability to pick up and drop some objects, inventory, whiteboard
"""

import time

# import the MUD server class
from mudserver import MudServer

splash = '''
 ______                  
/_  __/__ _    _____ ____
 / / / _ \ |/|/ / -_) __/
/_/  \___/__,__/\__/_/   
           ___           
     ___  / _/           
    / _ \/ _/            
   _\___/_/  __       __ 
  / _ )___ _/ /  ___ / / 
 / _  / _ `/ _ \/ -_) /  
/____/\_,_/_.__/\__/_/   
                         '''


# structure defining the rooms in the game. Try adding more rooms to the game!
rooms = {
    "Studio Managers\' Common Room": {
        "description": "You're in a small dimly-lit room.\n",
        "exits": {"outside": "Corridor"},
    },
    "Corridor": {
        "description": "You're standing in a corridor outside the Studio Managers\' Common Room.\nIt leads off to the north.",
        "exits": {"inside": "Studio Managers\' Common Room", "north": "Duty Operations Manager\'s office"},
    },
    "Duty Operations Manager\'s office": {
        "description": "The Duty Operation Manager\'s office. The DOM is on the phone.",
        "exits": {"south": "Corridor", "north": "Landing"},
    },
    "Landing": {
        "description": "A beautiful landing. The walls and floors are covered in marble.",
        "exits": {"south": "Duty Operations Manager\'s office", "down": "Lobby"},
    },
    "Lobby": {
        "description": "A marble lobby.",
        "exits": {"north": "Club", "up": "Landing", "west": "Canteen"},
    },
    "Club": {
        "description": "The Bush House BBC Club. \nIf you\'d like to play a proper adventure set in Bush House visit http://suppertime.co.uk/tower-of-babel/play.html",
        "exits": {"south": "Lobby"},
    },
    "Canteen": {
        "description": "A large canteen with a low ceiling, dirty formica tables and flourescent lighting.",
        "exits": {"east": "Lobby"},
    },
}

objects = {
    "whiteboard" : {
    	"description": "It says 'For sale: bathmat, slightly soiled.'",
    	"portable": False,
    	"location": "Studio Managers\' Common Room"
    },
    "sofa" : {
    	"description": "An old saggy sofa covered in dubious stains.",
    	"portable": False,
    	"location": "Studio Managers\' Common Room"
    },
    "key" : {
    	"description": "A key with the words STUDIO stamped on it.",
    	"portable": True,
    	"location": "Duty Operations Manager\'s office"
    },
    "fishtank" : {
    	"description": "A long fishtank in which bored tropical fish are swimming",
    	"portable": False,
    	"location": "Club"
    },
    "fruit machine" : {
    	"description": "A fruit machine with flashing lights.",
    	"portable": False,
    	"location": "Club"
    },
    "bottle of beer" : {
    	"description": "A bottle of Young\'s Ram Rod.",
    	"portable": True,
    	"location": "Club"
    },

}

# stores the players in the game
players = {}

# start the server
mud = MudServer()

# main game loop. We loop forever (i.e. until the program is terminated)
while True:

    # pause for 1/5 of a second on each loop, so that we don't constantly
    # use 100% CPU time
    time.sleep(0.2)

    # 'update' must be called in the loop to keep the game running and give
    # us up-to-date information
    mud.update()

    # go through any newly connected players
    for id in mud.get_new_players():

        # add the new player to the dictionary, noting that they've not been
        # named yet.
        # The dictionary key is the player's id number. We set their room to
        # None initially until they have entered a name
        # Try adding more player stats - level, gold, inventory, etc
        players[id] = {
            "name": None,
            "room": None,
            "inventory": [],
        }

        # send the new player a prompt for their name
        mud.send_message(id, "What is your name?")

    # go through any recently disconnected players
    for id in mud.get_disconnected_players():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue

        # go through all the players in the game
        for pid, pl in players.items():
            # send each player a message to tell them about the diconnected
            # player
            mud.send_message(pid, "{} has left the building".format(
                                                        players[id]["name"]))
                                                        
        # players leaving the game should drop any objects they're carrying
        for item in players[id]["inventory"]:
            objects[item]["location"] = players[id]["room"]
            
        # remove the player's entry in the player dictionary
        del(players[id])

    # go through any new commands sent from players
    for id, command, params in mud.get_commands():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue

        # if the player hasn't given their name yet, use this first command as
        # their name and move them to the starting room.
        if players[id]["name"] is None:

            players[id]["name"] = command
            players[id]["room"] = "Studio Managers\' Common Room"

            # go through all the players in the game
            for pid, pl in players.items():
                # send each player a message to tell them about the new player
                mud.send_message(pid, "{} entered the game".format(
                                                        players[id]["name"]))

            # send the new player a welcome message
            mud.send_message(id, splash+"\nWelcome to the Tower of Babel, {}.\nThis is a test game made in MUD Pi with just a few rooms but you can talk to other players. ".format(
                                                           players[id]["name"])
                             + "\n\nType 'help' for a list of commands. Have fun!\n")

            # send the new player the description of their current room
            mud.send_message(id, rooms[players[id]["room"]]["description"])

        # each of the possible commands is handled below. Try adding new
        # commands to the game!

        # 'help' command
        elif command == "help":

            # send the player back the list of possible commands
            mud.send_message(id, "Commands:")
            mud.send_message(id, "  say <message>   - Say something out loud, "
                                 + "e.g. 'say Hello'")
            mud.send_message(id, "  shout <message> - Shout something, "
                                 + "e.g. 'shout Hello'")
            mud.send_message(id, "  look            - Look at the "
                                 + "surroundings, e.g. 'look'")
            mud.send_message(id, "  examine <thing> - Examine an object in "
                                 + "detail, e.g. 'examine key'")
            mud.send_message(id, "  take <thing>    - Pick an object up "
                                 + "e.g. 'take key'")
            mud.send_message(id, "  drop <thing>    - Put an object down "
                                 + "e.g. 'drop key'")
            mud.send_message(id, "  inventory       - List what you\'re carrying")
            mud.send_message(id, "  write <message> - Write on the whiteboard "
                                 + "e.g. 'write Sam was here'")
            mud.send_message(id, "  go <exit>       - Move through the exit "
                                 + "specified, e.g. 'go outside'")

        # 'say' command
        elif command == "say":

            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # send them a message telling them what the player said
                    mud.send_message(pid, "{} says: {}".format(
                                                players[id]["name"], params))

        # 'shout' command
        elif command == "shout":

            # go through every player in the game
            for pid, pl in players.items():
                # send them a message telling them what the player said
                mud.send_message(pid, "{} shouts: {}".format(
                                            players[id]["name"], params))


        # examine object if it exists and is in your room
        elif command == "examine":
            if params in objects and objects[params]["location"] == players[id]["room"]:
                mud.send_message(pid, objects[params]["description"])
            else:
                mud.send_message(pid, "There\'s no {} here.".format(params))
			
					
        # 'look' command
        elif command == "look":

            # store the player's current room
            rm = rooms[players[id]["room"]]

            # send the player back the description of their current room
            mud.send_message(id, rm["description"])

            playershere = []
            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # ... and they have a name to be shown
                    if players[pid]["name"] is not None:
                        # add their name to the list
                        playershere.append(players[pid]["name"])
                        
            # list objects in your location
            objectshere = []
            for thing in objects:
            	if objects[thing]["location"] == players[pid]["room"]:
            		objectshere.append("a " + thing)
            if len(objectshere) > 0:
	            mud.send_message(id, "You can see {}".format(", ".join(objectshere)))

            # send player a message containing the list of players in the room
            mud.send_message(id, "Players here: {}".format(
                                                    ", ".join(playershere)))

            # send player a message containing the list of exits from this room
            mud.send_message(id, "Exits are: {}".format(
                                                    ", ".join(rm["exits"])))

        elif command == "take":
            if params in objects and objects[params]["location"] == players[id]["room"]:
                if objects[params]["portable"]:
                    mud.send_message(id, "You take the {}.".format(params))
                    players[id]["inventory"].append(params)
                    objects[params]["location"] = players[id]
                else:
                    mud.send_message(id, "The {} is far too heavy to pick up.".format(params))
            else:
                mud.send_message(id, "There\'s no {} here.".format(params))
                
        elif command == "drop":
            if params in players[id]["inventory"]:
                mud.send_message(id, "You drop the {}.".format(params))
                # remove object from player's inventory
                players[id]["inventory"].remove(params)
                # change object's location to current room
                objects[params]["location"] = players[id]["room"]
            else:
                mud.send_message(id, "You\'re not carrying a {}.".format(params))

                
        elif command == "inventory":
            if len(players[id]["inventory"]) > 0:
                inv_list = "You\'re carrying:"
                for item in players[id]["inventory"]:
                    inv_list = inv_list + "\n- a " + item
                mud.send_message(id, inv_list)
            else:
                mud.send_message(id, "You\'re not carrying anything.")
            

        # 'go' command
        elif command == "go":

            # store the exit name
            ex = params.lower()

            # store the player's current room
            rm = rooms[players[id]["room"]]

            # if the specified exit is found in the room's exits list
            if ex in rm["exits"]:

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] \
                            and pid != id:
                        # send them a message telling them that the player
                        # left the room
                        mud.send_message(pid, "{} left via exit '{}'".format(
                                                      players[id]["name"], ex))

                # update the player's current room to the one the exit leads to
                players[id]["room"] = rm["exits"][ex]
                rm = rooms[players[id]["room"]]

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same (new) room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] \
                            and pid != id:
                        # send them a message telling them that the player
                        # entered the room
                        mud.send_message(pid,
                                         "{} arrived via exit '{}'".format(
                                                      players[id]["name"], ex))

                # send the player a message telling them where they are now
                mud.send_message(id, "You arrive at '{}'".format(
                                                          players[id]["room"]))

            # the specified exit wasn't found in the current room
            else:
                # send back an 'unknown exit' message
                mud.send_message(id, "You can\'t go '{}'".format(ex))
                
        # allow player to leave a message on the whiteboard
        elif command == 'write':
            if players[pid]["room"] == "Studio Managers\' Common Room":
                objects["whiteboard"]["description"] = "It says '{}'".format(params)
                mud.send_message(id, "You have written '{}' on the whiteboard.".format(params))
            else:
                mud.send_message(id, "There's nothing to write on here.")

		# player pressed enter with no command
        elif command == '':
        	mud.send_message(id, "Give me a command.")

        elif command == 'quit':
        	mud.send_message(id, "To leave the game press ctrl-] and type 'quit' again at the telnet prompt.")
        
        # some other, unrecognised command
        else:
            # send back an 'unknown command' message
            mud.send_message(id, "I don\'t understand '{}'".format(command))
