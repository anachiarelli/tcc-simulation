#ifndef EVALUATOR_INTERFACE_CPP
#define EVALUATOR_INTERFACE_CPP

#include <boost/dynamic_bitset.hpp>
using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;

class EvaluatorInterface {
public:
    virtual double evaluateFitness(const individual_type& individual, int id, int generation) = 0;
};

#endif // EVALUATOR_INTERFACE_CPP