#include <iostream>
#include <ncurses/ncurses.h>
#include <vector>
#include <string>
#include "headers/armoury.hpp"
#include "headers/globals.hpp"
#include "headers/deck.hpp"
#include "headers/unit.hpp"

short user_action {-1};

std::vector<std::string> nations {"USA", "RUS", "GER", "CHI", "FIN", "GBR", "FRA", "POL", "IRN", "JAP"};
int nation_id {0};


std::vector<std::string> categories {"Infantry", "Armour", "Support", "Logistics", "Drones", "Helicopters", "Airforce", "Naval"};
int category_id {0};

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
    delwin(main_armoury_win);
    delwin(decks_pane);
    delwin(instructions_pane);
    delwin(units_pane);
    delwin(unit_info_pane);
    delwin(deck_units_pane);
}

void Armoury::display_armoury(){

    refresh();
    
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
    mvwprintw(instructions_pane,2,4,"--------------------------GENERAL--------------------------");
    mvwprintw(instructions_pane,3,4," -> RETURN TO MAIN MENU: press B");
    wattron(instructions_pane, COLOR_PAIR(3));
    mvwprintw(instructions_pane,5,4,"------------------------DECKS PANEL------------------------");
    wattroff(instructions_pane, COLOR_PAIR(3));
    mvwprintw(instructions_pane,6,4," -> SELECT DECK: arrow keys LEFT & RIGHT");
    mvwprintw(instructions_pane,7,4," -> CREATE NEW DECK:: press C");
    mvwprintw(instructions_pane,8,4," -> EDIT (SELECTED) DECK: press E");
    mvwprintw(instructions_pane,9,4,"     -> SAVE CHANGES: press S");
    mvwprintw(instructions_pane,10,4," -> DELETE (SELECTED) DECK: press D");
    wattron(instructions_pane, COLOR_PAIR(2));
    mvwprintw(instructions_pane,12,4,"---------------------UNITS LIST PANEL----------------------");
    wattroff(instructions_pane, COLOR_PAIR(2));
    mvwprintw(instructions_pane,13,4," -> SELECT UNIT: arrow keys UP & DOWN");
    mvwprintw(instructions_pane,14,4," -> SELECT NATION: press N");
    mvwprintw(instructions_pane,15,4," -> SELECT CATEGORY: press M");
    wattron(instructions_pane, COLOR_PAIR(4));
    mvwprintw(instructions_pane,17,4,"-------------------UNITS INFORMATION PANEL-----------------");
    wattroff(instructions_pane, COLOR_PAIR(4));
    mvwprintw(instructions_pane,18,4," -> ADD (SELECTED) UNIT: press A");
    mvwprintw(instructions_pane,19,4," -> REMOVE (SELECTED) UNIT: press R");
    wrefresh(instructions_pane);

    // Create units pane with border
    wclear(units_pane);
    box(units_pane,0,0);
    mvwprintw(units_pane,0,4,"UNITS LIST PANEL");
    mvwprintw(units_pane,2,4,"Nation: ");
    mvwprintw(units_pane,2,TER_WIDTH/4,"Category: ");
    mvwprintw(units_pane,3,2,"________________________________________________________________________________________________");
    mvwprintw(units_pane, 2, TER_WIDTH/4 + 10, (categories.at(category_id)).c_str());
    display_units();
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
        display_decks();

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
        }else if(user_action == 'm' || user_action == 'M'){
            if(category_id < categories.size()-1){
                category_id++;
            }else{
                category_id = 0;
            }
        }else{
            // no defined legal action
        }
    }
}

void Armoury::create_new_deck(){

    create_deck_pane = newwin(TER_HEIGHT/3, TER_WIDTH/4, TER_HEIGHT/2 - TER_HEIGHT/6, TER_WIDTH/2 - TER_WIDTH/8);
    Deck new_deck("default_name", "std", 0);
    short new_selected_nat {0};
    bool confirm_name {false};
    std::string deck_name = "          ";
    char user_input {};
    short num_of_input {0};
    bool nation_selected {false};

    // Create decks pane with border
    box(create_deck_pane,0,0);
    mvwprintw(create_deck_pane,0,4,"CREATE NEW DECK");
    mvwprintw(create_deck_pane,4,4,"Select nation: ");
    mvwprintw(create_deck_pane,6,4,"(Use arrow keys LEFT & RIGHT)");
    mvwprintw(create_deck_pane,7,4,"(Press ENTER to confirm nation)");
    wattron(create_deck_pane, A_REVERSE);
    mvwprintw(create_deck_pane,4,19,nations.at(new_selected_nat).c_str());
    wattroff(create_deck_pane, A_REVERSE);
    mvwprintw(create_deck_pane,10,4,"Deck name:");
    mvwprintw(create_deck_pane,14,4,"(Press ENTER to confirm name)");
    wrefresh(create_deck_pane);

    while(!confirm_name){

        user_input = wgetch(create_deck_pane);

        if(!nation_selected){
            
            // Select nation with arrow keys => 'M' & 'K' map to KEY_RIGHT and KEY_LEFT
            if((user_input == 'M') && (new_selected_nat < nations.size()-1)){
                new_selected_nat++;
                wattron(create_deck_pane, A_REVERSE);
                mvwprintw(create_deck_pane,4,19,nations.at(new_selected_nat).c_str());
                wattroff(create_deck_pane, A_REVERSE);
            }else if((user_input == 'K') && (new_selected_nat > 0)){
                new_selected_nat--;
                wattron(create_deck_pane, A_REVERSE);
                mvwprintw(create_deck_pane,4,19,nations.at(new_selected_nat).c_str());
                wattroff(create_deck_pane, A_REVERSE);
            }else if(user_input == 10){
                wattroff(create_deck_pane, A_REVERSE);
                mvwprintw(create_deck_pane,4,19,nations.at(new_selected_nat).c_str());
                nation_selected = true;
                new_deck.deck_prefix = nations.at(new_selected_nat);
            }

        }else{
            if(num_of_input > 10){
            num_of_input = 10;
            }

            if(num_of_input <= 0){
                num_of_input = 0;
            }

            // User pressed ENTER to confirm
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
            }else if(num_of_input < 10 && (user_input >= 32 && user_input <= 126)){
                deck_name[num_of_input] = user_input;
                num_of_input++;
            }

            mvwprintw(create_deck_pane,10,15,deck_name.c_str());
        }

        wrefresh(create_deck_pane);
    }

    wrefresh(create_deck_pane);
    delwin(create_deck_pane);
}

void Armoury::display_decks(){

    short row {0};
    short col {0};

    // Print all decks
    for(int i {0}; i < decks.size(); i++){

        if(i == d_selected){
            wattron(decks_pane, A_REVERSE);
            mvwprintw(decks_pane, 2+row*2, col*25 + 2, "[");
            mvwprintw(decks_pane, 2+row*2, col*25 + 3, (decks.at(i)).deck_prefix.c_str());
            mvwprintw(decks_pane, 2+row*2, col*25 + 6, "]");
            mvwprintw(decks_pane, 2+row*2, col*25 + 7, (decks.at(i)).deck_name.c_str());
            mvwprintw(decks_pane, 2+row*2, col*25 + (decks.at(i)).deck_name.length() + 7, " (%i/%i)", decks.at(i).current_size, deck_size_limit);
            wattroff(decks_pane, A_REVERSE);
        }else{
            mvwprintw(decks_pane, 2+row*2, col*25 + 2, "[");
            mvwprintw(decks_pane, 2+row*2, col*25 + 3, (decks.at(i)).deck_prefix.c_str());
            mvwprintw(decks_pane, 2+row*2, col*25 + 6, "]");
            mvwprintw(decks_pane, 2+row*2, col*25 + 7, (decks.at(i)).deck_name.c_str());
            mvwprintw(decks_pane, 2+row*2, col*25 + (decks.at(i)).deck_name.length() + 7, " (%i/%i)", decks.at(i).current_size, deck_size_limit);
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

// Switch units category in units panel
void Armoury::switch_category(){
    
    // TODO...

}

// Creates 1 instance of every unit for armoury
void Armoury::generate_unit_armoury(){

    // TODO...
    Unit new_test_unit1('X', 'S', 1, 10, 2, 1, 1, 0.8, "Infantry", "Generic infantry unit");
    Unit new_test_unit2('T', 'L', 2, 15, 4, 3, 2, 0.7, "Tank", "Generic tank unit");
    ground_units.push_back(new_test_unit1);
    ground_units.push_back(new_test_unit2);

}