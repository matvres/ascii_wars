#pragma once
#include <ncurses/ncurses.h>

class MainMenu{
private:


public:

    WINDOW* menu_win;
    WINDOW* main_menu_win;

    int menu_box_w {};
    int menu_box_h {};
    
    int selection {};

    MainMenu();
    ~MainMenu();
    
    int display_main_menu();

};