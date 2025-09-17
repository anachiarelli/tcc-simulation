#include <vector>
#include <string>

class State {
    int id;
    std::string name;
    bool is_initial;
};

class EventParam {
    std::string event_param_type;
    float min;
    float max;
    float step;
};

class Event {
    int id;
    std::string name;
    bool is_controllable;
    std::vector<EventParam> event_params;
};

class Transition {
    State source;
    State target;
    Event event;
};

class Automaton {
    std::vector<Event> events;
    std::vector<Transition> transitions;
    std::vector<State> states;
    State initial_state;
};
