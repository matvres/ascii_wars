#include "headers/multiplayer.hpp"
#include <ncurses/ncurses.h>
#include "headers/globals.hpp"

void Multiplayer::display_multiplayer(){
    
    // Create main window with border
    main_multi_win = newwin(TER_HEIGHT,TER_WIDTH,0,0);
    refresh();
    box(main_multi_win,0,0);

    // Print title to window    
    mvwprintw(main_multi_win,2,2,"Not yet implemented... ");
    wattron(main_multi_win, A_REVERSE);
    mvwprintw(main_multi_win,TER_HEIGHT-3,TER_WIDTH/2-2,"Back");
    wattroff(main_multi_win, A_REVERSE);
    wrefresh(main_multi_win);

    while(getch() != 10){
        //TODO...
    }

    delwin(main_multi_win);
}

Multiplayer::Multiplayer(){

}

Multiplayer::~Multiplayer(){

}