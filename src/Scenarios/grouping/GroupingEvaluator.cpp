#include "../../Genetics/Algorithm/EvaluatorInterface.cpp"
#include <boost/dynamic_bitset.hpp>

class GroupingEvaluator : public EvaluatorInterface {
public:
	double evaluateFitness(const boost::dynamic_bitset<>& individual) override {
		// Example fitness function: count the number of 1s in the bitset
		return individual.count();
	}
};