#ifndef AUTOMATON_CPP
#define AUTOMATON_CPP 1

#include <vector>
#include <string>

class State {
    int id;
    std::string name;
    bool is_initial;
    bool is_marked;
    int x;
    int y;
    public:
        State(int id, std::string name, bool is_initial, bool is_marked, int x, int y) : id(id), name(name), is_initial(is_initial), is_marked(is_marked), x(x), y(y) {}
        int getId() const { return id; }
        std::string getName() const { return name; }
        bool isInitial() const { return is_initial; }
        bool isMarked()  const { return is_marked; }
        int getX() const { return x; }
        int getY() const { return y; }
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
    bool is_observable;
    // std::vector<EventParam> event_params;
    public:
        Event(int id, std::string name, bool is_controllable, bool is_observable) : id(id), name(name), is_controllable(is_controllable), is_observable(is_observable) {}
        int getId() const { return id; }
        std::string getName() const { return name; }
        bool isControllable() const { return is_controllable; }
        bool isObservable() const { return is_observable; }
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
        bool isObservable() const { return event->isObservable(); }
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