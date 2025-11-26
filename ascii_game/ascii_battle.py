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
WIDTH = 30
HEIGHT = 15

# Colors (indices for curses)
COLOR_P1 = 1
COLOR_P2 = 2
COLOR_CURSOR = 3
COLOR_HIGHLIGHT = 4

# Terrain color indices
COLOR_GRASS = 5
COLOR_FOREST = 6
COLOR_WALL = 7

# Unit definitions
UNIT_TYPES = {
    'S': { 'name': 'Soldier', 'cost': 5, 'hp': 10, 'atk': 4, 'move': 3, 'range': 2, 'flying': False },
    'R': { 'name': 'Ranger',  'cost': 8, 'hp': 8,  'atk': 3, 'move': 3, 'range': 4, 'flying': False },
    'F': { 'name': 'Flyer',   'cost': 10, 'hp': 7, 'atk': 4, 'move': 4, 'range': 3, 'flying': True },
}

# Terrain definitions
TERRAIN_TYPES = {
    '.': { 'name': 'grass',  'mov_cost': 1, 'pass': True },
    'f': { 'name': 'forest', 'mov_cost': 1, 'pass': True },
    'x': { 'name': 'wall',   'mov_cost': 0, 'pass': False },
}

# Army starting positions
START_POSITIONS_P1 = [(1,1),(1,3),(1,5),(2,2),(2,4)]
START_POSITIONS_P2 = [(WIDTH-2,HEIGHT-2),(WIDTH-2,HEIGHT-4),(WIDTH-2,2),(WIDTH-3,3),(WIDTH-3,5)]

ARMY_P1 = ["F","S","S","R","R"]
ARMY_P2 = ["S","F","F","S","S"]


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
        self.atk = un['atk']
        self.move_range = un['move']
        self.att_range = un['range']
        self.flying = un['flying']
        self.moved = False
        self.acted = False

    def is_alive(self):
        return self.hp > 0

    def distance_to(self, x, y):
        return abs(self.x - x) + abs(self.y - y)

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
        curses.init_pair(COLOR_P1, 9, -1)
        curses.init_pair(COLOR_P2, 14, -1)
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, -1)

        # Terrain colors
        curses.init_pair(COLOR_GRASS, 113, 113)
        curses.init_pair(COLOR_FOREST, 22, 76)
        curses.init_pair(COLOR_WALL, 58, 113)


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

        # Draw grid and units
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
                    if map[y][x] == '.':
                        attr = curses.color_pair(COLOR_GRASS)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == 'f':
                        attr = curses.color_pair(COLOR_FOREST)
                        self.stdscr.addch(screen_y, screen_x, map[y][x], attr)
                    elif map[y][x] == 'x':
                        attr = curses.color_pair(COLOR_WALL)
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
                                self.stdscr.addch(sy,sx,'+', curses.color_pair(COLOR_HIGHLIGHT))
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
        self.stdscr.addstr(info_y+2, info_x, f"---------------------------------")
        u = self.unit_at(self.cursor_x, self.cursor_y)
        if u:
            self.stdscr.addstr(info_y+3, info_x, f"Unit: {'P1' if u.owner==1 else 'P2'} {u.kind} ({u.name})")
            self.stdscr.addstr(info_y+4, info_x, f"HP: {u.hp}/{u.max_hp}")
            self.stdscr.addstr(info_y+5, info_x, f"ATK: {u.atk}")
            self.stdscr.addstr(info_y+6, info_x, f"MOV: {u.move_range}")
            self.stdscr.addstr(info_y+7, info_x, f"Moved: {u.moved}")
            self.stdscr.addstr(info_y+8, info_x, f"Acted: {u.acted}")
        else:
            self.stdscr.addstr(info_y+3, info_x, "Empty")

        # Selected unit info
        if self.selected:
            self.stdscr.addstr(info_y+8, info_x, f"Selected: {'P1' if self.selected.owner==1 else 'P2'} {self.selected.kind} ({self.selected.hp}HP)")

        # Message
        self.stdscr.addstr(HEIGHT+3, 0, self.message[:curses.COLS-1])

        # Turn instructions
        ins_y = HEIGHT+5
        self.stdscr.addstr(ins_y, 0, "Arrows: move cursor  Enter: select  m:move  a:attack  e:end turn  q:quit")
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

def main(stdscr):
    g = Game(stdscr)
    g.game_loop()

if __name__ == '__main__':

    map = load_map("map.txt")
    #print(map)

    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print('\nGoodbye.')
        sys.exit(0)
