#include "../../Genetics/Algorithm/EvaluatorInterface.cpp"
#include <boost/dynamic_bitset.hpp>
#include "../../Simulator/SwarmSimulator.cpp"
#include "../../Robots/TernaryEPuckFactory.cpp"
#include "./SortingDataWriter.cpp"
#include "./SortingDataCollector.cpp"
#include "enki/PhysicalEngine.h"
#include <cmath>
#include "../../Geometry/GrahamScan.cpp"
#include "../../Geometry/Point.cpp"

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
		
		std::cout << "Evaluating clones of individual " << id << std::endl;
        std::vector<population_type> groups;
        std::vector<Enki::Color> colors = {
            Enki::Color(1.0, 0.0, 0.0, 1.0), // Red
            Enki::Color(0.0, 1.0, 0.0, 1.0), // Green
            Enki::Color(0.0, 0.0, 1.0, 1.0)  // Blue
        };

		std::vector<Enki::EPuck*> robots;
		objects_list objects;
		std::vector<double> all_fitness;
		std::vector<double> dispersion_by_step;
		std::vector<int> aliens_counts_by_step;
		SortingDataCollector* data_collector;

		for (int i = 0; i < 10; ++i) { // 10 runs per individual
            for (int j = 0; j < 3; j++) {
                 for (int k = 0; k < swarm_size; k++) {
                    auto robot = robot_factory->buildFromChromosome(individual);
                    robot->setColor(colors[j]);
                    robots.push_back(robot);
                }
            }

            // not used
			// for (int j = 0; j < this->number_of_objects; ++j) {
			// 	auto object = new Enki::PhysicalObject();
			// 	object->setCylindric(5.0, 10.0, 35.0); // These cylinders have a diameter and a height of 10 cm. Their mass is approximately 35 g
			// 	object->dryFrictionCoefficient = 0.58; // and their coefficient of static friction with the floor of our arena is approximately 0.58.
			// 	object->setColor(Enki::Color(1.0, 1.0, 1.0, 1.0));
			// 	objects.push_back(object);
			// }
			
			data_collector = new SortingDataCollector(robots, objects);
			simulator->simulate(robots, objects, data_collector);
			
			// Objects dispersion over time
			for (auto &step : data_collector->getRobotsData()) {
                std::vector<Points> coordinates_by_group = {{}, {}, {}};
                for (auto &robot_data : step) {
                    if (robot_data[3] == 1.0) { // Red
                        coordinates_by_group[0].push_back(Point(robot_data[0], robot_data[1]));
                    } else if (robot_data[4] == 1.0) { // Green
                        coordinates_by_group[1].push_back(Point(robot_data[0], robot_data[1]));
                    } else if (robot_data[5] == 1.0) { // Blue
                        coordinates_by_group[2].push_back(Point(robot_data[0], robot_data[1]));
                    }
                }

                double dispersion = 0.0;
                for (auto &group : coordinates_by_group) {
                    dispersion += calculateDispersion(group);
                }
				dispersion_by_step.push_back(dispersion);

				int aliens_count = countAliens(coordinates_by_group);
				aliens_counts_by_step.push_back(aliens_count);				
			}

			// TODO: the total steps should not be hardcoded ---> Across 10 systematic experiments with 5 robots and 20 objects, on average, 86.5% of the objects were in one cluster after 10 minutes
			double cost = 0.0;
			for (int i = 0; i < 1800; ++i) {
				double t = i / 10.0;
				cost += dispersion_by_step[i] * t * (1 + (aliens_counts_by_step[i] / 60.0)); 

			}

			data_writer->writeRobotsPositions(generation, id, data_collector->getRobotsData(), individual, i);
			// ->writeObjectsPositions(generation, id, data_collector->getObjectsData(), individual, i);
			// data_writer->writeDispersion(generation, id, dispersion_by_step, individual, i);
			double fitness = (1.0 / (1.0 + cost)) * 100000000; // Scaling to avoid very small numbers
			
			// Penalize fitness if there are any robots of another group inside the convex hull of each group

			
			all_fitness.push_back(fitness);

			delete(data_collector);
			dispersion_by_step.clear();
			aliens_counts_by_step.clear();

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

	int pnpoly(Points vertices, Point point) {
		int i, j, c = 0;
		for (i = 0, j = vertices.size() - 1; i < vertices.size(); j = i++) {
			if (
				((vertices[i].getY() > point.getY()) != (vertices[j].getY() > point.getY()))
				&& (point.getX() < (vertices[j].getX() - vertices[i].getX()) * (point.getY() - vertices[i].getY()) / (vertices[j].getY() - vertices[i].getY()) + vertices[i].getX())
			) {
				c = !c;
			}
		}
		return c;
	}

	int countAliens(std::vector<Points> coordinates_by_group) {
		std::vector<Points> convex_hulls;
		for (auto &group : coordinates_by_group) {
			convex_hulls.push_back(GrahamScan::computeConvexHull(group));
		}

		int alien_count = 0;
		// For each group, check how many robots from other groups are inside its convex hull
		for (int g = 0; g < coordinates_by_group.size(); g++) {
			for (int other_g = 0; other_g < coordinates_by_group.size(); other_g++) {
				if (g == other_g) continue;

				// Check if any point from the other group is inside the convex hull of the current group
				for (auto &point : coordinates_by_group[other_g]) {
					if (pnpoly(convex_hulls[g], point)) {
						alien_count++;
					}
				}
			}
		}

		// // print all coordinates for each group and its convex hull
		// for (int g = 0; g < coordinates_by_group.size(); g++) {
		// 	std::cout << "Group " << g << " coordinates:" << std::endl;
		// 	for (auto &point : coordinates_by_group[g]) {
		// 		std::cout << "(" << point.getX() << ", " << point.getY() << ")" << std::endl;
		// 	}
		// 	std::cout << "Group " << g << " convex hull:" << std::endl;
		// 	for (auto &point : convex_hulls[g]) {
		// 		std::cout << "(" << point.getX() << ", " << point.getY() << ")" << std::endl;
		// 	}
		// }

		// std::cout << "Alien count: " << alien_count << std::endl;

		// throw std::runtime_error("Stopping after aliens computation");
		return alien_count;
	}

	Point findCentroid(Points positions) {
        double sum_x = 0;
        double sum_y = 0;

        for (auto it = positions.begin(); it != positions.end(); ++it) {
            sum_x += it->getX();
            sum_y += it->getY();
        }

        return {
            sum_x / positions.size(),
            sum_y / positions.size()
        };
    }

    double calculateQuadraticDistance(Point a, Point b) {
        return (pow((b.getX() - a.getX()), 2) + pow((b.getY() - a.getY()), 2));
    }

    double calculateDispersion(Points positions) {
        double normalizer = 1 / 54.76; // (1 / 4 * raio^2) raio = 3.7

        Point centroid = findCentroid(positions);

        double quadratic_distances_sum = 0.0;
        for (auto it = positions.begin(); it != positions.end(); ++it) {
            quadratic_distances_sum += calculateQuadraticDistance((*it), centroid);
        }
        
        return normalizer * quadratic_distances_sum;
    }
};