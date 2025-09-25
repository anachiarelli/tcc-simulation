#ifndef GENEMAPBUILDER_CPP
#define GENEMAPBUILDER_CPP 1

#include <vector>
#include <string>
#include "../../Automaton/Automaton.cpp"
#include "GeneMap.cpp"

class GeneMapBuilder {
public:
    GeneMap buildMapFromAutomaton(Automaton* automaton) {
        GeneMap gene_map;
        int controlled_transitions = 0;
        for (Transition* transition : automaton->getTransitions()) {
            if (transition->isControllable()) {
                controlled_transitions++;
            }
        }
        gene_map.addSection(controlled_transitions, "bitmask");

        // TODO: adicionar genes para os parametros dos eventos

        return gene_map;
    }
};

#endif // GENEMAPBUILDER_CPP