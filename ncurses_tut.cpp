#include <iostream>
#include <vector>
#include <string>
#include <ncurses/ncurses.h>

using namespace std;

int main(){

    int x {10};
    int y {10};

    int height {10};
    int width {20};
    int start_x {10};
    int start_y {10};

    string vnos {};


    // move cursor
    // move(y,x);

    // print to terminal window
    //printw("Hello world!");

    // združiš move in print
    //mvprintw(0,0,"Ane...");

    // refreshes memory screen
    // refresh();

    // clears screen
    // clear();

     // get input and wait
    // char c {getch()};

    // start ncurses
    initscr();

    // dodatne init funkcije
    // cbreak() ctrl+c omogoči exit iz ncurses programa
    // raw() podobno kot ctrl+c sam da tut izpiše pa ne izločuje special characterjev

    // attron()
    // attroff()
    /*
    A_NORMAL        Normal display (no highlight)
    A_STANDOUT      Best highlighting mode of the terminal.
    A_UNDERLINE     Underlining
    A_REVERSE       Reverse background and text color
    A_BLINK         Blinking
    A_DIM           Half bright
    A_BOLD          Extra bright or bold
    A_PROTECT       Protected mode
    A_INVIS         Invisible or blank mode
    A_ALTCHARSET    Alternate character set
    A_CHARTEXT      Bit-mask to extract a character
    COLOR_PAIR(n)   Color-pair number n 
    */

    if(!has_colors()){
        cerr << "Terminal does not support colors!" << endl;
        return -1;
    }

    // Window attributes (win, y in x moraš prej deklarirat)
    // getyx(win, y, x) vrne polozaj kurzorja za določen window
    // getbegyx(win, y, x) vrne koordinate zgornjega levega kota windowa
    // getmaxyx(win, y, x) vrne max koordinate okna

    // stdscr je osnovn window


    // Initializer for color usage
    start_color();
    init_pair(1, COLOR_WHITE, COLOR_GREEN);

    attron(COLOR_PAIR(1));
    printw("Barve yaay");
    attroff(COLOR_PAIR(1));

    getch();

    if(!can_change_color()){
        cerr << "Terminal can't change colors" << endl;
    }

    WINDOW* win = newwin(height, width, start_y, start_x);
    refresh();

    box(win,0,0);
    wattrset(win, COLOR_PAIR(1));    
    mvwprintw(win, 1,1,"Moj box");
    wattroff(win, COLOR_PAIR(1));
    wrefresh(win);

    getch();

    // end ncurses
    endwin();

    return 0;
}