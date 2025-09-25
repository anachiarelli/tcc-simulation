#include <boost/dynamic_bitset.hpp>
#include "../../Automaton/Automaton.cpp"
#include "./ControlledEPuck.cpp"
using individual_type = boost::dynamic_bitset<>;

class ControlledEPuckFactory {
public:
    ControlledEPuckFactory(Automaton* base_automaton) : base_automaton(base_automaton) {}
    
    ControlledEPuck* buildFromChromosome(individual_type chromosome) {
    }

private:
    Automaton* base_automaton;
};
