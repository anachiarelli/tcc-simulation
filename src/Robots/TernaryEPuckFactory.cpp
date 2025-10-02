#ifndef TERNARYEPUCKFACTORY_CPP
#define TERNARYEPUCKFACTORY_CPP

#include <boost/dynamic_bitset.hpp>
#include <unordered_map>
#include "../Automaton/Automaton.cpp"
#include "../Automaton/AutomatonPlayer.cpp"
#include "./TernaryEPuck.cpp"
using individual_type = boost::dynamic_bitset<>;
using event_params = std::unordered_map<std::string, std::pair<double, double>>;

class TernaryEPuckFactory {
public:
    TernaryEPuckFactory(Automaton* base_automaton) : base_automaton(base_automaton) {}

    TernaryEPuck* buildFromChromosome(individual_type chromosome) {
        // std::cout << "Building modified automaton for " << chromosome << std::endl;
        Automaton* automaton = this->buildModifiedAutomatonFromChromosome(chromosome);
        // std::cout << "Building AutomatonPlayer." << std::endl;
        AutomatonPlayer* player = new AutomatonPlayer(automaton);
        // std::cout << "Building speeds_by_event." << std::endl;
        event_params speeds_by_event = this->buildSpeedsByEventFromChromosome(chromosome);
        // std::cout << "Building TernaryEPuck." << std::endl;
        Enki::Color epuck_color = Enki::Color(0.0, 0.0, 1.0, 1.0);
        Enki::Color object_color = Enki::Color(1.0, 0.0, 0.0, 1.0);
        return new TernaryEPuck(player, speeds_by_event, epuck_color, object_color);
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
        speeds_by_event["v_s"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(27, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(35, 8, chromosome))
        );
        speeds_by_event["v_w"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(43, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(51, 8, chromosome))
        );
        speeds_by_event["v_o"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(59, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(67, 8, chromosome))
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