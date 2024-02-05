#include <ncurses/ncurses.h>
#include <vector>
#include <string>
#include "headers/armoury.hpp"
#include "headers/globals.hpp"
#include "headers/deck.hpp"

std::vector<std::string> columns {"Logistics:", "Ground forces:", "Helicopters:", "Airforce:", "Naval:"};


short user_action {-1};

Armoury::Armoury(){
    main_armoury_win = newwin(TER_HEIGHT,TER_WIDTH,0,0);
    decks_pane = newwin(TER_HEIGHT/4+8,TER_WIDTH/2,1,2);
    instructions_pane = newwin(TER_HEIGHT/4+8,TER_WIDTH/4 + 16,1,(TER_WIDTH/2)+2);
    units_pane = newwin(TER_HEIGHT/2+5,TER_WIDTH/2,24,2);
    unit_info_pane = newwin(TER_HEIGHT/2+5,TER_WIDTH/4 + 16,24,(TER_WIDTH/2)+2);
    deck_units_pane = newwin(TER_HEIGHT-2,30,1,TER_WIDTH-32);

}

Armoury::~Armoury(){
    delwin(main_armoury_win);
    delwin(decks_pane);
    delwin(instructions_pane);
    delwin(units_pane);
    delwin(unit_info_pane);
    delwin(deck_units_pane);
    delwin(create_deck_pane);
}

void Armoury::display_armoury(){

    clear();
    refresh();

    // Create main window with border
    box(main_armoury_win,0,0);
    wrefresh(main_armoury_win);

    // Create decks pane with border
    box(decks_pane,0,0);
    mvwprintw(decks_pane,0,4,"DECKS PANEL");

    short row {0};
    short col {0};

    for(int i {0}; i < decks.size(); i++){
        mvwprintw(decks_pane, 4+i, 4, (decks.at(i)).deck_name.c_str());    // POPRAVI IZPIS!!!
        mvwprintw(decks_pane, 4+i, 4+(decks.at(i)).deck_name.length(), " (%d/%d)", decks.at(i).current_size, deck_size_limit);
    }
    wrefresh(decks_pane);

    // Create instructions pane with border
    box(instructions_pane,0,0);
    mvwprintw(instructions_pane,0,4,"INSTRUCTIONS & CONTROLS PANEL");
    mvwprintw(instructions_pane,2,4,"Select deck from DECKS PANEL: arrow keys LEFT & RIGHT.");
    mvwprintw(instructions_pane,3,4,"Select unit from UNITS LIST PANEL: arrow keys UP & DOWN.");
    wattron(instructions_pane, COLOR_PAIR(2));
    mvwprintw(instructions_pane,5,4,"Create new deck: press C");
    wattroff(instructions_pane, COLOR_PAIR(2));
    wattron(instructions_pane, COLOR_PAIR(3));
    mvwprintw(instructions_pane,7,4,"Edit deck: press E");
    wattroff(instructions_pane, COLOR_PAIR(3));
    wattron(instructions_pane, COLOR_PAIR(4));
    mvwprintw(instructions_pane,9,4,"Delete deck: press D");
    wattroff(instructions_pane, COLOR_PAIR(4));
    mvwprintw(instructions_pane,11,4,"Save changes: press S");
    mvwprintw(instructions_pane,12,4,"Return to main menu: press B");
    wrefresh(instructions_pane);

    // Create units pane with border
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
    box(unit_info_pane,0,0);
    mvwprintw(unit_info_pane,0,4,"UNIT INFORMATION PANEL");
    wrefresh(unit_info_pane);

    // Create deck units info pane with border
    box(deck_units_pane,0,0);
    mvwprintw(deck_units_pane,0,4,"UNITS IN DECK");
    wrefresh(deck_units_pane);

}

void Armoury::armoury_loop(){

    while(true){

        display_armoury();

        user_action = getch();

        if(user_action == 'b' || user_action == 'B'){
            break;
        }else if(user_action == 'c' || user_action == 'C'){
            create_new_deck();
        }   

    }

}

void Armoury::create_new_deck(){

    create_deck_pane = newwin(TER_HEIGHT/3, TER_WIDTH/4, TER_HEIGHT/2 - TER_HEIGHT/6, TER_WIDTH/2 - TER_WIDTH/8);
    Deck new_deck("default_name", "std", 0);

    short name_length_limit {15};
    bool confirm_name {false};
    std::string deck_name = "               ";
    char user_input {};
    short num_of_input {0};

    // Create decks pane with border
    box(create_deck_pane,0,0);
    mvwprintw(create_deck_pane,0,4,"CREATE NEW DECK");
    mvwprintw(create_deck_pane,2,4,"(max 15 characters)");
    mvwprintw(create_deck_pane,4,4,"Deck name:");
    mvwprintw(create_deck_pane,5,4,"(Press ENTER to confirm)");
    wrefresh(create_deck_pane);

    while(!confirm_name){

        user_input = wgetch(create_deck_pane);

        if(num_of_input > 14){
            num_of_input = 14;
        }

        if(num_of_input < 0){
            num_of_input = 0;
        }

        // User pressed ENTER to confirm name
        if(num_of_input >= 1 && user_input == 10){
            confirm_name = true;
            new_deck.deck_name = deck_name;
            decks.push_back(new_deck);
            continue;
        }

        // User used BACKSPACE
        if(!deck_name.empty() && user_input == 8){
            deck_name[num_of_input-1] = ' ';
            num_of_input--;

        // Append user character to deck name
        }else if(num_of_input < 15 && (user_input >= 32 && user_input <= 126)){
            deck_name[num_of_input] = user_input;
            num_of_input++;
        }

        mvwprintw(create_deck_pane,4,15,deck_name.c_str());
        wrefresh(create_deck_pane);
    }

    wrefresh(create_deck_pane);
    delwin(create_deck_pane);

}

void Armoury::delete_deck(){
    
}

void Armoury::edit_deck(){
    
}