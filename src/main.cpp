#include <iostream>
#include <vector>
#include <string>
#include <ncurses/ncurses.h>

using namespace std;

int main(){

    // start ncurses
    initscr();

    
    getch();

    // end ncurses
    endwin();

    return 0;
}