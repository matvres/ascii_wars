#pragma once

#include <vector>
#include "deck.hpp"

// Window size related
extern int TER_HEIGHT;
extern int TER_WIDTH;

// Decks related
extern std::vector<Deck> decks;
extern short deck_size_limit;
extern short max_num_decks;
extern short current_num_decks;

// Units related
extern std::vector<Unit> ground_units;

// Debbuging related
extern int A; 
extern int B;
extern int C;
extern int D;
extern int E;