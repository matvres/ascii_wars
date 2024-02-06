#pragma once
#include <ncurses/ncurses.h>
#include <string>
#include <vector>

class Armoury{
private:

public:
    WINDOW* main_armoury_win;
    WINDOW* decks_pane;
    WINDOW* units_pane;
    WINDOW* unit_info_pane;
    WINDOW* deck_units_pane;
    WINDOW* instructions_pane;

    WINDOW* create_deck_pane;

    // Main display and flow operations
    void display_armoury();
    void armoury_loop();
    
    // Deck operations
    void display_decks();
    void create_new_deck();
    void deck_selector();
    void delete_deck();
    void edit_deck();

    Armoury();
    ~Armoury();
};