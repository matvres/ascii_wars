#pragma once
#include <vector>
#include <string>

class Unit{
private:

public:

    // Units parameters
    char unit_symbol; // oznaka na mapi
    char unit_size; // S, M, L => za recce?
    short unit_slot_cost; // za deck building
    short unit_health;
    short unit_damage;
    short unit_range;
    short unit_movement;
    float unit_accuracy;
    std::string unit_name;
    std::string unit_desc;

    Unit(char u_symbol, char u_size, short u_slot_cost, short u_health, short u_damage, short u_range, short u_movement, float u_acc, std::string u_name, std::string u_desc);
    ~Unit();

    //void generate_unit_armoury();
};