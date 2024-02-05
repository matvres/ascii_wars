#pragma once
#include <vector>
#include <string>
#include "unit.hpp"

class Deck{
private:

public:

    static std::vector<Deck> player_decks;

    std::string deck_name;
    std::string deck_prefix;
    int size_limit;
    int current_size;
    std::vector<Unit> units_list;

    void add_unit_to_deck();
    void remove_unit_from_deck();


    Deck();
    Deck(std::string d_name, std::string d_prefix, int d_currrent_size, int d_size_limit);
    ~Deck();
};