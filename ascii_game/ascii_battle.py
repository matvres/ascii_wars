#!/usr/bin/env python3
"""
Small hot-seat 2-player ASCII turn-based battle game using curses.
Save as ascii_battle.py and run with `python3 ascii_battle.py`.

Controls (hot-seat):
 - Arrow keys: move cursor
 - Enter/Space: select/deselect a unit
 - m: move selected unit to cursor (if legal)
 - a: attack an adjacent enemy from selected unit to the cursor cell
 - e: end turn
 - q: quit

Notes:
 - Player 1 units are shown as uppercase letters and use color pair 1.
 - Player 2 units are shown as lowercase letters and use color pair 2.
 - This is intentionally small and self-contained.
"""

import curses
import random
import sys

# Game settings
WIDTH = 35
HEIGHT = 15

# Colors (indices for curses)
COLOR_P1 = 1
COLOR_P2 = 2
COLOR_CURSOR = 3
COLOR_HIGHLIGHT = 4
COLOR_ERROR = 99

# Terrain color indices (+ NUMBER OF ELEVATION LEVELS (5))
COLOR_WATER = 5
COLOR_GRASS = 10
COLOR_FOREST = 15
COLOR_ROAD = 20
COLOR_FIELD = 25
COLOR_BUILDING = 30
COLOR_SHRUB = 35

# Elevation levels:
COLOR_L0 = 110
COLOR_L1 = 111
COLOR_L2 = 112
COLOR_L3 = 113
COLOR_L4 = 114


# Unit definitions
"""
size: 1-10 ? (relevant for transport cargo/troops and spotting via optics)
arm: armor
optics: range 1-3 (bad-medium-good)
ws1 & ws2: weapon systems index (look at WEAPON_SYSTEM_TYPES)
"""
UNIT_TYPES = {
    'X': { 'name': 'Infantry',      'size':2,   'hp': 6, 'arm': 0,   'move': 2,  'flying': False,  'amph': False, 'ws1': 1, 'ws2': 2, 'ws1_ammo': 0, 'ws2_ammo': 0, 'optics': 1 },
    'T': { 'name': 'Tank',          'size':5,   'hp': 6, 'arm': 4,   'move': 2,  'flying': False,  'amph': False, 'ws1': 5, 'ws2': 3, 'ws1_ammo': 0, 'ws2_ammo': 0, 'optics': 1  },
    '>': { 'name': 'Atk. Helo',     'size':7,   'hp': 5, 'arm': 1,   'move': 4,  'flying': True,   'amph': False, 'ws1': 4, 'ws2': 0, 'ws1_ammo': 0, 'ws2_ammo': 0, 'optics': 3  },
    'O': { 'name': 'APC',           'size':5,   'hp': 6, 'arm': 2,   'move': 3,  'flying': False,  'amph': True , 'ws1': 4, 'ws2': 0, 'ws1_ammo': 0, 'ws2_ammo': 0, 'optics': 1 },
    'R': { 'name': 'Recon',         'size':1,   'hp': 4, 'arm': 0,   'move': 3,  'flying': False,  'amph': False, 'ws1': 1, 'ws2': 2, 'ws1_ammo': 0, 'ws2_ammo': 0, 'optics': 3  },
    'm': { 'name': 'Mortar',        'size':3,   'hp': 4, 'arm': 0,   'move': 1,  'flying': False,  'amph': False, 'ws1': 6, 'ws2': 0, 'ws1_ammo': 0, 'ws2_ammo': 0, 'optics': 2 },    # lahko dodamo radio operaterja kasneje k mortarju doda optics + range
    'C': { 'name': 'Cargo Truck',   'size':4,   'hp': 4, 'arm': 0,   'move': 3,  'flying': False,  'amph': False, 'ws1': 0, 'ws2': 0, 'ws1_ammo': 0, 'ws2_ammo': 0, 'optics': 1  },
    'A': { 'name': 'AA Gun',        'size':5,   'hp': 5, 'arm': 2,   'move': 2,  'flying': False,  'amph': False, 'ws1': 7, 'ws2': 7, 'ws1_ammo': 0, 'ws2_ammo': 0, 'optics': 2  },
}

# Weapon systems definitions
WEAPON_SYSTEM_TYPES = {
    0 : { 'name': '/',              'arm_pen': 0,  'dmg_val': 0, 'att_range': 0,   'ammo': 0,  'antiair': False },
    1 : { 'name': 'Small Arms',     'arm_pen': 1,  'dmg_val': 2, 'att_range': 2,   'ammo': 5,  'antiair': False },
    2 : { 'name': 'AT Rocket',      'arm_pen': 5,  'dmg_val': 3, 'att_range': 2,   'ammo': 1,  'antiair': False },
    3 : { 'name': 'Light MG',       'arm_pen': 1,  'dmg_val': 2, 'att_range': 3,   'ammo': 4,  'antiair': False },
    4 : { 'name': 'Heavy MG',       'arm_pen': 2,  'dmg_val': 3, 'att_range': 4,   'ammo': 4,  'antiair': False },
    5 : { 'name': 'Cannon',         'arm_pen': 5,  'dmg_val': 3, 'att_range': 5,   'ammo': 4,  'antiair': False },
    6 : { 'name': 'Heavy Mortar',   'arm_pen': 4,  'dmg_val': 6, 'att_range': 10,  'ammo': 3,  'antiair': False }, 
    7 : { 'name': 'MANPADS',        'arm_pen': 4,  'dmg_val': 5, 'att_range': 10,  'ammo': 3,  'antiair': True }, 
}

# Terrain definitions
TERRAIN_TYPES = {
    '.': { 'name': 'Open terrain',  'cover_lvl': 0, 'conceal': 0, 'mov_cost': 1, 'el_height': 0,  'pass': True,   'los': True },
    'f': { 'name': 'Light Woods',   'cover_lvl': 1, 'conceal': 2, 'mov_cost': 2, 'el_height': 1,  'pass': True,   'los': False },
    '+': { 'name': 'Road',          'cover_lvl': 0, 'conceal': 0, 'mov_cost': 1, 'el_height': 0,  'pass': True,   'los': True },
    '~': { 'name': 'Water',         'cover_lvl': 0, 'conceal': 0, 'mov_cost': 0, 'el_height': 0,  'pass': False,  'los': True },
    'F': { 'name': 'Heavy Woods',   'cover_lvl': 2, 'conceal': 3, 'mov_cost': 2, 'el_height': 1,  'pass': True,   'los': False },
    'H': { 'name': 'House',         'cover_lvl': 2, 'conceal': 4, 'mov_cost': 2, 'el_height': 1,  'pass': True,   'los': False },
    '*': { 'name': 'Shrubbery',     'cover_lvl': 0, 'conceal': 1, 'mov_cost': 1, 'el_height': 0,  'pass': True,   'los': False },
}

# Army starting positions
START_POSITIONS_P1 = [(1,1),(1,3),(1,5),(2,2),(2,4),(2,7)]
START_POSITIONS_P2 = [(WIDTH-2,HEIGHT-2),(WIDTH-2,HEIGHT-4),(WIDTH-2,2),(WIDTH-3,3),(WIDTH-3,5),(WIDTH-3,1)]

ARMY_P1 = [">","X","O","T","m","R"]
ARMY_P2 = ["X","X","T","O","X","X"]


class Unit:
    def __init__(self, x, y, owner, kind):
        un = UNIT_TYPES[kind]
        self.x = x
        self.y = y
        self.owner = owner  # 1 or 2
        self.kind = kind   # character symbol
        self.name = un['name']
        self.max_hp = un['hp'] 
        self.hp = self.max_hp
        self.arm = un['arm']

        self.move_range = un['move']
        self.amph = un['amph']
        self.flying = un['flying']

        self.ws1 = un['ws1']
        self.ws2 = un['ws2']
        self.ws1_ammo = WEAPON_SYSTEM_TYPES[self.ws1]['ammo']
        self.ws2_ammo = WEAPON_SYSTEM_TYPES[self.ws2]['ammo']
       
        # At some point se lahko doda action points system in cost-per-action/movement
        self.moved = False
        self.acted = False

    def is_alive(self):
        return self.hp > 0

    def distance_to(self, x, y):
        return abs(self.x - x) + abs(self.y - y)
    
    def display_ammo(self, ws_ammo):
        ammo = ""
        for i in range(ws_ammo):
            ammo+="|"
        return ammo


class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.cursor_x = 0
        self.cursor_y = 0
        self.turn = 1
        self.units = []
        self.selected = None
        self.message = "Welcome to ASCII Battle!"
        self.init_colors()
        self.populate_units()

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()

        # Admin colors
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, 230)
        curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, 220)
        curses.init_pair(COLOR_ERROR, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)

        # Players colors
        curses.init_pair(COLOR_P1, 0, 9)
        curses.init_pair(COLOR_P2, 0, 6)

        # Elevation colors
        curses.init_pair(COLOR_L0, -1, 46)
        curses.init_pair(COLOR_L1, -1, 40)
        curses.init_pair(COLOR_L2, -1, 34)
        curses.init_pair(COLOR_L3, -1, 28)
        curses.init_pair(COLOR_L4, -1, 22)

        # Terrain colors
        curses.init_pair(COLOR_GRASS, 22, -1)
        curses.init_pair(COLOR_FOREST, 22, -1)
        curses.init_pair(COLOR_ROAD, 142, -1)
        curses.init_pair(COLOR_WATER, 28, 39)
        curses.init_pair(COLOR_BUILDING, 52, 130)

        # Init color combinations (terrain + elevation)
        curses.init_pair(COLOR_L0+COLOR_GRASS, 22, 46)
        curses.init_pair(COLOR_L1+COLOR_GRASS, 22, 40)
        curses.init_pair(COLOR_L2+COLOR_GRASS, 22, 34)
        curses.init_pair(COLOR_L3+COLOR_GRASS, 22, 28)
        curses.init_pair(COLOR_L4+COLOR_GRASS, 22, 22)
        curses.init_pair(COLOR_L0+COLOR_FOREST, 22, 46)
        curses.init_pair(COLOR_L1+COLOR_FOREST, 22, 40)
        curses.init_pair(COLOR_L2+COLOR_FOREST, 22, 34)
        curses.init_pair(COLOR_L3+COLOR_FOREST, 22, 28)
        curses.init_pair(COLOR_L4+COLOR_FOREST, 22, 22)
        curses.init_pair(COLOR_L0+COLOR_ROAD, 142, 46)
        curses.init_pair(COLOR_L1+COLOR_ROAD, 142, 40)
        curses.init_pair(COLOR_L2+COLOR_ROAD, 142, 34)
        curses.init_pair(COLOR_L3+COLOR_ROAD, 142, 28)
        curses.init_pair(COLOR_L4+COLOR_ROAD, 142, 22)
        curses.init_pair(COLOR_L0+COLOR_SHRUB, 22, 46)
        curses.init_pair(COLOR_L1+COLOR_SHRUB, 22, 40)
        curses.init_pair(COLOR_L2+COLOR_SHRUB, 22, 34)
        curses.init_pair(COLOR_L3+COLOR_SHRUB, 22, 28)
        curses.init_pair(COLOR_L4+COLOR_SHRUB, 22, 22)


    def populate_units(self):
        # Place units for each side: P1 on left, P2 on right
        i = 0
        for x,y in START_POSITIONS_P1:
            self.units.append(Unit(x,y,1,ARMY_P1[i]))
            i+=1
        i = 0
        for x,y in START_POSITIONS_P2:
            self.units.append(Unit(x,y,2,ARMY_P2[i]))
            i=i+1

    def unit_at(self, x, y):
        for u in self.units:
            if u.is_alive() and u.x == x and u.y == y:
                return u
        return None

    def draw(self):
        self.stdscr.clear()
        # Draw border
        for y in range(HEIGHT+2):
            for x in range(WIDTH+2):
                if y==0 or y==HEIGHT+1:
                    ch = '-'
                elif x==0 or x==WIDTH+1:
                    ch = '|'
                else:
                    ch = ' '
                self.stdscr.addch(y, x, ch)

        # Draw terrain features and/or units
        for y in range(HEIGHT):
            for x in range(WIDTH):
                screen_x = x+1
                screen_y = y+1
                u = self.unit_at(x,y)
                
                # Unit layer
                if u and u.is_alive():
                    if u.owner == 1:
                        attr = curses.color_pair(COLOR_P1)
                    else:
                        attr = curses.color_pair(COLOR_P2)
                    ch = u.kind
                    self.stdscr.addch(screen_y, screen_x, ch, attr)
                    
                # Terrain layer
                else:
                    #self.stdscr.addch(screen_y, screen_x, map[y][x])
                    if map[y][x] == '.' and elev[y][x] == '0':
                        attr = curses.color_pair(COLOR_GRASS+COLOR_L0)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '.' and elev[y][x] == '1':
                        attr = curses.color_pair(COLOR_GRASS+COLOR_L1)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '.' and elev[y][x] == '2':
                        attr = curses.color_pair(COLOR_GRASS+COLOR_L2)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '.' and elev[y][x] == '3':
                        attr = curses.color_pair(COLOR_GRASS+COLOR_L3)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '.' and elev[y][x] == '4':
                        attr = curses.color_pair(COLOR_GRASS+COLOR_L4)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)


                    elif (map[y][x] == 'f' or map[y][x] == 'F') and elev[y][x] == '0':
                        attr = curses.color_pair(COLOR_FOREST+COLOR_L0)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif (map[y][x] == 'f' or map[y][x] == 'F') and elev[y][x] == '1':
                        attr = curses.color_pair(COLOR_FOREST+COLOR_L1)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif (map[y][x] == 'f' or map[y][x] == 'F') and elev[y][x] == '2':
                        attr = curses.color_pair(COLOR_FOREST+COLOR_L2)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif (map[y][x] == 'f' or map[y][x] == 'F') and elev[y][x] == '3':
                        attr = curses.color_pair(COLOR_FOREST+COLOR_L3)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif (map[y][x] == 'f' or map[y][x] == 'F') and elev[y][x] == '4':
                        attr = curses.color_pair(COLOR_FOREST+COLOR_L4)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)

                    elif map[y][x] == '+' and elev[y][x] == '0':
                        attr = curses.color_pair(COLOR_ROAD+COLOR_L0)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '+' and elev[y][x] == '1':
                        attr = curses.color_pair(COLOR_ROAD+COLOR_L1)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '+' and elev[y][x] == '2':
                        attr = curses.color_pair(COLOR_ROAD+COLOR_L2)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '+' and elev[y][x] == '3':
                        attr = curses.color_pair(COLOR_ROAD+COLOR_L3)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '+' and elev[y][x] == '4':
                        attr = curses.color_pair(COLOR_ROAD+COLOR_L4)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)

                    elif map[y][x] == '*' and elev[y][x] == '0':
                        attr = curses.color_pair(COLOR_SHRUB+COLOR_L0)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '*' and elev[y][x] == '1':
                        attr = curses.color_pair(COLOR_SHRUB+COLOR_L1)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '*' and elev[y][x] == '2':
                        attr = curses.color_pair(COLOR_SHRUB+COLOR_L2)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '*' and elev[y][x] == '3':
                        attr = curses.color_pair(COLOR_SHRUB+COLOR_L3)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '*' and elev[y][x] == '4':
                        attr = curses.color_pair(COLOR_SHRUB+COLOR_L4)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)

                    elif map[y][x] == '"':
                        attr = curses.color_pair(COLOR_FIELD)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == 'H':
                        attr = curses.color_pair(COLOR_BUILDING)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == '~':
                        attr = curses.color_pair(COLOR_WATER)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)

                    else:
                        attr = curses.color_pair(COLOR_ERROR)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
        
        # Highlight selected unit's possible moves
        if self.selected:
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.selected.distance_to(x,y) <= self.selected.move_range:
                        # Skip occupied by other unit
                        if not self.unit_at(x,y):
                            sx = x+1; sy = y+1
                            try:
                                self.stdscr.addch(sy,sx,'x', curses.color_pair(COLOR_HIGHLIGHT))
                            except curses.error:
                                pass

        # Draw cursor (invert cell)
        cx = self.cursor_x+1
        cy = self.cursor_y+1
        try:
            ch = chr(self.stdscr.inch(cy, cx) & 0xFF)
        except curses.error:
            ch = ' '
        self.stdscr.addch(cy, cx, ch, curses.color_pair(COLOR_CURSOR))

        # Info panel
        info_y = 0
        info_x = WIDTH + 4
        self.stdscr.addstr(info_y, info_x, f"Turn: Player {self.turn}")
        self.stdscr.addstr(info_y+1, info_x, f"Cursor: ({self.cursor_x},{self.cursor_y})")
        self.stdscr.addstr(info_y+2, info_x, f"Terrain: {TERRAIN_TYPES[map[self.cursor_y][self.cursor_x]]['name']}")
        self.stdscr.addstr(info_y+3, info_x, f"Elevation: {elev[self.cursor_y][self.cursor_x]} (+{TERRAIN_TYPES[map[self.cursor_y][self.cursor_x]]['el_height']} per terrain)" )
        self.stdscr.addstr(info_y+4, info_x, f"------------------------------------")
        u = self.unit_at(self.cursor_x, self.cursor_y)

        if u:
            self.stdscr.addstr(info_y+5, info_x, f"Unit: {'Player1' if u.owner==1 else 'Player2'} [ {u.kind} ] ({u.name})")
            self.stdscr.addstr(info_y+6, info_x, f"HP: {u.hp}/{u.max_hp}    ARMOR: {u.arm}")
            self.stdscr.addstr(info_y+7, info_x, f"MOVEMENT: {u.move_range}")
            self.stdscr.addstr(info_y+8, info_x, f"------------------------------------")
            self.stdscr.addstr(info_y+9, info_x, f"[1. WPN]: {WEAPON_SYSTEM_TYPES[u.ws1]['name']} (range: {WEAPON_SYSTEM_TYPES[u.ws1]['att_range']})")
            self.stdscr.addstr(info_y+10, info_x, f"[stats]: DMG: {WEAPON_SYSTEM_TYPES[u.ws1]['dmg_val']} (Arm. Pen. = {WEAPON_SYSTEM_TYPES[u.ws1]['arm_pen']})")
            self.stdscr.addstr(info_y+11, info_x, f"[ammo]: {u.display_ammo(u.ws1_ammo)}")
            self.stdscr.addstr(info_y+12, info_x, f" ")
            self.stdscr.addstr(info_y+13, info_x, f"[2. WPN]: {WEAPON_SYSTEM_TYPES[u.ws2]['name']} (range: {WEAPON_SYSTEM_TYPES[u.ws2]['att_range']})")             # tle naredi tko da če 2.wpn ne obstaja sploh ne izpisuj
            self.stdscr.addstr(info_y+14, info_x, f"[stats]: DMG: {WEAPON_SYSTEM_TYPES[u.ws2]['dmg_val']} (Arm. Pen. = {WEAPON_SYSTEM_TYPES[u.ws2]['arm_pen']})")
            self.stdscr.addstr(info_y+15, info_x, f"[ammo]: {u.display_ammo(u.ws2_ammo)}")
            self.stdscr.addstr(info_y+16, info_x, f"------------------------------------")
            self.stdscr.addstr(info_y+17, info_x, f"Moved: {u.moved}")
            self.stdscr.addstr(info_y+18, info_x, f"Acted: {u.acted}")
        else:
            self.stdscr.addstr(info_y+5, info_x, "Empty")

        # Selected unit info
        if self.selected:
            self.stdscr.addstr(info_y+19, info_x, f"Selected: {self.selected.name} at ({self.cursor_x},{self.cursor_y})")

        # Message
        self.stdscr.addstr(HEIGHT+3, 0, self.message[:curses.COLS-1])

        # Objectives
        ins_y = HEIGHT+5
        self.stdscr.addstr(ins_y, 0, "[OBJECTIVE]: eliminate enemy forces")
        self.stdscr.refresh()

        # Turn instructions
        ins_y = HEIGHT+8
        self.stdscr.addstr(ins_y, 0, "KEYBINDS: move cursor  Enter: select  m:move  a:attack  e:end turn  q:quit")
        self.stdscr.refresh()

    def select_unit(self):
        u = self.unit_at(self.cursor_x, self.cursor_y)
        if not u:
            self.message = "No unit here to select."
            return
        if u.owner != self.turn:
            self.message = "Cannot select enemy unit."
            return
        if u.moved and u.acted:
            self.message = "Unit already moved and acted this turn."
            return
        self.selected = u
        self.message = f"Selected unit at ({u.x},{u.y})."

    def deselect(self):
        self.selected = None
        self.message = "Deselected."

    def move_selected(self):
        if not self.selected:
            self.message = "No unit selected."
            return
        if self.selected.owner != self.turn:
            self.message = "Selected unit does not belong to you."
            return
        if self.selected.moved:
            self.message = "Selected unit already moved this turn."
            return
        dist = self.selected.distance_to(self.cursor_x, self.cursor_y)
        if dist > self.selected.move_range:
            self.message = f"Target too far (dist: {dist})."
            return
        if self.unit_at(self.cursor_x, self.cursor_y):
            self.message = "Target cell is occupied."
            return
        # perform move
        self.selected.x = self.cursor_x
        self.selected.y = self.cursor_y
        self.selected.moved = True
        self.message = f"Moved to ({self.cursor_x},{self.cursor_y})."


    # NEEDS MAJOF FIXING
    # funkcijo je treba prilagodit z novimi formulami za izračun napada:
    # upoštevat elevation, LOS, hit chance, armor pen, cover ...
    def attack_with_selected(self):
        if not self.selected:
            self.message = "No unit selected."
            return
        if self.selected.owner != self.turn:
            self.message = "Selected unit does not belong to you."
            return
        if self.selected.acted:
            self.message = "Selected unit already acted this turn."
            return
        target = self.unit_at(self.cursor_x, self.cursor_y)
        if not target or target.owner == self.selected.owner:
            self.message = "No enemy at target to attack."
            return
        dist = self.selected.distance_to(target.x, target.y)
        if dist > self.selected.att_range:
            self.message = "Target out of range!"
            return
        # perform attack
        dmg = random.randint(max(1,self.selected.atk-2), self.selected.atk+1)
        target.hp -= dmg
        self.selected.acted = True
        self.message = f"Attacked enemy for {dmg} dmg."
        if target.hp <= 0:
            self.message += " Enemy died!"

    # TREBA DODAT FUNKCIJO ZA LOS: concealment (+elevation) VS optics range


    def end_turn(self):
        # reset moved/acted flags for next player's units
        for u in self.units:
            if u.owner == self.turn:
                u.moved = False
                u.acted = False
        # swap turn
        self.turn = 2 if self.turn == 1 else 1
        self.selected = None
        self.message = f"Player {self.turn}'s turn."

    def check_victory(self):
        p1_alive = any(u.is_alive() and u.owner==1 for u in self.units)
        p2_alive = any(u.is_alive() and u.owner==2 for u in self.units)
        if not p1_alive:
            return 2
        if not p2_alive:
            return 1
        return None
    
        # ADD OBJECTIVES...

    def game_loop(self):
        curses.curs_set(0)
        self.stdscr.nodelay(False)
        self.stdscr.keypad(True)
        while True:
            self.draw()
            winner = self.check_victory()
            if winner:
                self.message = f"Player {winner} wins! Press q to quit or r to restart."
                self.draw()
                c = self.stdscr.getch()
                if c in (ord('q'), ord('Q')):
                    return
                if c in (ord('r'), ord('R')):
                    self.__init__(self.stdscr)
                    continue
                continue

            c = self.stdscr.getch()
            if c == curses.KEY_UP:
                self.cursor_y = max(0, self.cursor_y-1)
            elif c == curses.KEY_DOWN:
                self.cursor_y = min(HEIGHT-1, self.cursor_y+1)
            elif c == curses.KEY_LEFT:
                self.cursor_x = max(0, self.cursor_x-1)
            elif c == curses.KEY_RIGHT:
                self.cursor_x = min(WIDTH-1, self.cursor_x+1)
            elif c in (ord('\n'), ord(' ')):
                # select/deselect
                u = self.unit_at(self.cursor_x, self.cursor_y)
                if self.selected and self.selected.x == self.cursor_x and self.selected.y == self.cursor_y:
                    # toggle deselect
                    self.deselect()
                elif u and u.owner == self.turn:
                    self.select_unit()
                else:
                    self.message = "No friendly unit here to select."
            elif c in (ord('m'), ord('M')):
                self.move_selected()
            elif c in (ord('a'), ord('A')):
                self.attack_with_selected()
            elif c in (ord('e'), ord('E')):
                self.end_turn()
            elif c in (ord('q'), ord('Q')):
                return
            elif c in (ord('h'), ord('H')):
                self.message = "Hints: select your unit, move with m, attack adjacent enemy with a. End turn with e."
            else:
                # ignore
                pass

def load_map(filename):
    grid = []
    with open(filename, "r") as f:
        for line in f:
            row = list(line.rstrip("\n"))
            grid.append(row)
    return grid

def load_elev(filename):
    grid = []
    with open(filename, "r") as f:
        for line in f:
            row = (line.rstrip("\n")).split(",")
            grid.append(row)
    return grid

def main(stdscr):
    g = Game(stdscr)
    g.game_loop()

if __name__ == '__main__':

    map = load_map("map3.txt")
    #print(map)
    elev = load_elev("elevation2.txt")
    #print(elev)
    #print(elev[4][7])

    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print('\nGoodbye.')
        sys.exit(0)
