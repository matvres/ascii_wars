#include <iostream>
#include <ncurses/ncurses.h>
#include <vector>
#include <string>
#include "headers/armoury.hpp"
#include "headers/globals.hpp"
#include "headers/deck.hpp"
#include "headers/unit.hpp"

std::vector<std::string> columns {"Logistics:", "Ground forces:", "Helicopters:", "Airforce:", "Naval:"};
short user_action {-1};
int d_selected {0};
int u_selected {0};

Armoury::Armoury(){
    main_armoury_win = newwin(TER_HEIGHT,TER_WIDTH,0,0);
    decks_pane = newwin(TER_HEIGHT/4+8,TER_WIDTH/2,1,2);
    instructions_pane = newwin(TER_HEIGHT/4+8,TER_WIDTH/4 + 16,1,(TER_WIDTH/2)+2);
    units_pane = newwin(TER_HEIGHT/2+5,TER_WIDTH/2,24,2);
    unit_info_pane = newwin(TER_HEIGHT/2+5,TER_WIDTH/4 + 16,24,(TER_WIDTH/2)+2);
    deck_units_pane = newwin(TER_HEIGHT-2,30,1,TER_WIDTH-32);

    generate_unit_armoury();

    keypad(stdscr,true);
    keypad(delete_deck_pane,true);
}

Armoury::~Armoury(){
    A = delwin(main_armoury_win);
    delwin(decks_pane);
    delwin(instructions_pane);
    delwin(units_pane);
    delwin(unit_info_pane);
    delwin(deck_units_pane);
    delwin(create_deck_pane);
}

void Armoury::display_armoury(){
    
    // Create main window with border
    box(main_armoury_win,0,0);
    wrefresh(main_armoury_win);

    // Create decks pane with border
    wclear(decks_pane);
    box(decks_pane,0,0);
    mvwprintw(decks_pane,0,4,"DECKS PANEL ");
    mvwprintw(decks_pane,0,16,"(%i/%i)", current_num_decks, max_num_decks);
    display_decks();
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
    mvwprintw(instructions_pane,7,4,"Edit (selected) deck: press E");
    wattroff(instructions_pane, COLOR_PAIR(3));
    wattron(instructions_pane, COLOR_PAIR(4));
    mvwprintw(instructions_pane,9,4,"Delete (selected) deck: press D");
    wattroff(instructions_pane, COLOR_PAIR(4));
    mvwprintw(instructions_pane,11,4,"Save changes: press S");
    mvwprintw(instructions_pane,12,4,"Return to main menu: press B");
    wrefresh(instructions_pane);

    // Create units pane with border
    wclear(units_pane);
    box(units_pane,0,0);
    mvwprintw(units_pane,0,4,"UNITS LIST PANEL");

    for(int i {0}; i < columns.size(); i++){
        wattron(units_pane, COLOR_PAIR(5));
        mvwprintw(units_pane,2,i*20 + 4,columns[i].c_str());
        wattroff(units_pane, COLOR_PAIR(5));
    }
    display_units();
    mvwprintw(units_pane,3,2,"________________________________________________________________________________________________");
    wrefresh(units_pane);
    

     // Create unit info pane with border
    wclear(unit_info_pane);
    box(unit_info_pane,0,0);
    mvwprintw(unit_info_pane,0,4,"UNIT INFORMATION PANEL");
    wrefresh(unit_info_pane);

    // Create deck units info pane with border
    wclear(deck_units_pane);
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
            if(current_num_decks < max_num_decks){
                create_new_deck();
                current_num_decks++;
            }
                
        }else if(user_action == KEY_RIGHT || user_action == KEY_LEFT){
            deck_selector();
        }else if(user_action == 'd' || user_action == 'D'){
            if(current_num_decks > 0){
                delete_deck();
            }
        }else if(user_action == KEY_DOWN || user_action == KEY_UP){
            unit_selector();
        }else{
            // no defined legal action
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

        if(num_of_input > 15){
            num_of_input = 15;
        }

        if(num_of_input <= 0){
            num_of_input = 0;
        }

        user_input = wgetch(create_deck_pane);

        // User pressed ENTER to confirm name
        if(num_of_input >= 1 && user_input == 10){
            confirm_name = true;
            new_deck.deck_name = deck_name;
            decks.push_back(new_deck);
            continue;
        }

        // User used BACKSPACE
        if(num_of_input > 0 && user_input == 8){

            num_of_input--;
            deck_name[num_of_input] = ' ';
            
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
    display_decks();
}

void Armoury::display_decks(){

    short row {0};
    short col {0};

    // Print all decks
    for(int i {0}; i < decks.size(); i++){

        if(i == d_selected){
            wattron(decks_pane, A_REVERSE);
            mvwprintw(decks_pane, 2+row*2, col*25 + 2, (decks.at(i)).deck_name.c_str());
            mvwprintw(decks_pane, 2+row*2, col*25 + (decks.at(i)).deck_name.length() + 2, " (%i/%i)", decks.at(i).current_size, deck_size_limit);
            wattroff(decks_pane, A_REVERSE);
        }else{
            mvwprintw(decks_pane, 2+row*2, col*25 + 2, (decks.at(i)).deck_name.c_str());
            mvwprintw(decks_pane, 2+row*2, col*25 + (decks.at(i)).deck_name.length() + 2, " (%i/%i)", decks.at(i).current_size, deck_size_limit);
        }
        
        if(row < 9){
            row++;
        }else{
            row = 0;
            col++;
        }
    }
}

void Armoury::deck_selector(){

    if(user_action == KEY_RIGHT && (d_selected < decks.size()-1)){
        d_selected++;
    }else if(user_action == KEY_LEFT && (d_selected > 0)){
        d_selected--;
    }
}

void Armoury::delete_deck(){

    delete_deck_pane = newwin(TER_HEIGHT/5, TER_WIDTH/5, TER_HEIGHT/2 - TER_HEIGHT/10, TER_WIDTH/2 - TER_WIDTH/10);
    char inp {};
    bool bck = false;

    // Create decks pane with border
    box(delete_deck_pane,0,0);
    mvwprintw(delete_deck_pane,2,4,"DELETE selected deck?");
    mvwprintw(delete_deck_pane,4,4,"(Press ENTER to confirm)");
    wrefresh(delete_deck_pane);

    while(!bck){

        inp = wgetch(delete_deck_pane);

        // User pressed ENTER to confirm name
        if(inp == 10){
            decks.erase(decks.begin() + d_selected);
            current_num_decks--;
            d_selected--;
            if(d_selected < 0){
                d_selected = 0;
            }
            bck = true;
        }else{
            bck = true;
        }

    }
    
    delwin(delete_deck_pane);
}

void Armoury::unit_selector(){

    if(user_action == KEY_DOWN && (u_selected < ground_units.size()-1)){
        u_selected++;
    }else if(user_action == KEY_UP && (u_selected > 0)){
        u_selected--;
    }
}

void Armoury::display_units(){

    short row {0};
    short col {0};

    // Print all ground units
    for(int i {0}; i < ground_units.size(); i++){

        if(i == u_selected){
            wattron(units_pane, A_REVERSE);
            mvwprintw(units_pane, 5+row*2, col*25 + 2, (ground_units.at(i)).unit_name.c_str()); // popravi formatiranje izpisa glede na units panel
            wattroff(units_pane, A_REVERSE);
        }else{
            mvwprintw(units_pane, 5+row*2, col*25 + 2, (ground_units.at(i)).unit_name.c_str()); // popravi formatiranje izpisa glede na units panel
        }
        
        if(row < 14){
            row++;
        }else{
            row = 0;
            col++;
        }
    }
}

// TODO...
void Armoury::edit_deck(){
    
}

// Creates 1 instance of every unit for armoury
void Armoury::generate_unit_armoury(){

    // TODO...
    Unit new_test_unit1('X', 'S', 1, 10, 2, 1, 1, 0.8, "Infantry", "Generic infantry unit");
    Unit new_test_unit2('T', 'L', 2, 15, 4, 3, 2, 0.7, "Tank", "Generic tank unit");
    ground_units.push_back(new_test_unit1);
    ground_units.push_back(new_test_unit2);

}