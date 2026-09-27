#ifndef AUTOMATONWRITER_CPP
#define AUTOMATONWRITER_CPP

#include <fstream>
#include <string>
#include "../Automaton/Automaton.cpp"

class AutomatonWriter {
    public:
        static void writeAutomatonToFile(const Automaton& automaton, const std::string& file_path) {
            std::ofstream file(file_path);
            if (!file.is_open()) {
                throw std::runtime_error("Could not open file for writing: " + file_path);
            }

            file << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
            file << "<model version=\"0.0\" type=\"FSA\" id=\"Untitled\">\n";
            file << "<data>\n";
            // Write states
            for (const auto& state : automaton.getStates()) {
                file << "<state id=\"" << state->getId() << "\""
                     << " name=\"" << state->getName() << "\""
                     << " initial=\"" << (state->isInitial() ? "True" : "False") << "\""
                     << " marked=\"" << (state->isMarked() ? "True" : "False") << "\""
                     << " x=\"" << state->getX() << "\""
                     << " y=\"" << state->getY() << "\""
                     << "/>\n";
            }

            // Write events
            for (const auto& event : automaton.getEvents()) {
                file << "<event id=\"" << event->getId() << "\""
                     << " name=\"" << event->getName() << "\""
                     << " controllable=\"" << (event->isControllable() ? "True" : "False") << "\""
                     << " observable=\"" << (event->isObservable() ? "True" : "False") << "\""
                     << "/>\n";
            }

            // Write transitions
            for (const auto& transition : automaton.getTransitions()) {
                file << "<transition source=\"" << transition->getSource()->getId() << "\""
                     << " target=\"" << transition->getTarget()->getId() << "\""
                     << " event=\"" << transition->getEvent()->getId() << "\""
                     << "/>\n";
            }

            file << "</data>\n";
            file << "</model>\n";

            file.close();
        }

};
#endif // AUTOMATONWRITER_CPP