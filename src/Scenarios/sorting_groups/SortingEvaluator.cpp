#include "../../Genetics/Algorithm/EvaluatorInterface.cpp"
#include <boost/dynamic_bitset.hpp>
#include "../../Simulator/SwarmSimulator.cpp"
#include "../../Robots/TernaryEPuckFactory.cpp"
#include "./SortingDataWriter.cpp"
#include "./SortingDataCollector.cpp"
#include "enki/PhysicalEngine.h"
#include <cmath>

using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;
using objects_list = std::vector<Enki::PhysicalObject*>;

class SortingEvaluator : public EvaluatorInterface {
public:
	SortingEvaluator(SwarmSimulator *simulator, int swarm_size, int number_of_groups, int number_of_objects, TernaryEPuckFactory *robot_factory, SortingDataWriter *data_writer) :
		simulator(simulator),
		swarm_size(swarm_size),
		number_of_groups(number_of_groups),
		number_of_objects(number_of_objects),
		robot_factory(robot_factory),
		data_writer(data_writer) {}
	
	double evaluateFitness(const individual_type& individual, int id, int generation) override {
		population_type clones;
        std::vector<population_type> groups;
        std::vector<Enki::Color> colors = {
            Enki::Color(1.0, 0.0, 0.0, 1.0), // Red
            Enki::Color(0.0, 1.0, 0.0, 1.0), // Green
            Enki::Color(0.0, 0.0, 1.0, 1.0)  // Blue
        };

        for (int i = 0; i < number_of_groups; i++) {
            for (int i = 0; i < swarm_size; i++) {
                clones.push_back(individual);
            }   
        }

		std::cout << "Evaluating " << clones.size() << " clones of individual " << id << std::endl;

		std::vector<Enki::EPuck*> robots;
		objects_list objects;
		std::vector<double> all_fitness;
		std::vector<double> dispersions;
		SortingDataCollector* data_collector;

		for (int i = 0; i < 1; ++i) { // 10 runs per individual

            for (int j = 0; j < 3; j++) {
                for (const auto& clone : clones) {
                    auto robot = robot_factory->buildFromChromosome(clone);
                    robot->setColor(colors[j]);
                    robots.push_back(robot);
                }
            }

            // not used
			for (int j = 0; j < this->number_of_objects; ++j) {
				auto object = new Enki::PhysicalObject();
				object->setCylindric(5.0, 10.0, 35.0); // These cylinders have a diameter and a height of 10 cm. Their mass is approximately 35 g
				object->dryFrictionCoefficient = 0.58; // and their coefficient of static friction with the floor of our arena is approximately 0.58.
				object->setColor(Enki::Color(1.0, 1.0, 1.0, 1.0));
				objects.push_back(object);
			}
			
			data_collector = new SortingDataCollector(robots, objects);
			simulator->simulate(robots, objects, data_collector);
			
			// Objects dispersion over time
			for (auto &step : data_collector->getRobotsData()) {
                std::vector<std::vector<std::vector<double>>> groups_positions = {{}, {}, {}};
                for (auto &robot : step) {
                    if (robot[3] == 1.0) { // Red
                        groups_positions[0].push_back(robot);
                    } else if (robot[4] == 1.0) { // Green
                        groups_positions[1].push_back(robot);
                    } else if (robot[5] == 1.0) { // Blue
                        groups_positions[2].push_back(robot);
                    }
                }
                double dispersion = 0.0;
                for (auto &group : groups_positions) {
                    dispersion += calculateDispersion(group);
                }
				dispersions.push_back(dispersion);
			}

			// TODO: the total steps should not be hardcoded ---> Across 10 systematic experiments with 5 robots and 20 objects, on average, 86.5% of the objects were in one cluster after 10 minutes
			double cost = 0.0;
			for (int i = 0; i < 1000; ++i) {
				double t = i / 10.0;
				cost += dispersions[i] * t;
			}

			data_writer->writeRobotsPositions(generation, id, data_collector->getRobotsData(), individual, i);
			data_writer->writeObjectsPositions(generation, id, data_collector->getObjectsData(), individual, i);
			data_writer->writeDispersion(generation, id, dispersions, individual, i);
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
    int number_of_groups;
    int number_of_objects;
	TernaryEPuckFactory *robot_factory;
	SortingDataWriter *data_writer;

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