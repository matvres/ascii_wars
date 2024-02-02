#include <ncurses/ncurses.h>
#include <vector>
#include <string>
#include "headers/armoury.hpp"
#include "headers/globals.hpp"

std::vector<std::string> columns {"Logistics:", "Ground forces:", "Helicopters:", "Airforce:", "Naval:"};

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
    decks_pane = newwin(TER_HEIGHT/4+5,TER_WIDTH/2,1,2);
    refresh();
    box(decks_pane,0,0);
    mvwprintw(decks_pane,0,4,"DECKS PANEL");
    //mvwprintw(decks_pane,2,4,"dasdasdigsapuioghpsaudhgpoasuhgodasughpioasdhgisaohgnfodksnvsšpdoigfhasdšgoauishdgšposdgpvocsjvbnoscaiuhdšgoisdšvoicjšoxišaopidghšaosidghšoasid");
    wrefresh(decks_pane);

    // Create units pane with border
    units_pane = newwin(TER_HEIGHT/2+5,TER_WIDTH/2,24,2);
    refresh();
    box(units_pane,0,0);
    mvwprintw(units_pane,0,4,"UNITS LIST PANEL");

    for(int i {0}; i < columns.size(); i++){
        wattron(units_pane, A_REVERSE);
        mvwprintw(units_pane,2,i*20 + 4,columns[i].c_str());
        wattroff(units_pane, A_REVERSE);
    }
    mvwprintw(units_pane,3,2,"________________________________________________________________________________________________");
    wrefresh(units_pane);
    

     // Create unit info pane with border
    unit_info_pane = newwin(TER_HEIGHT/2+5,TER_WIDTH/4,24,(TER_WIDTH/2)+2);
    refresh();
    box(unit_info_pane,0,0);
    mvwprintw(unit_info_pane,0,4,"UNIT INFORMATION PANEL");
    wrefresh(unit_info_pane);

     // Create info pane with border
    deck_units_pane = newwin(TER_HEIGHT/2+5,46,24,TER_WIDTH -48);
    refresh();
    box(deck_units_pane,0,0);
    mvwprintw(deck_units_pane,0,4,"UNITS IN DECK");
    wrefresh(deck_units_pane);

    getch();
    
}

void Armoury::create_new_deck(){

}

void Armoury::delete_deck(){
    
}

void Armoury::edit_deck(){
    
}