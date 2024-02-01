#pragma once
#include <ncurses/ncurses.h>

class Multiplayer{
private:
public:

    WINDOW* main_multi_win;

    void display_multiplayer();

    Multiplayer();
    ~Multiplayer();

};