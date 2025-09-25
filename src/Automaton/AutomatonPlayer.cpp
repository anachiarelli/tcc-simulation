#include "Automaton.cpp"

class AutomatonPlayer {
    public:
        AutomatonPlayer(Automaton* automaton) : automaton(automaton) {
            this->current_state = *(automaton->getInitialState());
        }

        void step() {

        }
    private:
        Automaton* automaton;
        State current_state;
};