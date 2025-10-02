#ifndef SWARMSIMULATOR_H
#define SWARMSIMULATOR_H

#include <enki/PhysicalEngine.h>
#include <enki/robots/e-puck/EPuck.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <random>
#include <bitset>
#include <filesystem>
#include <chrono>
#include <boost/dynamic_bitset.hpp>
using namespace std;
using robots_list = vector<Enki::EPuck*>;
using objects_list = vector<Enki::PhysicalObject*>;
using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;

class SwarmSimulator {
public:
    SwarmSimulator(int world_size) : world_size(world_size) {}

    double simulate(robots_list& robots, objects_list& objects, string simulation_name, string output_dir) {
        filesystem::create_directories(output_dir + "/positions");
        filesystem::create_directories(output_dir + "/dispersions");
        
        ofstream position_file(output_dir + "/positions/" + simulation_name);
        ofstream dispersion_file(output_dir + "/dispersions/" + simulation_name);
        
        if (!position_file.is_open()) {
            cerr << "Unable to open position file" << endl;
            exit(-1);
        }

        if (!dispersion_file.is_open()) {
            cerr << "Unable to open dispersion file" << endl;
            exit(-1);
        }

        Enki::World world(this->world_size, this->world_size);
        double cost = 0.0;

        this->spawnRobots(robots, world);

        for (auto it = robots.begin(); it != robots.end(); ++it) {
            position_file << (*it)->pos.x << "," << (*it)->pos.y << ",";
        }
        position_file << endl;

        // TODO: Save object positions to file
        this->spawnObjects(objects, world);
        
        double dispersion = calculateDispersion(objects);
        dispersion_file << dispersion << endl;

        std::chrono::steady_clock::time_point start_time = std::chrono::steady_clock::now();
        std::chrono::steady_clock::time_point checkpoint_time;

        // 1800 steps at 10 steps/sec = 180s (GAUCI_a)
        for (int i = 0; i < 1800; ++i) {
            world.step(0.1, 10);
            double t = i / 10.0;

            dispersion = calculateDispersion(objects);
            dispersion_file << dispersion << endl;
            cost += dispersion * t;
            
            for (auto it = robots.begin(); it != robots.end(); ++it) {
                position_file << (*it)->pos.x << "," << (*it)->pos.y << ",";
            }
            position_file << endl;
        }
        
        checkpoint_time = std::chrono::steady_clock::now();
        cout << "Final dispersion: " << calculateDispersion(objects) << " Time taken: " << std::chrono::duration_cast<std::chrono::milliseconds>(checkpoint_time - start_time).count() << "ms" << endl;

        position_file.close();

        return cost;
    }
private:
    int world_size;

    void spawnRobots(robots_list& robots, Enki::World& world) {
        random_device rand_dev;
        mt19937 generator(rand_dev());
        uniform_real_distribution<double> position_distr(10, this->world_size - 10); //gauci_a
        uniform_real_distribution<double> angle_distr(-M_PI, M_PI);

        for (auto &it : robots) {
            it->pos.x = position_distr(generator);
            it->pos.y = position_distr(generator);
            it->angle = angle_distr(generator);

            world.addObject(it);
        }
    }

    void spawnObjects(objects_list& objects, Enki::World& world) {
        random_device rand_dev;
        mt19937 generator(rand_dev());
        uniform_real_distribution<double> position_distr(10, this->world_size - 10); //gauci_a

        for (auto &it : objects) {
            it->pos = Enki::Point(position_distr(generator), position_distr(generator));
            world.addObject(it);
        }
    }

    Enki::Point findCentroid(objects_list objects) {
        double sum_x = 0;
        double sum_y = 0;

        for (auto it = objects.begin(); it != objects.end(); ++it) {
            sum_x += (*it)->pos.x;
            sum_y += (*it)->pos.y;
        }

        return {
            sum_x / objects.size(),
            sum_y / objects.size()
        };
    }

    double calculateQuadraticDistance(Enki::Point a, Enki::Point b) {
        return (pow((b.x - a.x), 2) + pow((b.y - a.y), 2));
    }

    double calculateDispersion(objects_list objects) {
        double normalizer = 1 / 54.76; // (1 / 4 * raio^2) raio = 3.7

        Enki::Point centroid = this->findCentroid(objects);

        double quadratic_distances_sum = 0.0;
        for (auto it = objects.begin(); it != objects.end(); ++it) {
            quadratic_distances_sum += calculateQuadraticDistance((*it)->pos, centroid);
        }
        
        return normalizer * quadratic_distances_sum;
    }
};

#endif