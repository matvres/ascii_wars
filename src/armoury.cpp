#include <ncurses/ncurses.h>
#include <vector>
#include <string>
#include "headers/armoury.hpp"
#include "headers/globals.hpp"

Armoury::Armoury(){

}

Armoury::~Armoury(){

}

void Armoury::display_armoury(){

    clear();

    // Create main window with border
    main_armoury_win = newwin(TER_HEIGHT,TER_WIDTH,0,0);
    refresh();
    box(main_armoury_win,0,0);
    wrefresh(main_armoury_win);

    // Create decks pane with border
    decks_pane = newwin(TER_HEIGHT/4,TER_WIDTH/2,2,2);
    refresh();
    box(decks_pane,0,0);
    mvwprintw(decks_pane,0,4,"DECKS");
    wrefresh(decks_pane);

    // Create units pane with border
    units_pane = newwin(TER_HEIGHT/2,TER_WIDTH/2,20,2);
    refresh();
    box(units_pane,0,0);
    mvwprintw(units_pane,0,4,"UNITS LIST");
    wrefresh(units_pane);

     // Create info pane with border
    info_pane = newwin(TER_HEIGHT/3,TER_WIDTH/4,20,(TER_WIDTH/2)+2);
    refresh();
    box(info_pane,0,0);
    mvwprintw(info_pane,0,4,"INFORMATION PANEL");
    wrefresh(info_pane);

    getch();
    
}