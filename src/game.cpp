#include "headers/game.hpp"
#include "headers/main_menu.hpp"
#include "headers/multiplayer.hpp"
#include "headers/armoury.hpp"

Multiplayer* mp;
MainMenu* mm;
Armoury* ar;

bool end = false;

Game::Game(){

    mm = new MainMenu();
    mp = new Multiplayer();
    ar = new Armoury();
    

    game_loop();
    
}

Game::~Game(){
    delete mp;
    delete mm;
}

int Game::game_loop(){

    short decision {-1};

    /*
    Post main menu divert to:
    0 - Singleplayer (hotseat)
    1 - Multiplayer
    2 - Armoury
    3 - Settings
    4 - Exit
    */
    while(!end){

        decision = mm->display_main_menu();

        switch(decision){

            case 0:
                break;
            case 1:
                mp->display_multiplayer();
                break;
            case 2:
                ar->display_armoury();
                break;
            case 3:
                break;
            case 4:
                end = true;
                break;
        }
    }
    

    

    return 0;
}