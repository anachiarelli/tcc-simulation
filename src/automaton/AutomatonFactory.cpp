#include "Automaton.cpp"
#include <string>
#include <pugixml.hpp>
#include <iostream>
#include <stdexcept>
#include <vector>

class AutomatonFactory {
    public:
        Automaton buildFromXMLFile(const char* path) {
            pugi::xml_document doc;
            pugi::xml_parse_result result = doc.load_file(path);
            if (!result) {
                throw std::runtime_error(result.description());
            }

            // Automaton automaton;

            std::vector<State> states;

            for (pugi::xml_node state : doc.child("model").child("data").children("state")) {
                int id = state.attribute("id").as_int();
                std::string name = state.attribute("name").as_string();
                bool is_initial = state.attribute("initial").as_bool();

                std::cout << "state: " << id << ", " << name << ", " << is_initial << std::endl;
            }

            for (pugi::xml_node event : doc.child("model").child("data").children("event")) {
                int id = event.attribute("id").as_int();
                std::string name = event.attribute("name").as_string();
                bool is_controllable = event.attribute("controllable").as_bool();

                std::cout << "event: " << id << ", " << name << ", " << is_controllable << std::endl;
            }

            for (pugi::xml_node transition : doc.child("model").child("data").children("transition")) {
                int source = transition.attribute("source").as_int();
                int target = transition.attribute("target").as_int();
                int event = transition.attribute("event").as_int();

                std::cout << "transition: " << source << ", " << target << ", " << event << std::endl;
            }

            std::cout << "ok" << std::endl;
            return Automaton();
        }
};