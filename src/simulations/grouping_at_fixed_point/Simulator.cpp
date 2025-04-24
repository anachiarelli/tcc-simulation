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
            uniform_real_distribution<double> position_distr(10, 190);
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
            return sqrt(pow((b.x - a.x), 2) + pow((b.y - a.y), 2));
        }

    public:
        vector<double> simulate(vector<bitset<32>> population) {
            Enki::World world(200, 200);

            individual_list robots = this->createIndividuals(population);
            vector<double> fitness;

            for (auto it = robots.begin(); it != robots.end(); ++it) {
                world.addObject(*it);
                fitness.push_back(0);
                // std::cout << "E-puck pos is ( x = "<< (*it)->pos.x << ", y =" << (*it)->pos.y << ", angle = " << (*it)->angle << ")" << std::endl;
            }
	
            // Run for 10 minutes - 4 step/second to match the camera's frame rate (4 fps)
            for (int i = 0; i < 24000; ++i) {
                world.step(0.1, 5);

                Enki::Point centroid = this->findCentroid(robots);
                double distances_sum = 0;

                for (auto it = robots.begin(); it != robots.end(); ++it) {
                    double quadratic_distance = calculateQuadraticDistance((*it)->pos, centroid);
                    distances_sum += quadratic_distance;
                }

                auto f = fitness.begin();
                double distances_avg = distances_sum / robots.size();
                for (auto it = robots.begin(); it != robots.end(); ++it) {
                    double quadratic_distance = calculateQuadraticDistance((*it)->pos, centroid);
                    (*f) += 1 / (distances_avg + quadratic_distance);  
                    ++f;
                }

            }

            return fitness;
        }
};