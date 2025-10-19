#include "Automaton.cpp"
#include <string>
#include <pugixml.hpp>
#include <iostream>
#include <stdexcept>
#include <vector>

#include <boost/dynamic_bitset.hpp>
using individual_type = boost::dynamic_bitset<>;

class AutomatonFactory {
    public:
        Automaton* buildFromXMLFile(const char* path) {
            std::vector<State*> states;
            std::vector<Event*> events;
            std::vector<Transition*> transitions;

            pugi::xml_document doc;
            pugi::xml_parse_result result = doc.load_file(path);
            if (!result) {
                throw std::runtime_error(result.description());
            }

            int initial_state_id = -1;
            for (pugi::xml_node state : doc.child("model").child("data").children("state")) {
                int id = state.attribute("id").as_int();
                std::string name = state.attribute("name").as_string();
                bool is_initial = state.attribute("initial").as_bool();
                bool is_marked = state.attribute("marked").as_bool();
                int x = state.attribute("x").as_int();
                int y = state.attribute("y").as_int();

                if (is_initial) {
                    initial_state_id = id;
                }

                if (id >= states.size()) {
                    states.resize(id + 1);
                }

                states[id] = new State(id, name, is_initial, is_marked, x, y);
            }

            std::cout << "Total states loaded: " << states.size() << std::endl;

            for (pugi::xml_node event : doc.child("model").child("data").children("event")) {
                int id = event.attribute("id").as_int();
                std::string name = event.attribute("name").as_string();
                bool is_controllable = event.attribute("controllable").as_bool();
                bool is_observable = event.attribute("observable").as_bool();

                if (id >= events.size()) {
                    events.resize(id + 1);
                }

                events[id] = new Event(id, name, is_controllable, is_observable);
            }

            std::cout << "Total events loaded: " << events.size() << std::endl;

            for (pugi::xml_node transition : doc.child("model").child("data").children("transition")) {
                int source = transition.attribute("source").as_int();
                int target = transition.attribute("target").as_int();
                int event = transition.attribute("event").as_int();

                transitions.push_back(new Transition(states[source], states[target], events[event]));
            }

            std::cout << "Total transitions loaded: " << transitions.size() << std::endl;

            if (initial_state_id == -1) {
                throw std::runtime_error("No initial state defined in the automaton.");
            }

            std::cout << "Initial state ID: " << initial_state_id << std::endl;

            return new Automaton(events, transitions, states, states[initial_state_id]);
        }

        Automaton* buildModifiedAutomatonFromChromosome(individual_type chromosome, Automaton* base_automaton) {
            std::vector<Transition*> transitions;
            std::vector<State*> states;
            std::vector<Event*> events;

            auto base_states = base_automaton->getStates();
            // std::cout << "Cloning " << this->base_automaton->getStates().size() << " states..." << std::endl;
            for (auto state = base_states.begin(); state != base_states.end(); ++state) {
                if ((*state)->getId() >= states.size()) {
                    states.resize((*state)->getId() + 1);
                }
                states[(*state)->getId()] = new State((*state)->getId(), (*state)->getName(), (*state)->isInitial(), (*state)->isMarked(), (*state)->getX(), (*state)->getY());
            }

            auto base_events = base_automaton->getEvents();
            // std::cout << "Cloning " << base_events.size() << " events..." << std::endl;
            for (auto event = base_events.begin(); event != base_events.end(); ++event) {
                if ((*event)->getId() >= events.size()) {
                    events.resize((*event)->getId() + 1);
                }
                events[(*event)->getId()] = new Event((*event)->getId(), (*event)->getName(), (*event)->isControllable(), (*event)->isObservable());
            }
            
            auto base_transitions = base_automaton->getTransitions();
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

            return new Automaton(events, transitions, states, states[base_automaton->getInitialState()->getId()]);
        }
};