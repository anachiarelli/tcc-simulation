#include "../../Genetics/Algorithm/EvaluatorInterface.cpp"
#include <boost/dynamic_bitset.hpp>
#include "./SwarmSimulator.cpp"
using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;

class GroupingEvaluator : public EvaluatorInterface {
public:
	GroupingEvaluator(SwarmSimulator *simulator, int swarm_size) : simulator(simulator), swarm_size(swarm_size) {}
	double evaluateFitness(const individual_type& individual, int id, int generation) override {
		population_type clones;

		for (int i = 0; i < swarm_size; i++) {
			clones.push_back(individual);
		}

		std::cout << "Evaluating " << clones.size() << " clones of individual " << id << std::endl;

		string num_str = to_string(id);
		num_str = string(3 - num_str.length(), '0') + num_str;
		string buffer;
		boost::to_string(individual, buffer);
		string simulation_name = num_str + "_" + buffer;

		string generation_str = to_string(generation);
		generation_str = string(3 - generation_str.length(), '0') + generation_str;
		string output_dir = "/root/simulation/output/current/" + generation_str;

		std::cout << "Setting up output directory: " << output_dir << std::endl;
		double cost = simulator->simulate(clones, simulation_name, output_dir);

		// Setting fitness to 1/(1 + cost), as the algorithm's goal is to maximize it
		return (1.0 / (1.0 + cost));
	}
private:
	SwarmSimulator *simulator;
	int swarm_size;
};