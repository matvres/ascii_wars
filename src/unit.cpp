#include "headers/unit.hpp"
#include "headers/globals.hpp"

std::vector<Unit> ground_units;

Unit::Unit(char u_symbol, char u_size, short u_slot_cost, short u_health, short u_damage, short u_range, short u_movement, float u_acc, std::string u_name, std::string u_desc)
:   unit_symbol{u_symbol}, 
    unit_size{u_size}, 
    unit_slot_cost{u_slot_cost}, 
    unit_health{u_health}, 
    unit_damage{u_damage}, 
    unit_range{u_range}, 
    unit_movement{u_movement}, 
    unit_accuracy{u_acc}, 
    unit_name{u_name}, 
    unit_desc{u_desc}
{



}



Unit::~Unit(){
    
}