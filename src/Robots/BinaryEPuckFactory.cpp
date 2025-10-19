#ifndef BINARYEPUCKFACTORY_CPP
#define BINARYEPUCKFACTORY_CPP

#include <boost/dynamic_bitset.hpp>
#include <unordered_map>
#include "../Automaton/Automaton.cpp"
#include "../Automaton/AutomatonPlayer.cpp"
#include "./BinaryEPuck.cpp"
using individual_type = boost::dynamic_bitset<>;
using event_params = std::unordered_map<std::string, std::pair<double, double>>;

class BinaryEPuckFactory {
public:
    BinaryEPuckFactory(Automaton* base_automaton, AutomatonFactory* automaton_factory) : base_automaton(base_automaton), automaton_factory(automaton_factory) {}

    BinaryEPuck* buildFromChromosome(individual_type chromosome) {
        // std::cout << "Building modified automaton for " << chromosome << std::endl;
        Automaton* automaton = this->automaton_factory->buildModifiedAutomatonFromChromosome(chromosome, this->base_automaton);
        // std::cout << "Building AutomatonPlayer." << std::endl;
        AutomatonPlayer* player = new AutomatonPlayer(automaton);
        // std::cout << "Building speeds_by_event." << std::endl;
        event_params speeds_by_event = this->buildSpeedsByEventFromChromosome(chromosome);
        // std::cout << "Building BinaryEPuck." << std::endl;
        return new BinaryEPuck(player, speeds_by_event);
    }

private:
    Automaton* base_automaton;
    AutomatonFactory* automaton_factory;

    event_params buildSpeedsByEventFromChromosome(individual_type chromosome) {
        event_params speeds_by_event;

        // TODO: replace hardcoded params with dynamic params from GeneMap
        speeds_by_event["v0"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(8, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(16, 8, chromosome))
        );
        speeds_by_event["v1"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(24, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(32, 8, chromosome))
        );

        return speeds_by_event;
    }
    
    uint64_t decodeChromosomeSegment(int begin, int length, individual_type chromosome) {
        uint64_t value = 0;

        for (size_t i = begin; i < (length + begin); ++i) {
            if (chromosome[i]) {
                value |= (1ULL << (i - begin));
            }
        }
        return value;
    }

    double transformChromosomeSegmentValueIntoSpeed(uint64_t value) {
        return (-12.8 + (value * 0.1));
    }
};

#endif