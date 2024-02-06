#include "headers/deck.hpp"
#include "headers/globals.hpp"

std::vector<Deck> decks;
short deck_size_limit {20};
short max_num_decks {40};
short current_num_decks {0};

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