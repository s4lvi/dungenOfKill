import numpy as np
import os
import time

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


class Player():
    def __init__(self, name, hp, mp, atk, df):
        self.name = name
        self.maxHp = hp
        self.hp = hp
        self.maxMp = mp
        self.mp = mp
        self.atk = atk
        self.df = df
        self.inventory = []
        self.armor = None
        self.weapon = None
        self.space = 10

    def showInventory(self):
        for i in range(len(self.inventory)):
            print(str(i) + ": " + self.inventory[i].name)
        if len(self.inventory) == 0:
            print(self.name + " isn't holding anything.")

    def use(self, item): 
        if item.type == "CONSUMABLE":
            if item.modifies == "hp":
                self.hp = self.hp + item.modifier
                if self.hp > self.maxHp:
                    self.hp = self.maxHp
            if item.modifies == "mp":
                self.mp = self.mp + item.modifier
                if self.mp > self.maxMp:
                    self.mp = self.maxMp
            print(str(item.modifier) + " " + item.modifies + " restored!")
            self.inventory.remove(item)

    def get(self, item, room):
        if len(self.inventory) < self.space:
            self.inventory.append(item)
            room.objects.remove(item)
            print(self.name + " takes the " + item.name)
        else:
            print(self.name + " cannot hold any more!")

    def drop(self, itemName, room):
        for i in self.inventory:
            if itemName == i.name.lower():
                room.objects.append(i)
                self.inventory.remove(i)
                print(self.name + " drops a " + itemName + " on the ground.")
                return
        print(self.name + " has no " + itemName + "!")

    def equip(self, item):
        if item.type == "WEAPON":
            if item.modifies == "atk":
                self.atk = self.atk + item.modifier
                self.weapon = item
                self.inventory.remove(item)
        if item.type == "ARMOR":
            if item.modifies == "df":
                self.df = self.df + item.modifier
                self.armor = item
                self.inventory.remove(item)

    def attack(self, target):
        print(self.name + " attacks!")
        target.hit(self.atk)

    def hit(self, dmg):
        mDmg = dmg - self.df
        if mDmg < 0:
            mDmg = 0
        print(self.name + " receives " + str(mDmg) + " damage.")
        self.hp = self.hp - mDmg
        if not self.isAlive():
            print(self.name + " has been killed!")

    def isAlive(self):
        if self.hp <= 0:
            return False
        return True
        
    def move(self, x, y):
        self.x = x
        self.y = y

class Object: 
    def __init__(self, name, type, description, value, modifies, modifier):
        self.name = name
        self.type = type
        self.description = description
        self.value = value
        self.modifies = modifies
        self.modifier = modifier

    def cycle(self, room, player):
        return

class Monster:
    def __init__(self, mId, name, hp, mp, atk, df, loot = []):
        self.mId = mId
        self.name = name
        self.maxHp = hp
        self.hp = hp
        self.maxMp = mp
        self.mp = mp
        self.atk = atk
        self.df = df
        self.armor = None
        self.weapon = None
        self.inventory = loot

    def attack(self, target):
        print(self.name + " attacks!")
        target.hit(self.atk)

    def hit(self, dmg):
        mDmg = dmg - self.df
        if mDmg < 0:
            mDmg = 0
        print(self.name + " receives " + str(mDmg) + " damage.")
        self.hp = self.hp - mDmg
        if not self.isAlive():
            print(self.name + " has been killed!")

    def isAlive(self):
        if self.hp <= 0:
            return False
        return True

    def dropAll(self, room):
        for i in self.inventory:
            room.objects.append(i)
            self.inventory.remove(i)
            print(self.name + " drops a " + i.name + " on the ground.")

    def cycle(self, room, player):
        self.attack(player)

class Room:
    def __init__(self, description, entities, objects):
        self.description = description
        self.entities = entities
        self.objects = objects
        self.exits = []

    def look(self):
        print(self.description)
        for e in self.exits:
            print("There is an exit to the " + e)
        if len(self.entities) > 0:
            for e in self.entities:
                if e.isAlive():
                    print("There is a " + e.name + " here.")
                else:
                    print("There is a dead " + e.name + " here.")
        if len(self.objects) > 0:
            for o in self.objects:
                print("There is a " + o.name + " here.")

    def cycle(self, player):
        toRemove = []
        for e in self.entities:
            if e.isAlive():
                e.cycle(self, player)
            else:
                e.dropAll(self)
                toRemove.append(e)
        for e in toRemove:
            self.entities.remove(e)
        for o in self.objects:
            o.cycle(self, player)

class Area:
    def __init__(self, rooms):
        self.rooms = rooms
        self.currentRoom = None
        self.currentX = 0
        self.currentY = 0

    def setRoom(self, x, y):
        if self.hasRoom(x, y):
            self.currentRoom = self.rooms[x][y]
            self.currentX = x
            self.currentY = y
        else:
            print("Cannot go that way")

    def hasRoom(self, x, y):
        if x >= 0 and y >= 0 and x < len(self.rooms) and y < len(self.rooms[x]) and self.rooms[x][y] != None:
            return True
        return False

    def getRoom(self):
        return self.currentRoom

    def getExits(self):
        for x in range(len(self.rooms)):
            for y in range(len(self.rooms[x])):
                if self.rooms[x][y] != None:
                    if self.hasRoom(x,y-1):
                        self.rooms[x][y].exits.append("n")
                    if self.hasRoom(x,y+1):
                        self.rooms[x][y].exits.append("s")
                    if self.hasRoom(x-1,y):
                        self.rooms[x][y].exits.append("w")
                    if self.hasRoom(x+1,y):
                        self.rooms[x][y].exits.append("e")
        
def genMob():
    num = np.random.randint(0,5)
    if num == 0:
        return Monster(np.random.rand(), 'Goblin', 10, 2, 8, 3, [Object("Goblin corpse", "JUNK", "The rotting corpse of a goblin", 5, "none", 0), genItem()])
    if num == 1:
        return Monster(np.random.rand(), 'RatMan', 15, 2, 8, 5, [Object("Ratman corpse", "JUNK", "The rotting corpse of a ratman", 5, "none", 0), genItem()])
    if num == 2:
        return Monster(np.random.rand(), 'Basilisk', 20, 5, 12, 5, [Object("Basilisk corpse", "JUNK", "The rotting corpse of a basilisk", 50, "none", 0), genItem(), genItem(), genItem(), genItem()])
    if num == 3:
        return Monster(np.random.rand(), 'Orc', 25, 2, 15, 3, [Object("Orc corpse", "JUNK", "The rotting corpse of an orc", 15, "none", 0), genItem(), genItem()])
    if num == 4:
        return Monster(np.random.rand(), 'Bandit', 15, 2, 8, 3, [Object("Bandit corpse", "JUNK", "The rotting corpse of a bandit", 15, "none", 0), genItem(), genItem(), genItem()])

def genItem():
    num = np.random.randint(0,100)
    if num > 0 and num < 20:
        return Object("Potion", "CONSUMABLE", "An elixir of health", 10, "hp", 20)
    if num > 20 and num < 40:
        return Object("Elixir", "CONSUMABLE", "An elixir of mana", 10, "mp", 10)
    if num > 40 and num < 45:
        return Object("Bronze Helmet", "ARMOR", "An bronze helm", 100, "df", 10)
    if num > 45 and num < 50:
        return Object("Bronze Shield", "ARMOR", "A bronze shield", 100, "df", 5)
    if num == 50:
        return Object("Dagger of kill", "WEAPON", "A worn but sturdy blade", 500, "atk", 15)
    if num == 51:
        return Object("Bronze Sword", "WEAPON", "A worn but sturdy blade", 100, "atk", 10)
    return Object("Junk", "JUNK", "Assorted scraps and debris", 0, "none", 0)


def command(c, area, player):
    tokens = c.lower().split(" ")
    if (tokens[0] == 'attack' or tokens[0] == 'hit' or tokens[0] == 'kill' or tokens[0] == 'kill'):
        for e in area.currentRoom.entities:
            if e.name.lower() == tokens[1]:
                player.attack(e)
                return
    if (tokens[0] == 'take' or tokens[0] == 'get'):
        if len(tokens) > 1:
            itemName = tokens[1]
            if len(tokens) > 2:
                for j in range(2,len(tokens)):
                    itemName = itemName + " " + tokens[j]
            for i in area.currentRoom.objects:
                if i.name.lower() == itemName:
                    player.get(i, area.currentRoom)
                    return
            print("There is no " + itemName + " here")
            return
    if (tokens[0] == 'pick' and len(tokens) > 1 and tokens[1] == 'up'):
        if len(tokens) > 2:
            itemName = tokens[2]
            if len(tokens) > 3:
                for j in range(3,len(tokens)):
                    itemName = itemName + " " + tokens[j]
            for i in area.currentRoom.objects:
                if i.name.lower() == itemName:
                    player.get(i, area.currentRoom)
                    return
            print("There is no " + itemName + " here")
            return
    if (tokens[0] == 'drop' or tokens[0] == 'discard'):
        itemName = tokens[1]
        if len(tokens) > 2:
            for j in range(2,len(tokens)):
                itemName = itemName + " " + tokens[j]
        player.drop(itemName, area.currentRoom)
        return
    if (tokens[0] == 'use'):
        itemName = tokens[1]
        if len(tokens) > 2:
            for j in range(2,len(tokens)):
                itemName = itemName + " " + tokens[j]
        for i in player.inventory:
            if i.name.lower() == itemName:
                if i.type == "CONSUMABLE":
                    print(player.name + " uses the " + i.name)
                    player.use(i)
                else:
                    print("You cannot use the " + i.name + " that way!")
                return
    if (tokens[0] == 'equip'):
        itemName = tokens[1]
        if len(tokens) > 2:
            for j in range(2,len(tokens)):
                itemName = itemName + " " + tokens[j]
        for i in player.inventory:
            if i.name.lower() == itemName:
                if i.type == "ARMOR" or i.type == "WEAPON":
                    print(player.name + " equips the " + i.name)
                    player.equip(i)
                else:
                    print("You cannot equip the " + i.name + "!")
                return
    if (tokens[0] == 'go'):
        if len(tokens) > 1:
            if tokens[1] == 'n':
                area.setRoom(area.currentX, area.currentY-1)
                area.currentRoom.look()
            if tokens[1] == 's':
                area.setRoom(area.currentX, area.currentY+1)
                area.currentRoom.look()
            if tokens[1] == 'e':
                area.setRoom(area.currentX+1, area.currentY)
                area.currentRoom.look()
            if tokens[1] == 'w':
                area.setRoom(area.currentX-1, area.currentY)
                area.currentRoom.look()
            return
        else:
            print("Go where?")
    if (tokens[0] == 'inventory' or tokens[0] == 'inv'):
        player.showInventory()
        return
    if (tokens[0] == 'look' or tokens[0] == 'skip'):
        area.currentRoom.look()
        return
    print("Unknown command: " + tokens[0])

name = input("Enter your name: ")
p = Player(name, 20, 10, 5, 5)
p.inventory.append(Object("Potion", "CONSUMABLE", "An elixir of health", 10, "hp", 20))
p.inventory.append(Object("Elixir", "CONSUMABLE", "An elixir of mana", 10, "mp", 10))
p.inventory.append(Object("Sword", "WEAPON", "A worn but sturdy blade", 10, "atk", 5))
p.inventory.append(Object("Breastplate", "ARMOR", "Shining bronze armor", 10, "df", 10))
cls()
print("Welcome, " + p.name + "...")
print("...to the DUNGEN of KILL")
playing = True
area = Area([[Room("A nondescript room", [], []),Room("A nondescript room", [genMob()], []),Room("A nondescript room", [], []),None,Room("A nondescript room", [], [])],
            [None,Room("A nondescript room", [], []),Room("A nondescript room", [genMob()], []),None],
            [Room("A nondescript room", [], []),Room("A nondescript room", [genMob()], []),None,Room("A nondescript room", [], []),Room("A nondescript room", [], [])],
            [Room("A nondescript room", [genMob()], []),Room("A nondescript room", [], []),None,Room("A nondescript room", [], []),Room("A nondescript room", [genMob()], [])]])
area.setRoom(0,0)
area.getExits()
time.sleep(1)
c = "skip"

while playing == True:
    cls()
    print("<<<<<<<<<DUNGEN OF KILL>>>>>>>>>>")
    print()
    command(c, area, p)
    area.currentRoom.cycle(p)
    if (not p.isAlive()):
        playing = False
        break
    print(p.name + " | hp:" + str(p.hp) + "/" + str(p.maxHp) + " | mp:" + str(p.mp) + "/" + str(p.maxMp))
    print("---------------------------------")
    print("Enter command:")
    c = input()
    time.sleep(.5)
cls()
tText = p.name
side = int((33 - len(tText)) / 2)
filler = "-" * side
tText = filler + tText + filler
if len(tText) == 32:
    tText = tText + "-"
print("             -------             ")
print("      ---------------------      ")
print(" ------------------------------- ")
print("------------Here Lies------------")
print("---------------------------------")
print(tText)
print("---------------------------------")
print("--------------R.I.P.-------------")
print("---------------------------------")
print("---------------------------------")

    
