#include "game.hpp"
#include "main_menu.hpp"
#include "multiplayer.hpp"

Game::Game(){

    

    menu_loop();
    
}

Game::~Game(){
    
}

int Game::menu_loop(){

    short decision {-1};

    Multiplayer* mp;

    MainMenu* mm = new MainMenu();
    decision = mm->main_menu();
    delete mm;

    /*
    Post main menu divert to:
    0 - Singleplayer (hotseat)
    1 - Multiplayer
    2 - Armoury
    3 - Settings
    4 - Exit
    */
    switch(decision){

        case 0:
            break;
        case 1:
            mp = new Multiplayer();
            delete mp;
            break;
        case 2:
            break;
        case 3:
            break;
        case 4:
            break;
    }

    

    return 0;
}