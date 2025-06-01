#include <enki/PhysicalEngine.h>
#include "./GeneticEPuck.cpp"
#include <iostream>
#include <vector>
#include <random>
#include <bitset>
using namespace std;
using individual_list = vector<GeneticEPuck*>;

class Simulator {
    private:
        individual_list createIndividuals(vector<bitset<32>> population) {
            individual_list individuals;

            random_device rand_dev;
            mt19937 generator(rand_dev());
            // TODO: parameterize world size
            uniform_real_distribution<double> position_distr(10, 300); //gauci_a
            uniform_real_distribution<double> angle_distr(-M_PI, M_PI);


            for (auto it = population.begin(); it != population.end(); ++it) {
                GeneticEPuck *robot = new GeneticEPuck(*it);
            
                robot->pos = Enki::Point(position_distr(generator), position_distr(generator));
                robot->angle = angle_distr(generator);

                individuals.push_back(robot);
            }
            
            return individuals;
        }

        Enki::Point findCentroid(individual_list robots) {
            double sum_x = 0;
            double sum_y = 0;

            for (auto it = robots.begin(); it != robots.end(); ++it) {
                sum_x += (*it)->pos.x;
                sum_y += (*it)->pos.y;
            }

            return {
                sum_x / robots.size(),
                sum_y / robots.size()
            };
        }

        double calculateQuadraticDistance(Enki::Point a, Enki::Point b) {
            return (pow((b.x - a.x), 2) + pow((b.y - a.y), 2));
        }

        double calculateDispersion(individual_list robots) {
            double normalizer = 1 / 54.76; // (1 / 4 * raio^2) raio = 3.7

            Enki::Point centroid = this->findCentroid(robots);

            double quadratic_distances_sum = 0.0;
            for (auto it = robots.begin(); it != robots.end(); ++it) {
                quadratic_distances_sum += calculateQuadraticDistance((*it)->pos, centroid);
            }
            cout << "qds = " << quadratic_distances_sum << endl;

            return normalizer * quadratic_distances_sum;
        }

    public:
        double simulate(vector<bitset<32>> population) {
            Enki::World world(316, 316); // gauci_a
            individual_list robots = this->createIndividuals(population);
            double fitness = 0.0;

            cout << "simulation beginning " << population[0] << endl;
            for (auto it = robots.begin(); it != robots.end(); ++it) {
                world.addObject(*it);
                //std::cout << "E-puck pos is ( x = "<< (*it)->pos.x << ", y =" << (*it)->pos.y << ", angle = " << (*it)->angle << ")" << std::endl;
            }
	
            // 1800 steps at 10 steps/sec = 180s (GAUCI_a)
            for (int i = 0; i < 1800; ++i) {
                world.step(0.1, 10);
                double t = i / 10;

                fitness += calculateDispersion(robots) * t;
                cout << "step fitness = " << fitness << endl;
            }

            return fitness;
        }
};