"""
ASCII-Warrior: Turn-based 2-player hot-seat strategy game using curses

Features:
- Loads map from `map.txt` (editable): characters G=grass, F=forest, R=road
- Loads elevation from `elevation.txt` (CSV grid matching map size), values -10..10
- Left panel: selected unit info and stats
- Right panel: action log
- Bottom toolbar: keybinds display
- Supports 3 unit types per side: melee, ranged, flyer
- Terrain affects movement & line-of-sight. Elevation influences sight and is drawn with different backgrounds.
- Units have atk, def, move, sight/range, HP.

How to use:
- Run: python3 ascii_warrior.py
- Keys: arrow keys move cursor, Enter select/deselect unit, m move, a attack, e end turn, q quit

This single-file script will create example `map.txt` and `elevation.txt` if they are missing.
"""

import curses
import os
import sys
import textwrap
from collections import deque

MAP_FILE = 'map.txt'
ELEV_FILE = 'elevation.txt'

# Sample map & elevation written if not present
SAMPLE_MAP = """
GGGGGGGGGGGGGG
GGRGGFFGGGGRGG
GGGGGFGGGGGGGG
GGRGGGGGGGRGGG
GGGFFFFGGGGGGG
GGGGGGGGGGGGGG
""".strip()

SAMPLE_ELEV = """
0,0,0,1,1,1,1,1,1,0,0,0,0
0,0,1,1,2,2,2,1,1,1,0,0,0
0,0,0,1,1,2,1,1,1,0,0,0,0
0,0,1,1,2,3,2,1,1,1,0,0,0
0,0,0,0,1,2,2,1,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0
""".strip()

# Terrain config
TERRAINS = {
    'G': {'name': 'Grass',  'move_cost': 1, 'sight_modifier': 0, 'char': '.'},
    'F': {'name': 'Forest', 'move_cost': 2, 'sight_modifier': -1, 'char': 'T'},
    'R': {'name': 'Road',   'move_cost': 1, 'sight_modifier': 0, 'char': '='},
}

# Unit templates
UNIT_TYPES = {
    'melee': {'hp': 12, 'atk': 6, 'def': 3, 'move': 3, 'range': 1, 'sight': 3, 'char': 'M'},
    'ranged':{'hp': 9, 'atk': 5, 'def': 2, 'move': 2, 'range': 4, 'sight': 5, 'char': 'R'},
    'flyer': {'hp': 10,'atk': 5, 'def': 2, 'move': 4, 'range': 1, 'sight': 4, 'char': 'V'},
}

# Map reading / writing helpers

def ensure_sample_files():
    if not os.path.exists(MAP_FILE):
        with open(MAP_FILE, 'w') as f:
            f.write(SAMPLE_MAP)
    if not os.path.exists(ELEV_FILE):
        with open(ELEV_FILE, 'w') as f:
            f.write(SAMPLE_ELEV)


def load_map():
    with open(MAP_FILE, 'r') as f:
        lines = [line.rstrip('\n') for line in f if line.strip('\n')!='']
    grid = [list(line) for line in lines]
    return grid


def load_elevation():
    with open(ELEV_FILE, 'r') as f:
        lines = [line.strip() for line in f if line.strip()!='']
    grid = [list(map(int, line.split(','))) for line in lines]
    return grid

# Game objects
class Unit:
    def __init__(self, team, utype, y, x, id_):
        self.team = team  # 0 or 1
        self.type = utype
        tmpl = UNIT_TYPES[utype]
        self.max_hp = tmpl['hp']
        self.hp = tmpl['hp']
        self.atk = tmpl['atk']
        self.defense = tmpl['def']
        self.move = tmpl['move']
        self.range = tmpl['range']
        self.sight = tmpl['sight']
        self.char = tmpl['char']
        self.y = y
        self.x = x
        self.id = id_
        self.moved = False
        self.attacked = False

    def reset_turn(self):
        self.moved = False
        self.attacked = False

    def is_alive(self):
        return self.hp>0

# Utility functions

def in_bounds(y,x, h, w):
    return 0<=y<h and 0<=x<w


def manhattan(a,b):
    return abs(a[0]-b[0])+abs(a[1]-b[1])

# Game class
class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        ensure_sample_files()
        self.map = load_map()
        self.elev = load_elevation()
        self.h = len(self.map)
        self.w = len(self.map[0])
        # Check dims
        if len(self.elev)!=self.h or any(len(row)!=self.w for row in self.elev):
            raise ValueError('Elevation grid size must match map size!')

        # UI layout sizes
        self.map_win_h = self.h
        self.map_win_w = self.w  # draw two chars per tile for clarity
        self.left_w = 28
        self.right_w = 36
        self.bottom_h = 3

        # Colors
        curses.start_color()
        curses.use_default_colors()
        # define color pairs for elevation levels (5 levels)
        # use background colors where possible
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # unit colors
        curses.init_pair(10, curses.COLOR_WHITE, -1)  # default
        curses.init_pair(11, curses.COLOR_RED, -1)    # team 0
        curses.init_pair(12, curses.COLOR_BLUE, -1)   # team 1
        curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_RED) # selection
        curses.init_pair(14, curses.COLOR_BLACK, curses.COLOR_YELLOW) # cursor

        # Terrain levels (COLORS):
        # G     : 118
        # G+1   : 112
        # G+2   : 106
        # G+3   : 100
        # G+4   : 94

        # Create units
        self.units = []
        self.create_starting_units()
        self.selected_unit = None
        self.cursor_y = 0
        self.cursor_x = 0
        self.turn = 0  # 0 or 1
        self.turn_num = 1
        self.log = []

        # Precompute elevation levels mapping -10..10 to 1..5
        self.elev_level = [[self.elev_to_level(v) for v in row] for row in self.elev]

    def elev_to_level(self, v):
        # clamp -10..10
        v = max(-10, min(10, v))
        # map to 0..4 then +1
        idx = int((v+10)/21*5)
        if idx<0: idx=0
        if idx>4: idx=4
        return idx+1

    def create_starting_units(self):
        # Place 3 units for each team. Team 0 top-left, Team1 bottom-right
        placements = [
            (0,'melee', 0,1), (0,'ranged',1,2), (0,'flyer',0,3),
            (1,'melee', self.h-1,self.w-2), (1,'ranged', self.h-2,self.w-3), (1,'flyer', self.h-1,self.w-4),
        ]
        idc = 1
        for team,ut,y,x in placements:
            u = Unit(team, ut, y, x, idc)
            self.units.append(u)
            idc+=1

    def unit_at(self,y,x):
        for u in self.units:
            if u.is_alive() and u.y==y and u.x==x:
                return u
        return None

    def draw(self):
        self.stdscr.clear()
        maxy, maxx = self.stdscr.getmaxyx()
        needed_w = self.left_w + self.map_win_w + self.right_w
        needed_h = self.map_win_h + self.bottom_h
        if maxy<needed_h or maxx<needed_w:
            self.stdscr.addstr(0,0,"Terminal too small. Need {}x{}".format(needed_h, needed_w))
            self.stdscr.refresh()
            return

        # Draw map window at (0, left_w)
        for y in range(self.h):
            for x in range(self.w):
                ch = TERRAINS.get(self.map[y][x], {'char':'?'})['char']
                level = self.elev_level[y][x]
                color = curses.color_pair(level)
                # draw two-character wide tile
                sy = y
                sx = self.left_w + x*2
                attr = color
                # highlight cursor
                if y==self.cursor_y and x==self.cursor_x:
                    attr |= curses.color_pair(14)
                self.stdscr.addstr(sy, sx, ch*2, attr)

        # Draw units
        for u in self.units:
            if not u.is_alive():
                continue
            sy = u.y
            sx = self.left_w + u.x*2
            pair = curses.color_pair(11 if u.team==0 else 12)
            if self.selected_unit and self.selected_unit==u:
                # selection highlight
                self.stdscr.addstr(sy, sx, u.char*2, curses.color_pair(13))
            else:
                self.stdscr.addstr(sy, sx, u.char*2, pair | curses.A_BOLD)

        # Left panel
        lx = 0
        ly = 0
        self.stdscr.addstr(ly, lx, " UNIT INFO ".center(self.left_w,'='))
        ly +=1
        if self.selected_unit:
            u = self.selected_unit
            lines = [
                f"Team: {'A' if u.team==0 else 'B'}",
                f"Type: {u.type}",
                f"HP: {u.hp}/{u.max_hp}",
                f"ATK: {u.atk}",
                f"DEF: {u.defense}",
                f"MOVE: {u.move}  RANGE: {u.range}",
                f"SIGHT: {u.sight}",
                f"Pos: ({u.y},{u.x})",
                f"Moved: {'Yes' if u.moved else 'No'} Attacked: {'Yes' if u.attacked else 'No'}",
            ]
            for line in lines:
                self.stdscr.addstr(ly, lx, line.ljust(self.left_w))
                ly+=1
        else:
            self.stdscr.addstr(ly, lx, '(no unit selected)'.ljust(self.left_w))
            ly+=1

        # Turn header
        self.stdscr.addstr(self.map_win_h - 2, 0, (' TURN {} - Player {}'.format(self.turn_num, 'A' if self.turn==0 else 'B')).ljust(self.left_w))

        # Right log panel
        rx = self.left_w + self.map_win_w
        ry = 0
        self.stdscr.addstr(ry, rx, " ACTION LOG ".center(self.right_w,'='))
        ry+=1
        # show last few log lines
        max_log_lines = self.map_win_h - 2
        recent = self.log[-max_log_lines:]
        for line in recent:
            self.stdscr.addstr(ry, rx, line[:self.right_w].ljust(self.right_w))
            ry+=1

        # Bottom toolbar
        by = self.map_win_h
        toolbar = "Arrows: Move cursor  Enter: Select  m:Move  a:Attack  e:End turn  q:Quit"
        self.stdscr.addstr(by, 0, toolbar.ljust(needed_w))

        # Help for selected or active unit
        if self.selected_unit:
            hint = "Press m to show possible moves, a to attack an enemy in range."
            self.stdscr.addstr(by+1, 0, hint.ljust(needed_w))

        self.stdscr.refresh()

    def add_log(self, text):
        self.log.append(text)
        # keep log reasonable length
        if len(self.log)>200:
            self.log = self.log[-200:]

    def select_unit(self, y, x):
        u = self.unit_at(y,x)
        if u and u.team==self.turn and u.is_alive():
            self.selected_unit = u
            self.add_log(f"Selected unit {u.char}{u.id} (Team {'A' if u.team==0 else 'B'}) at ({y},{x})")
        else:
            self.selected_unit = None

    def end_turn(self):
        self.add_log(f"End of Player {'A' if self.turn==0 else 'B'} turn.")
        # reset units of other team? Actually reset all units' moved/attacked for next player's turn
        for u in self.units:
            if u.team==self.turn:
                # units that belonged to this player already moved are kept, but on their next turn they should be reset
                pass
        # switch turn
        self.turn = 1 - self.turn
        self.turn_num += 1
        # reset all units of new current team
        for u in self.units:
            if u.team==self.turn and u.is_alive():
                u.reset_turn()
        self.selected_unit = None

    def compute_move_range(self, unit):
        # BFS accumulating movement cost. Flyers ignore terrain costs and elevation.
        h,w = self.h, self.w
        max_move = unit.move
        visited = [[None]*w for _ in range(h)]
        q = deque()
        q.append((unit.y, unit.x, 0))
        visited[unit.y][unit.x]=0
        while q:
            y,x,cost = q.popleft()
            for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny,nx = y+dy, x+dx
                if not in_bounds(ny,nx,h,w): continue
                if unit.type!='flyer':
                    t = self.map[ny][nx]
                    tc = TERRAINS.get(t,{'move_cost':1})['move_cost']
                else:
                    tc = 1  # flyers treat everything as cost 1
                newcost = cost + tc
                # cannot move into a tile occupied by own unit
                other = self.unit_at(ny,nx)
                if other and other.team==unit.team and other.is_alive():
                    continue
                if newcost<=max_move and (visited[ny][nx] is None or newcost<visited[ny][nx]):
                    visited[ny][nx]=newcost
                    q.append((ny,nx,newcost))
        # return list of reachable coords (excluding start)
        res = [(y,x) for y in range(h) for x in range(w) if visited[y][x] is not None and not (y==unit.y and x==unit.x)]
        return res

    def compute_attackable(self, unit):
        # simple distance-based (manhattan) attack range; flyers may attack at same range
        res = []
        for o in self.units:
            if o.team!=unit.team and o.is_alive():
                d = manhattan((unit.y,unit.x),(o.y,o.x))
                # line of sight: reduce effective sight by terrain between? We'll approximate by counting forest tiles in straight path
                sight = unit.sight
                # reduce by elevation difference
                elev_diff = abs(self.elev[unit.y][unit.x] - self.elev[o.y][o.x])
                sight -= max(0, elev_diff//3)
                # count forests along approximate path (simple Bresenham not implemented) -> approximate via straight axis
                forests = 0
                if unit.y==o.y:
                    for x in range(min(unit.x,o.x), max(unit.x,o.x)+1):
                        if self.map[unit.y][x]=='F': forests+=1
                elif unit.x==o.x:
                    for y in range(min(unit.y,o.y), max(unit.y,o.y)+1):
                        if self.map[y][unit.x]=='F': forests+=1
                else:
                    # for diagonal-ish, sample a few intermediate tiles
                    steps = max(abs(unit.y-o.y), abs(unit.x-o.x))
                    for i in range(steps+1):
                        ty = int(round(unit.y + (o.y-unit.y)*i/steps))
                        tx = int(round(unit.x + (o.x-unit.x)*i/steps))
                        if self.map[ty][tx]=='F': forests+=1

                sight -= forests
                # ensure at least 0
                if sight<0: sight=0
                # effective range is unit.range for attack, sight limits if relevant
                if d<=unit.range and d<=sight:
                    res.append(o)
        return res

    def move_unit(self, unit, to_y, to_x):
        # simple move (assume reachable checked before)
        other = self.unit_at(to_y,to_x)
        if other and other.team!=unit.team:
            self.add_log('Cannot move onto enemy unit.')
            return False
        unit.y = to_y
        unit.x = to_x
        unit.moved = True
        self.add_log(f"Unit {unit.char}{unit.id} moved to ({to_y},{to_x})")
        return True

    def attack(self, attacker, defender):
        # simple damage formula
        dmg = max(1, attacker.atk - defender.defense)
        defender.hp -= dmg
        attacker.attacked = True
        self.add_log(f"{attacker.char}{attacker.id} attacked {defender.char}{defender.id} for {dmg} dmg")
        if defender.hp<=0:
            defender.hp=0
            self.add_log(f"{defender.char}{defender.id} was defeated!")

    def handle_input(self, ch):
        if ch in (curses.KEY_UP, ord('k')):
            self.cursor_y = max(0, self.cursor_y-1)
        elif ch in (curses.KEY_DOWN, ord('j')):
            self.cursor_y = min(self.h-1, self.cursor_y+1)
        elif ch in (curses.KEY_LEFT, ord('h')):
            self.cursor_x = max(0, self.cursor_x-1)
        elif ch in (curses.KEY_RIGHT, ord('l')):
            self.cursor_x = min(self.w-1, self.cursor_x+1)
        elif ch == ord('\n') or ch==10 or ch==13:
            # select/deselect
            self.select_unit(self.cursor_y, self.cursor_x)
        elif ch==ord('q'):
            self.quit()
        elif ch==ord('e'):
            self.end_turn()
        elif ch==ord('m'):
            if not self.selected_unit:
                self.add_log('No unit selected to move.')
                return
            if self.selected_unit.team!=self.turn:
                self.add_log('Selected unit not on your team.')
                return
            if self.selected_unit.moved:
                self.add_log('Selected unit already moved this turn.')
                return
            reachable = self.compute_move_range(self.selected_unit)
            if not reachable:
                self.add_log('No reachable tiles to move.')
                return
            # show reachable tiles on map and let player pick target tile via moving cursor
            self.add_log('Showing reachable tiles - move cursor and press Enter to move, Esc to cancel')
            self.draw_reachable_and_choose(reachable)
        elif ch==ord('a'):
            if not self.selected_unit:
                self.add_log('No unit selected to attack with.')
                return
            if self.selected_unit.attacked:
                self.add_log('Selected unit already attacked this turn.')
                return
            targets = self.compute_attackable(self.selected_unit)
            if not targets:
                self.add_log('No enemies in range or line of sight.')
                return
            # choose a target under cursor or cycle
            # if cursor on an enemy in targets, attack that
            for t in targets:
                if t.y==self.cursor_y and t.x==self.cursor_x:
                    self.attack(self.selected_unit, t)
                    return
            # else pick first
            self.attack(self.selected_unit, targets[0])
        # other ignored

    def draw_reachable_and_choose(self, reachable):
        # highlight reachable and interact until Enter on reachable or Esc to cancel
        reachable_set = set(reachable)
        while True:
            # draw map with reachable highlighted
            self.stdscr.clear()
            for y in range(self.h):
                for x in range(self.w):
                    ch = TERRAINS.get(self.map[y][x], {'char':'?'})['char']
                    level = self.elev_level[y][x]
                    color = curses.color_pair(level)
                    sy = y
                    sx = self.left_w + x*2
                    attr = color
                    if (y,x) in reachable_set:
                        attr |= curses.A_REVERSE
                    if y==self.cursor_y and x==self.cursor_x:
                        attr |= curses.color_pair(14)
                    self.stdscr.addstr(sy, sx, ch*2, attr)
            # redraw units
            for u in self.units:
                if not u.is_alive(): continue
                sy = u.y
                sx = self.left_w + u.x*2
                pair = curses.color_pair(11 if u.team==0 else 12)
                self.stdscr.addstr(sy, sx, u.char*2, pair | curses.A_BOLD)
            # left/right panels and bottom toolbar minimal while choosing
            self.stdscr.addstr(self.map_win_h, 0, 'Move mode: Enter to move, Esc to cancel'.ljust(self.left_w + self.map_win_w + self.right_w))
            self.stdscr.refresh()
            ch = self.stdscr.getch()
            if ch in (curses.KEY_UP, ord('k')):
                self.cursor_y = max(0, self.cursor_y-1)
            elif ch in (curses.KEY_DOWN, ord('j')):
                self.cursor_y = min(self.h-1, self.cursor_y+1)
            elif ch in (curses.KEY_LEFT, ord('h')):
                self.cursor_x = max(0, self.cursor_x-1)
            elif ch in (curses.KEY_RIGHT, ord('l')):
                self.cursor_x = min(self.w-1, self.cursor_x+1)
            elif ch==27:  # Esc
                self.add_log('Move cancelled.')
                return
            elif ch==ord('\n') or ch==10 or ch==13:
                if (self.cursor_y, self.cursor_x) in reachable_set:
                    self.move_unit(self.selected_unit, self.cursor_y, self.cursor_x)
                else:
                    self.add_log('Destination not reachable.')
                return

    def quit(self):
        curses.endwin()
        print('Goodbye!')
        sys.exit(0)

    def game_loop(self):
        # initial reset of team 0 units
        for u in self.units:
            if u.team==self.turn:
                u.reset_turn()
        while True:
            self.draw()
            ch = self.stdscr.getch()
            self.handle_input(ch)


def main(stdscr):
    curses.curs_set(0)
    g = Game(stdscr)
    g.add_log('Game started. Player A begins.')
    g.game_loop()

if __name__=='__main__':
    try:
        curses.wrapper(main)
    except Exception as e:
        print('Error:', e)
        raise
