#ifndef CONTROLLEDEPUCKFACTORY_CPP
#define CONTROLLEDEPUCKFACTORY_CPP

#include <boost/dynamic_bitset.hpp>
#include <unordered_map>
#include "../../Automaton/Automaton.cpp"
#include "../../Automaton/AutomatonPlayer.cpp"
#include "./ControlledEPuck.cpp"
using individual_type = boost::dynamic_bitset<>;
using event_params = std::unordered_map<std::string, std::pair<double, double>>;

class ControlledEPuckFactory {
public:
    ControlledEPuckFactory(Automaton* base_automaton) : base_automaton(base_automaton) {}
    
    ControlledEPuck* buildFromChromosome(individual_type chromosome) {
        Automaton* automaton = this->buildModifiedAutomatonFromChromosome(chromosome);
        AutomatonPlayer* player = new AutomatonPlayer(automaton);
        event_params speeds_by_event = this->buildSpeedsByEventFromChromosome(chromosome);
        return new ControlledEPuck(player, speeds_by_event);
    }

private:
    Automaton* base_automaton;

    Automaton* buildModifiedAutomatonFromChromosome(individual_type chromosome) {
        std::vector<Transition*> transitions;
        std::vector<State*> states;
        std::vector<Event*> events;

        for (auto state = this->base_automaton->getStates().begin(); state != this->base_automaton->getStates().end(); ++state) {
            if ((*state)->getId() >= states.size()) {
                states.resize((*state)->getId() + 1);
            }
            states[(*state)->getId()] = new State((*state)->getId(), (*state)->getName(), (*state)->isInitial());
        }

        for (auto event = this->base_automaton->getEvents().begin(); event != this->base_automaton->getEvents().end(); ++event) {
            if ((*event)->getId() >= events.size()) {
                events.resize((*event)->getId() + 1);
            }
            events[(*event)->getId()] = new Event((*event)->getId(), (*event)->getName(), (*event)->isControllable());
        }
        
        int controllable_transition_index = 0;
        for (auto transition = this->base_automaton->getTransitions().begin(); transition != this->base_automaton->getTransitions().end(); ++transition) {
            if ((*transition)->isControllable()) {
                if (chromosome[controllable_transition_index] == 0) {
                    controllable_transition_index++;
                    continue;
                }
                controllable_transition_index++;
            }

            transitions.push_back(new Transition(
                states[(*transition)->getSource()->getId()],
                states[(*transition)->getTarget()->getId()],
                events[(*transition)->getEvent()->getId()]
            ));
        }

        return new Automaton(events, transitions, states, states[this->base_automaton->getInitialState()->getId()]);
    }

    event_params buildSpeedsByEventFromChromosome(individual_type chromosome) {
        event_params speeds_by_event;

        // TODO: replace hardcoded params with dynamic params from GeneMap
        speeds_by_event["v0"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(4, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(12, 8, chromosome))
        );
        speeds_by_event["v1"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(20, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(28, 8, chromosome))
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