#ifndef AUTOMATON_PLAYER_CPP
#define AUTOMATON_PLAYER_CPP

#include <string>
#include <vector>
#include "Automaton.cpp"

class AutomatonPlayer {
    public:
        AutomatonPlayer(Automaton* automaton) : automaton(automaton), current_state(*(automaton->getInitialState())) {}

        std::string step() {
            std::vector<Event*> controllable_events;
            for (auto transition = this->automaton->getTransitions().begin(); transition != this->automaton->getTransitions().end(); ++transition) {
                if ((*transition)->getSource()->getId() == this->current_state.getId() && (*transition)->isControllable()) {
                    controllable_events.push_back((*transition)->getEvent());
                }
            }

            // Choose an event randomly
            if (!controllable_events.empty()) {
                int random_index = rand() % controllable_events.size();
                Event* chosen_event = controllable_events[random_index];
                this->dispatch(chosen_event->getName());
                return chosen_event->getName();
            }

            return "";
        }

        void dispatch(std::string event_name) {
            for (auto transition = this->automaton->getTransitions().begin(); transition != this->automaton->getTransitions().end(); ++transition) {
                if ((*transition)->getSource()->getId() == this->current_state.getId() && (*transition)->getEvent()->getName() == event_name) {
                    this->current_state = *(*transition)->getTarget();
                    return;
                }
            }
        }
    private:
        Automaton* automaton;
        State current_state;
};

#endif