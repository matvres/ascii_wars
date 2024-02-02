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
    WINDOW* info_pane;

    void display_armoury();
    Armoury();
    ~Armoury();
};