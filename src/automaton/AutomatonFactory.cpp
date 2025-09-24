#include "Automaton.cpp"
#include <string>
#include <pugixml.hpp>
#include <iostream>
#include <stdexcept>
#include <vector>

class AutomatonFactory {
    public:
        Automaton buildFromXMLFile(const char* path) {
            std::vector<State> states;
            std::vector<Event> events;
            std::vector<Transition> transitions;

            pugi::xml_document doc;
            pugi::xml_parse_result result = doc.load_file(path);
            if (!result) {
                throw std::runtime_error(result.description());
            }

            // Automaton automaton;

            int initial_state_id = -1;
            for (pugi::xml_node state : doc.child("model").child("data").children("state")) {
                int id = state.attribute("id").as_int();
                std::string name = state.attribute("name").as_string();
                bool is_initial = state.attribute("initial").as_bool();

                if (is_initial) {
                    initial_state_id = id;
                }

                if (id >= states.size()) {
                    states.resize(id + 1);
                }

                states[id] = State(id, name, is_initial);
            }

            for (pugi::xml_node event : doc.child("model").child("data").children("event")) {
                int id = event.attribute("id").as_int();
                std::string name = event.attribute("name").as_string();
                bool is_controllable = event.attribute("controllable").as_bool();

                events[id] = Event(id, name, is_controllable);
            }

            for (pugi::xml_node transition : doc.child("model").child("data").children("transition")) {
                int source = transition.attribute("source").as_int();
                int target = transition.attribute("target").as_int();
                int event = transition.attribute("event").as_int();

                transitions.push_back(Transition(states[source], states[target], events[event]));
            }

            if (initial_state_id == -1) {
                throw std::runtime_error("No initial state defined in the automaton.");
            }
            
            Automaton automaton(events, transitions, states, states[initial_state_id]);
            return automaton;
        }
};