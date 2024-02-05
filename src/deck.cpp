#include "headers/deck.hpp"
#include "headers/globals.hpp"


std::vector<Deck> decks;
int deck_size_limit {20};

void Deck::add_unit_to_deck(){

}

void Deck::remove_unit_from_deck(){

}

Deck::Deck(std::string d_name, std::string d_prefix, int d_currrent_size) {
    deck_name = d_name;
    deck_prefix = d_prefix;
    current_size = d_currrent_size;
}

Deck::Deck(){

}

Deck::~Deck(){

}