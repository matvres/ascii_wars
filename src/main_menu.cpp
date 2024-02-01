#include "headers/main_menu.hpp"
#include "headers/globals.hpp"
#include <ncurses/ncurses.h>
#include <iostream>
#include <string>
#include <vector>


int MainMenu::display_main_menu() {

    start_color();
    init_pair(1, COLOR_RED, COLOR_WHITE);
    
    // Create main window with border
    main_menu_win = newwin(TER_HEIGHT,TER_WIDTH,0,0);
    refresh();
    box(main_menu_win,0,0);

    // Print title to window    
    wattron(main_menu_win, COLOR_PAIR(1));
    mvwprintw(main_menu_win, TER_HEIGHT/3 - 1, TER_WIDTH/2 - 6, " ASCII WARS ");
    wrefresh(main_menu_win);
    wattroff(main_menu_win, COLOR_PAIR(1));

    // Create menu box
    menu_box_h = 15;
    menu_box_w = 24;
    menu_win = newwin(menu_box_h,menu_box_w,TER_HEIGHT/3,TER_WIDTH/2 - 12);
    box(menu_win,0,0);
    keypad(menu_win,true);
    wrefresh(menu_win);

    std::vector<std::string> choices {"Singleplayer", "Multiplayer", "Armoury", "Settings", "Exit"};

    int highlight {0};
    int choice {0};
    selection = 0;

    while(true){

        for(int i {0}; i < choices.size(); i++){

            if(i == highlight){
                wattron(menu_win, A_REVERSE);
            }
            mvwprintw(menu_win, i*2+2, (menu_box_w/2) - ((choices.at(i)).length())/2, (choices.at(i)).c_str());
            wattroff(menu_win, A_REVERSE);
        }

        choice = wgetch(menu_win);

        switch(choice){
            case KEY_UP:
                if(selection > 0){
                    selection--;
                    highlight--;
                }else{
                    selection = 0;
                    highlight = 0;
                }
                break;
            case KEY_DOWN:
                if(selection < 4){
                    selection++;
                    highlight++;
                }else{
                    selection = 4;
                    highlight = 4;
                }
                break;
            default:
                break;
        }

        // If user confirms with ENTER key
        if(choice == 10){
            break;
        }
    }

    return selection;

}

MainMenu::MainMenu() {

}

MainMenu::~MainMenu(){

}