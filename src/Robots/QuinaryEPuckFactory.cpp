#ifndef TERNARYEPUCKFACTORY_CPP
#define TERNARYEPUCKFACTORY_CPP

#include <boost/dynamic_bitset.hpp>
#include <unordered_map>
#include "../Automaton/Automaton.cpp"
#include "../Automaton/AutomatonPlayer.cpp"
#include "./QuinaryEPuck.cpp"
#include "../Automaton/AutomatonFactory.cpp"
#include "../Genetics/ParamDecoderInterface.cpp"
using individual_type = boost::dynamic_bitset<>;
using event_params = std::unordered_map<std::string, std::pair<double, double>>;

class QuinaryEPuckFactory {
public:
    QuinaryEPuckFactory(Automaton* base_automaton, AutomatonFactory* automaton_factory, ParamDecoderInterface* param_decoder) : base_automaton(base_automaton), automaton_factory(automaton_factory), param_decoder(param_decoder) {}

    QuinaryEPuck* buildFromChromosome(individual_type chromosome, Enki::Color interest_color, std::vector<Enki::Color> non_interest_colors) {
        // std::cout << "Building modified automaton for " << chromosome << std::endl;
        Automaton* automaton = this->automaton_factory->buildModifiedAutomatonFromChromosome(chromosome, this->base_automaton);
        // std::cout << "Building AutomatonPlayer." << std::endl;
        AutomatonPlayer* player = new AutomatonPlayer(automaton);
        // std::cout << "Building speeds_by_event." << std::endl;
        event_params speeds_by_event = this->param_decoder->decodeParams(chromosome);
        // std::cout << "Building QuinaryEPuck." << std::endl;
        Enki::Color epuck_color = Enki::Color(0.0, 0.0, 1.0, 1.0);
        return new QuinaryEPuck(player, speeds_by_event, epuck_color, interest_color, non_interest_colors);
    }

private:
    Automaton* base_automaton;
    AutomatonFactory* automaton_factory;
    ParamDecoderInterface* param_decoder;
};

#endif