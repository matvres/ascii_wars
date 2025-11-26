#!/usr/bin/env python3
"""
ASCII Battle — Extended Version
Adds:
 - Pre-battle army-building menu
 - Point-buy system for units
 - Three unit types:
     * S — Soldier (melee, cheap)
     * R — Ranger (ranged attack, moderate cost)
     * F — Flyer (can ignore movement blocking and has higher mobility)

Controls and gameplay identical to previous version.
"""

import curses
import random
import sys

WIDTH = 12
HEIGHT = 8

COLOR_P1 = 1
COLOR_P2 = 2
COLOR_CURSOR = 3
COLOR_HIGHLIGHT = 4

# Unit definitions
UNIT_TYPES = {
    'S': { 'name': 'Soldier', 'cost': 5, 'hp': 10, 'atk': 4, 'move': 3, 'range': 1, 'flying': False },
    'R': { 'name': 'Ranger',  'cost': 8, 'hp': 8,  'atk': 3, 'move': 3, 'range': 3, 'flying': False },
    'F': { 'name': 'Flyer',   'cost': 10, 'hp': 7, 'atk': 4, 'move': 4, 'range': 1, 'flying': True },
}

ARMY_POINTS = 20
START_POSITIONS_P1 = [(1,1),(1,3),(1,5),(2,2),(2,4)]
START_POSITIONS_P2 = [(WIDTH-2,HEIGHT-2),(WIDTH-2,HEIGHT-4),(WIDTH-2,2),(WIDTH-3,3),(WIDTH-3,5)]

class Unit:
    def __init__(self, x, y, owner, kind):
        d = UNIT_TYPES[kind]
        self.x = x
        self.y = y
        self.owner = owner
        self.kind = kind
        self.max_hp = d['hp']
        self.hp = self.max_hp
        self.atk = d['atk']
        self.move_range = d['move']
        self.rng = d['range']
        self.flying = d['flying']
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
        self.message = "Welcome! Build your armies."

        self.init_colors()
        self.army_p1 = self.build_army(1)
        self.army_p2 = self.build_army(2)
        self.populate_units()

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_P1, curses.COLOR_RED, -1)
        curses.init_pair(COLOR_P2, curses.COLOR_BLUE, -1)
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, -1)

    def build_army(self, player):
        points = ARMY_POINTS
        army = []

        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"Player {player}: Build your army ({points} points left)")
            y = 2
            for k,v in UNIT_TYPES.items():
                self.stdscr.addstr(y, 0, f"[{k}] {v['name']} - {v['cost']} pts (HP:{v['hp']} ATK:{v['atk']} MV:{v['move']} RNG:{v['range']} {'FLY' if v['flying'] else ''})")
                y += 1
            self.stdscr.addstr(y+1, 0, "Press unit key to buy, ENTER when done.")
            self.stdscr.refresh()

            c = self.stdscr.getch()
            if c == curses.KEY_ENTER or c in (10,13):
                break

            ch = chr(c).upper()
            if ch in UNIT_TYPES:
                cost = UNIT_TYPES[ch]['cost']
                if cost <= points:
                    army.append(ch)
                    points -= cost
                else:
                    pass

        return army

    def populate_units(self):
        for (pos, kind) in zip(START_POSITIONS_P1, self.army_p1):
            x,y = pos
            self.units.append(Unit(x,y,1,kind))
        for (pos, kind) in zip(START_POSITIONS_P2, self.army_p2):
            x,y = pos
            # lowercase for player2 visuals
            self.units.append(Unit(x,y,2,kind.lower()))

    def unit_at(self, x, y):
        for u in self.units:
            if u.is_alive() and u.x == x and u.y == y:
                return u
        return None

    def draw(self):
        self.stdscr.clear()
        for y in range(HEIGHT+2):
            for x in range(WIDTH+2):
                ch = '-' if y in (0,HEIGHT+1) else ('|' if x in (0,WIDTH+1) else ' ')
                self.stdscr.addch(y, x, ch)

        for y in range(HEIGHT):
            for x in range(WIDTH):
                screen_x = x+1
                screen_y = y+1
                u = self.unit_at(x,y)
                if u:
                    attr = curses.color_pair(COLOR_P1 if u.owner==1 else COLOR_P2)
                    self.stdscr.addch(screen_y, screen_x, u.kind, attr)
                else:
                    self.stdscr.addch(screen_y, screen_x, '.')

        if self.selected:
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.selected.distance_to(x,y) <= self.selected.move_range:
                        if not self.unit_at(x,y) or self.selected.flying:
                            self.stdscr.addch(y+1,x+1,'+', curses.color_pair(COLOR_HIGHLIGHT))

        cx = self.cursor_x+1
        cy = self.cursor_y+1
        try:
            ch = chr(self.stdscr.inch(cy, cx) & 0xFF)
        except curses.error:
            ch = ' '
        self.stdscr.addch(cy, cx, ch, curses.color_pair(COLOR_CURSOR))

        info_y = 0; info_x = WIDTH + 4
        self.stdscr.addstr(info_y, info_x, f"Turn: Player {self.turn}")

        self.stdscr.addstr(HEIGHT+3, 0, self.message[:curses.COLS-1])
        self.stdscr.addstr(HEIGHT+5, 0, "Arrows:move  Enter:select  m:move  a:attack  e:end  q:quit")
        self.stdscr.refresh()

    def select_unit(self):
        u = self.unit_at(self.cursor_x, self.cursor_y)
        if not u or u.owner != self.turn:
            self.message = "No friendly unit."; return
        self.selected = u
        self.message = "Selected."

    def move_selected(self):
        if not self.selected: return
        u = self.selected
        dist = u.distance_to(self.cursor_x, self.cursor_y)
        if dist > u.move_range: self.message="Too far."; return
        if not u.flying and self.unit_at(self.cursor_x, self.cursor_y):
            self.message="Blocked."; return
        u.x = self.cursor_x; u.y = self.cursor_y
        u.moved = True
        self.message="Moved."

    def attack_with_selected(self):
        if not self.selected: return
        attacker = self.selected
        target = self.unit_at(self.cursor_x, self.cursor_y)
        if not target or target.owner == attacker.owner:
            self.message="No enemy."; return
        dist = attacker.distance_to(target.x, target.y)
        if dist > attacker.rng:
            self.message="Out of range."; return
        dmg = random.randint(max(1,attacker.atk-2), attacker.atk+1)
        target.hp -= dmg
        attacker.acted = True
        self.message = f"Hit for {dmg}."

    def end_turn(self):
        for u in self.units:
            if u.owner == self.turn:
                u.moved = False
                u.acted = False
        self.turn = 2 if self.turn==1 else 1
        self.selected = None
        self.message = f"Player {self.turn}'s turn."

    def check_victory(self):
        p1 = any(u.is_alive() and u.owner==1 for u in self.units)
        p2 = any(u.is_alive() and u.owner==2 for u in self.units)
        if not p1: return 2
        if not p2: return 1
        return None

    def game_loop(self):
        curses.curs_set(0)
        self.stdscr.nodelay(False)
        self.stdscr.keypad(True)
        while True:
            self.draw()
            w = self.check_victory()
            if w:
                self.stdscr.addstr(HEIGHT+7, 0, f"Player {w} wins! q=quit r=restart")
                c=self.stdscr.getch()
                if c in (ord('q'),ord('Q')): return
                if c in (ord('r'),ord('R')):
                    self.__init__(self.stdscr)
                continue

            c = self.stdscr.getch()
            if c == curses.KEY_UP: self.cursor_y=max(0,self.cursor_y-1)
            elif c == curses.KEY_DOWN: self.cursor_y=min(HEIGHT-1,self.cursor_y+1)
            elif c == curses.KEY_LEFT: self.cursor_x=max(0,self.cursor_x-1)
            elif c == curses.KEY_RIGHT: self.cursor_x=min(WIDTH-1,self.cursor_x+1)
            elif c in (10,13,ord(' ')): self.select_unit()
            elif c in (ord('m'),ord('M')): self.move_selected()
            elif c in (ord('a'),ord('A')): self.attack_with_selected()
            elif c in (ord('e'),ord('E')): self.end_turn()
            elif c in (ord('q'),ord('Q')): return


def main(stdscr):
    g = Game(stdscr)
    g.game_loop()

if __name__ == '__main__':
    curses.wrapper(main)
