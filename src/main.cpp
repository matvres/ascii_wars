#include <iostream>
#include <vector>
#include <string>
#include <ncurses/ncurses.h>
#include "headers/game.hpp"
#include "headers/globals.hpp"

// Debug related
int A {};
int B {};
int C {};
int D {};
int E {};
//----------------

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

    start_color();
    init_pair(1, COLOR_RED, COLOR_WHITE); // ASCII WARS main menu title
    init_pair(2, COLOR_GREEN, COLOR_BLACK);
    init_pair(3, COLOR_CYAN, COLOR_BLACK);
    init_pair(4, COLOR_RED, COLOR_BLACK);
    init_pair(5, COLOR_WHITE, COLOR_GREEN);

    Game* game = new Game();
    game->game_loop();
    delete game;

    endwin();

    return 0;
}