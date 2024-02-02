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

    void display_armoury();
    void create_new_deck();
    void delete_deck();
    void edit_deck();
    Armoury();
    ~Armoury();
};