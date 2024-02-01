#include <iostream>
#include <vector>
#include <string>
#include <ncurses/ncurses.h>
#include "game.hpp"
#include "globals.hpp"

int TER_HEIGHT;
int TER_WIDTH;

int main(){

    initscr();
    noecho();

    // Sets cursor to invisible
    curs_set(0);

    getmaxyx(stdscr, TER_HEIGHT, TER_WIDTH);

    if(!has_colors()){
        std::cerr << "Terminal does not support colors! ...exiting" << std::endl;
        return -1;
    }

    Game* game = new Game();
    delete game;

    endwin();

    return 0;
}