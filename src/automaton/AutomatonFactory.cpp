#include "Automaton.cpp"
#include <string>
#include <pugixml/src/pugixml.hpp>
#include <iostream>
#include <stdexcept>

class AutomatonFactory {
    public:
        Automaton buildFromXMLFile(std::string path) {
            pugi::xml_document doc;
            pugi::xml_parse_result result = doc.load_file("input/sync.xml");
            if (!result) {
                throw std::runtime_error(result.description());
            }

            // Automaton automaton;

            for (pugi::xml_node event : doc.child("model").child("data").children("event")) {
                std::string name = event.attribute("name").as_string();
                std::cout << name << std::endl;
            }

            std::cout << "ok" << std::endl;
        }
};