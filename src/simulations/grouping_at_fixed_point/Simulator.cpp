#include <enki/PhysicalEngine.h>
#include "./GeneticEPuck.cpp"
#include <iostream>
#include <fstream>
#include <vector>
#include <random>
#include <bitset>
#include <filesystem>
using namespace std;
using individual_list = vector<GeneticEPuck*>;

class Simulator {
    private:
        int world_size;

        individual_list createIndividuals(vector<bitset<32>> population) {
            individual_list individuals;

            random_device rand_dev;
            mt19937 generator(rand_dev());
            uniform_real_distribution<double> position_distr(10, this->world_size - 10); //gauci_a
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
            
            return normalizer * quadratic_distances_sum;
        }

    public:
        Simulator(int world_size) {
            this->world_size = world_size;
        }

        double simulate(vector<bitset<32>> population, string simulation_name, string output_dir) {
            Enki::World world(this->world_size, this->world_size);
            individual_list robots = this->createIndividuals(population);
            double cost = 0.0;

            filesystem::create_directory(output_dir + "/positions");
            filesystem::create_directory(output_dir + "/dispersions");
            
            ofstream position_file(output_dir + "/positions/" + simulation_name);
            ofstream dispersion_file(output_dir + "/dispersions/" + simulation_name);

            // filesystem::path currentPath = filesystem::current_path();
            // cout << "Current Directory: " << currentPath << endl;
            
            if (!position_file.is_open()) {
                cerr << "Unable to open position file" << endl;
                exit(-1);
            }

            if (!dispersion_file.is_open()) {
                cerr << "Unable to open dispersion file" << endl;
                exit(-1);
            }

            cout << "Starting simulation for " << population[0] << " with world size " << this->world_size << endl;

            for (auto it = robots.begin(); it != robots.end(); ++it) {
                position_file << (*it)->pos.x << "," << (*it)->pos.y << ",";
                world.addObject(*it);
            }
            position_file << endl;

            double dispersion = calculateDispersion(robots);
            dispersion_file << dispersion << endl;
	
            // 1800 steps at 10 steps/sec = 180s (GAUCI_a)
            for (int i = 0; i < 1800; ++i) {
                world.step(0.1, 10);
                double t = i / 10.0;

                dispersion = calculateDispersion(robots);
                dispersion_file << dispersion << endl;
                cost += dispersion * t;
                
                for (auto it = robots.begin(); it != robots.end(); ++it) {
                    position_file << (*it)->pos.x << "," << (*it)->pos.y << ",";
                }
                position_file << endl;
            }

            // cout << "Final dispersion: " << calculateDispersion(robots) << endl;

            position_file.close();

            return cost;
        }
};