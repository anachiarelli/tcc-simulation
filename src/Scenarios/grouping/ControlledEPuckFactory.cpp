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
        // std::cout << "Building modified automaton for " << chromosome << std::endl;
        Automaton* automaton = this->buildModifiedAutomatonFromChromosome(chromosome);
        // std::cout << "Building AutomatonPlayer." << std::endl;
        AutomatonPlayer* player = new AutomatonPlayer(automaton);
        // std::cout << "Building speeds_by_event." << std::endl;
        event_params speeds_by_event = this->buildSpeedsByEventFromChromosome(chromosome);
        // std::cout << "Building ControlledEPuck." << std::endl;
        return new ControlledEPuck(player, speeds_by_event);
    }

private:
    Automaton* base_automaton;

    Automaton* buildModifiedAutomatonFromChromosome(individual_type chromosome) {
        std::vector<Transition*> transitions;
        std::vector<State*> states;
        std::vector<Event*> events;

        auto base_states = this->base_automaton->getStates();
        // std::cout << "Cloning " << this->base_automaton->getStates().size() << " states..." << std::endl;
        for (auto state = base_states.begin(); state != base_states.end(); ++state) {
            if ((*state)->getId() >= states.size()) {
                states.resize((*state)->getId() + 1);
            }
            states[(*state)->getId()] = new State((*state)->getId(), (*state)->getName(), (*state)->isInitial());
        }

        auto base_events = this->base_automaton->getEvents();
        // std::cout << "Cloning " << base_events.size() << " events..." << std::endl;
        for (auto event = base_events.begin(); event != base_events.end(); ++event) {
            if ((*event)->getId() >= events.size()) {
                events.resize((*event)->getId() + 1);
            }
            events[(*event)->getId()] = new Event((*event)->getId(), (*event)->getName(), (*event)->isControllable());
        }
        
        auto base_transitions = this->base_automaton->getTransitions();
        // std::cout << "Cloning " << base_transitions.size() << " transitions..." << std::endl;
        int controllable_transition_index = 0;
        for (auto transition = base_transitions.begin(); transition != base_transitions.end(); ++transition) {
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