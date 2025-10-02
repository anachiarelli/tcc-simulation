#ifndef EVALUATOR_INTERFACE_CPP
#define EVALUATOR_INTERFACE_CPP

#include <boost/dynamic_bitset.hpp>
using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;

class EvaluatorInterface {
public:
    virtual double evaluateFitness(const individual_type& individual, int id, int generation) = 0;

    virtual std::vector<double> evaluatePopulation(const population_type& population, int generation) {
        std::vector<double> fitness_values;
        for (int i = 0; i < population.size(); ++i) {
            fitness_values.push_back(this->evaluateFitness(population[i], i, generation));
        }
        return fitness_values;
    }
};

#endif // EVALUATOR_INTERFACE_CPPs