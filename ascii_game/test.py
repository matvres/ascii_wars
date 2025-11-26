#!/usr/bin/env python3
"""
ASCII Battle — Terrain Edition
Adds:
 - Three terrain types: grass (.), forest (f), wall (H)
 - Movement costs: . = 1, f = 2, H = impassable (unless flying)
 - Forest gives defense bonus
 - Walls block line of sight
 - Terrain colored: grass=green, forest=dark green, wall=gray
"""

import curses
import random
import sys

WIDTH = 16
HEIGHT = 10

# Colors
COLOR_P1 = 1
COLOR_P2 = 2
COLOR_CURSOR = 3
COLOR_HIGHLIGHT = 4
COLOR_GRASS = 5
COLOR_FOREST = 6
COLOR_WALL = 7

UNIT_TYPES = {
    'S': { 'hp':10, 'atk':4, 'move':3, 'range':2, 'flying':False },
    'R': { 'hp': 8, 'atk':3, 'move':3, 'range':4, 'flying':False },
    'F': { 'hp': 7, 'atk':4, 'move':4, 'range':3, 'flying':True },
}

TERRAIN = {
    '.': { 'cost':1, 'def':0,  'block':False },
    'f': { 'cost':2, 'def':1,  'block':False },
    'H': { 'cost':999, 'def':0,'block':True },
}

ARMY_P1 = ["F","S","S","R","R"]
ARMY_P2 = ["S","F","F","S","S"]

START_POSITIONS_P1 = [(1,1),(1,3),(1,5),(2,2),(2,4)]
START_POSITIONS_P2 = [(WIDTH-2,HEIGHT-2),(WIDTH-2,HEIGHT-4),(WIDTH-2,2),(WIDTH-3,3),(WIDTH-3,5)]

class Unit:
    def __init__(self,x,y,owner,kind):
        un = UNIT_TYPES[kind]
        self.x=x; self.y=y
        self.owner=owner
        self.kind=kind
        self.max_hp=un['hp']; self.hp=self.max_hp
        self.atk=un['atk']
        self.move_range=un['move']
        self.att_range=un['range']
        self.flying=un['flying']
        self.moved=False; self.acted=False

    def is_alive(self): return self.hp>0

    def distance_to(self,x,y): return abs(self.x-x)+abs(self.y-y)

class Game:
    def __init__(self, stdscr):
        self.stdscr=stdscr
        self.cursor_x=0; self.cursor_y=0
        self.turn=1
        self.units=[]
        self.selected=None
        self.message="Terrain test!"

        self.init_colors()
        self.terrain=self.generate_terrain()
        self.populate_units()

    def init_colors(self):
        curses.start_color(); curses.use_default_colors()
        curses.init_pair(COLOR_P1, curses.COLOR_RED, -1)
        curses.init_pair(COLOR_P2, curses.COLOR_BLUE, -1)
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, -1)
        curses.init_pair(COLOR_GRASS, curses.COLOR_GREEN, -1)
        curses.init_pair(COLOR_FOREST, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(COLOR_WALL, curses.COLOR_WHITE, curses.COLOR_BLACK)

    # -------- Terrain Generation --------
    def generate_terrain(self):
        grid=[[ '.' for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r=random.random()
                if r<0.1: grid[y][x]='H'
                elif r<0.25: grid[y][x]='f'
        return grid

    def populate_units(self):
        i=0
        for x,y in START_POSITIONS_P1:
            self.units.append(Unit(x,y,1,ARMY_P1[i])); i+=1
        i=0
        for x,y in START_POSITIONS_P2:
            self.units.append(Unit(x,y,2,ARMY_P2[i])); i+=1

    def unit_at(self,x,y):
        for u in self.units:
            if u.is_alive() and u.x==x and u.y==y: return u
        return None

    # -------- LOS (line of sight) --------
    def has_los(self, x1,y1,x2,y2):
        dx=x2-x1; dy=y2-y1
        steps=max(abs(dx),abs(dy))
        if steps==0: return True
        sx=dx/steps; sy=dy/steps
        cx,cy=x1,y1
        for _ in range(steps):
            cx+=sx; cy+=sy
            tx=int(round(cx)); ty=int(round(cy))
            if (tx,ty)==(x2,y2): return True
            if 0<=tx<WIDTH and 0<=ty<HEIGHT:
                if TERRAIN[self.terrain[ty][tx]]['block']:
                    return False
        return True

    # -------- Drawing --------
    def draw(self):
        self.stdscr.clear()
        for y in range(HEIGHT+2):
            for x in range(WIDTH+2):
                ch='-' if y in (0,HEIGHT+1) else ('|' if x in (0,WIDTH+1) else ' ')
                self.stdscr.addch(y,x,ch)

        # Terrain
        for y in range(HEIGHT):
            for x in range(WIDTH):
                tile=self.terrain[y][x]
                scr_x=x+1; scr_y=y+1
                if tile=='.': attr=curses.color_pair(COLOR_GRASS)
                elif tile=='f': attr=curses.color_pair(COLOR_FOREST)
                elif tile=='H': attr=curses.color_pair(COLOR_WALL)
                self.stdscr.addch(scr_y,scr_x,tile,attr)

        # Units on top
        for u in self.units:
            if not u.is_alive(): continue
            x,y=u.x,u.y
            attr=curses.color_pair(COLOR_P1 if u.owner==1 else COLOR_P2)
            self.stdscr.addch(y+1,x+1,u.kind,attr)

        # Movement highlights
        if self.selected:
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.can_move_to(self.selected,x,y):
                        self.stdscr.addch(y+1,x+1,'+',curses.color_pair(COLOR_HIGHLIGHT))

        # Cursor
        cx=self.cursor_x+1; cy=self.cursor_y+1
        try: ch=chr(self.stdscr.inch(cy,cx)&0xFF)
        except: ch=' '
        self.stdscr.addch(cy,cx,ch,curses.color_pair(COLOR_CURSOR))

        self.stdscr.addstr(HEIGHT+3,0,self.message)
        self.stdscr.refresh()

    # -------- Movement Rules --------
    def can_move_to(self,u,x,y):
        if u.flying:
            return u.distance_to(x,y)<=u.move_range
        if self.unit_at(x,y): return False
        tile=self.terrain[y][x]
        cost=TERRAIN[tile]['cost']
        return u.distance_to(x,y)*cost <= u.move_range

    def move_selected(self):
        if not self.selected: return
        u=self.selected
        x,y=self.cursor_x,self.cursor_y
        if self.can_move_to(u,x,y):
            u.x=x; u.y=y; u.moved=True; self.message="Moved."
        else:
            self.message="Cannot move there."

    def attack_with_selected(self):
        if not self.selected: return
        attacker=self.selected
        target=self.unit_at(self.cursor_x,self.cursor_y)
        if not target or target.owner==attacker.owner:
            self.message="No enemy."; return
        if attacker.distance_to(target.x,target.y)>attacker.att_range:
            self.message="Out of range."; return
        if not self.has_los(attacker.x,attacker.y,target.x,target.y):
            self.message="No LOS!"; return
        dmg=random.randint(attacker.atk-1,attacker.atk+1)
        tile=self.terrain[target.y][target.x]
        dmg-=TERRAIN[tile]['def']
        dmg=max(1,dmg)
        target.hp-=dmg
        attacker.acted=True
        self.message=f"Hit for {dmg}."

    # -------- Turn Logic --------
    def select_unit(self):
        u=self.unit_at(self.cursor_x,self.cursor_y)
        if not u or u.owner!=self.turn:
            self.message="No friendly unit."; return
        self.selected=u; self.message="Selected."

    def end_turn(self):
        for u in self.units:
            if u.owner==self.turn:
                u.moved=False; u.acted=False
        self.turn=2 if self.turn==1 else 1
        self.selected=None
        self.message=f"Player {self.turn}'s turn."

    def check_victory(self):
        p1=any(u.is_alive() and u.owner==1 for u in self.units)
        p2=any(u.is_alive() and u.owner==2 for u in self.units)
        if not p1: return 2
        if not p2: return 1
        return None

    def game_loop(self):
        curses.curs_set(0)
        self.stdscr.nodelay(False); self.stdscr.keypad(True)

        while True:
            self.draw()
            w=self.check_victory()
            if w:
                self.message=f"Player {w} wins! q quits."
                self.draw()
                c=self.stdscr.getch()
                if c in (ord('q'),ord('Q')): return

            c=self.stdscr.getch()
            if c==curses.KEY_UP: self.cursor_y=max(0,self.cursor_y-1)
            elif c==curses.KEY_DOWN: self.cursor_y=min(HEIGHT-1,self.cursor_y+1)
            elif c==curses.KEY_LEFT: self.cursor_x=max(0,self.cursor_x-1)
            elif c==curses.KEY_RIGHT:self.cursor_x=min(WIDTH-1,self.cursor_x+1)
            elif c in (10,13,ord(' ')): self.select_unit()
            elif c in (ord('m'),ord('M')): self.move_selected()
            elif c in (ord('a'),ord('A')): self.attack_with_selected()
            elif c in (ord('e'),ord('E')): self.end_turn()
            elif c in (ord('q'),ord('Q')): return


def main(stdscr):
    Game(stdscr).game_loop()

if __name__=='__main__': curses.wrapper(main)
