#ifndef EVALUATOR_INTERFACE_CPP
#define EVALUATOR_INTERFACE_CPP

#include <boost/dynamic_bitset.hpp>

class EvaluatorInterface {
public:
    virtual double evaluateFitness(const boost::dynamic_bitset<>& individual) = 0;
};

#endif // EVALUATOR_INTERFACE_CPP