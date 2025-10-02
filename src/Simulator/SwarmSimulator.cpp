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
#include "./DataCollectorInterface.cpp"

using robots_list = std::vector<Enki::EPuck*>;
using objects_list = std::vector<Enki::PhysicalObject*>;
using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;

class SwarmSimulator {
public:
    SwarmSimulator(int world_size) : world_size(world_size) {}

    void simulate(robots_list& robots, objects_list& objects, DataCollectorInterface* data_collector) {
        Enki::World world(this->world_size, this->world_size);
        double cost = 0.0;

        this->spawnRobots(robots, world);
        this->spawnObjects(objects, world);

        data_collector->collect();

        std::chrono::steady_clock::time_point start_time = std::chrono::steady_clock::now();
        std::chrono::steady_clock::time_point checkpoint_time;

        // 1800 steps at 10 steps/sec = 180s (GAUCI_a)
        for (int i = 0; i < 1800; ++i) {
            world.step(0.1, 10);

            data_collector->collect();
        }
        
        checkpoint_time = std::chrono::steady_clock::now();
        std::cout << " Time taken: " << std::chrono::duration_cast<std::chrono::milliseconds>(checkpoint_time - start_time).count() << "ms" << std::endl;
    }
private:
    int world_size;

    void spawnRobots(robots_list& robots, Enki::World& world) {
        std::random_device rand_dev;
        std::mt19937 generator(rand_dev());
        std::uniform_real_distribution<double> position_distr(10, this->world_size - 10); //gauci_a
        std::uniform_real_distribution<double> angle_distr(-M_PI, M_PI);

        for (auto &it : robots) {
            it->pos.x = position_distr(generator);
            it->pos.y = position_distr(generator);
            it->angle = angle_distr(generator);

            world.addObject(it);
        }
    }

    void spawnObjects(objects_list& objects, Enki::World& world) {
        std::random_device rand_dev;
        std::mt19937 generator(rand_dev());
        std::uniform_real_distribution<double> position_distr(10, this->world_size - 10); //gauci_a

        for (auto &it : objects) {
            it->pos = Enki::Point(position_distr(generator), position_distr(generator));
            world.addObject(it);
        }
    }
};

#endif