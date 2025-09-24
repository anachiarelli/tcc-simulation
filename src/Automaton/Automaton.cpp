#ifndef AUTOMATON_CPP
#define AUTOMATON_CPP 1

#include <vector>
#include <string>

class State {
    int id;
    std::string name;
    bool is_initial;
    public:
        State(int id, std::string name, bool is_initial) : id(id), name(name), is_initial(is_initial) {}
        int getId() const { return id; }
        std::string getName() const { return name; }
        bool isInitial() const { return is_initial; }    
};

/* class EventParam {
    std::string event_param_type;
    float min;
    float max;
    float step;
};
 */

 class Event {
    int id;
    std::string name;
    bool is_controllable;
    // std::vector<EventParam> event_params;
    public:
        Event(int id, std::string name, bool is_controllable) : id(id), name(name), is_controllable(is_controllable) {}
        int getId() const { return id; }
        std::string getName() const { return name; }
        bool isControllable() const { return is_controllable; }
};

class Transition {
    State* source;
    State* target;
    Event* event;
    public:
        Transition(State* source, State* target, Event* event) : source(source), target(target), event(event) {}
        State* getSource() const { return source; }
        State* getTarget() const { return target; }
        Event* getEvent() const { return event; }
        bool isControllable() const { return event->isControllable(); }
};

class Automaton {
    std::vector<Event*> events;
    std::vector<Transition*> transitions;
    std::vector<State*> states;
    State* initial_state;
    public:
        Automaton(std::vector<Event*> events, std::vector<Transition*> transitions, std::vector<State*> states, State* initial_state)
            : events(events), transitions(transitions), states(states), initial_state(initial_state) {}
        std::vector<Event*> getEvents() const { return events; }
        std::vector<Transition*> getTransitions() const { return transitions; }
        std::vector<State*> getStates() const { return states; }
        State* getInitialState() const { return initial_state; }
};

#endif // AUTOMATON_CPP