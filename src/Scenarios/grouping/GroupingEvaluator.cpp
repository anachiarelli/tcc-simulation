#include "../../Genetics/Algorithm/EvaluatorInterface.cpp"
#include <boost/dynamic_bitset.hpp>
#include "../../Simulator/SwarmSimulator.cpp"
#include "../../Robots/BinaryEPuckFactory.cpp"
#include "./GroupingDataWriter.cpp"
#include "./GroupingDataCollector.cpp"

using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;

class GroupingEvaluator : public EvaluatorInterface {
public:
	GroupingEvaluator(SwarmSimulator *simulator, int swarm_size, BinaryEPuckFactory *robot_factory, GroupingDataWriter *data_writer) :
		simulator(simulator),
		swarm_size(swarm_size),
		robot_factory(robot_factory),
		data_writer(data_writer) {}
	
	double evaluateFitness(const individual_type& individual, int id, int generation) override {
		population_type clones;

		for (int i = 0; i < swarm_size; i++) {
			clones.push_back(individual);
		}

		std::cout << "Evaluating " << clones.size() << " clones of individual " << id << std::endl;
		
		std::vector<Enki::EPuck*> robots;
		GroupingDataCollector* data_collector;
		std::vector<Enki::PhysicalObject*> objects;
		std::vector<double> dispersions;
		std::vector<double> all_fitness;
		
		for (int i = 0; i < 10; ++i) {
			for (const auto& clone : clones) {
				auto robot = robot_factory->buildFromChromosome(clone);
				robots.push_back(robot);
			}

			data_collector = new GroupingDataCollector(robots);
			simulator->simulate(robots, objects, data_collector);

			for (auto &step : data_collector->getData()) {
				dispersions.push_back(calculateDispersion(step));
			}

			// TODO: the total steps should not be hardcoded
			double cost = 0.0;
			for (int i = 0; i < 1800; ++i) {
				double t = i / 10.0;
				cost += dispersions[i] * t;
			}

			data_writer->writePositions(generation, id, data_collector->getData(), individual, i);
			// data_writer->writeDispersion(generation, id, dispersions, individual, i);

			// Setting fitness to 1/(1 + cost), as the algorithm's goal is to maximize it
			double fitness = (1.0 / (1.0 + cost)) * 100000000; // Scaling to avoid very small numbers
			all_fitness.push_back(fitness);

			delete(data_collector);
			dispersions.clear();
			robots.clear();
			objects.clear();

		}
		
		return std::accumulate(all_fitness.begin(), all_fitness.end(), 0.0) / all_fitness.size();
	}

	std::vector<double> evaluatePopulation(const population_type& population, int generation) override {
		std::vector<double> fitness_values = EvaluatorInterface::evaluatePopulation(population, generation);
		this->data_writer->writeFitness(generation, fitness_values);

		return fitness_values;
	}

private:
	SwarmSimulator *simulator;
	int swarm_size;
	BinaryEPuckFactory *robot_factory;
	GroupingDataWriter *data_writer;

	std::vector<double> findCentroid(std::vector<std::vector<double>> positions) {
        double sum_x = 0;
        double sum_y = 0;

        for (auto it = positions.begin(); it != positions.end(); ++it) {
            sum_x += (*it)[0];
            sum_y += (*it)[1];
        }

        return {
            sum_x / positions.size(),
            sum_y / positions.size()
        };
    }

    double calculateQuadraticDistance(std::vector<double> a, std::vector<double> b) {
        return (pow((b[0] - a[0]), 2) + pow((b[1] - a[1]), 2));
    }

    double calculateDispersion(std::vector<std::vector<double>> positions) {
        double normalizer = 1 / 54.76; // (1 / 4 * raio^2) raio = 3.7

        std::vector<double> centroid = this->findCentroid(positions);

        double quadratic_distances_sum = 0.0;
        for (auto it = positions.begin(); it != positions.end(); ++it) {
            quadratic_distances_sum += calculateQuadraticDistance((*it), centroid);
        }
        
        return normalizer * quadratic_distances_sum;
    }
};