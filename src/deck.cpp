#include "headers/deck.hpp"

void Deck::add_unit_to_deck(){

}

void Deck::remove_unit_from_deck(){

}

Deck::Deck(std::string d_name, std::string d_prefix, int d_currrent_size = 0, int d_size_limit = 20) {
    deck_name = d_name;
    deck_prefix = d_prefix;
    current_size = d_currrent_size;
    size_limit = d_size_limit;
}

Deck::~Deck(){

}