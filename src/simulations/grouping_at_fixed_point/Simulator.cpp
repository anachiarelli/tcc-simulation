#include <enki/PhysicalEngine.h>
#include "./ControlledEPuck.cpp"
#include <iostream>
#include <vector>
#include <random>
#include <bitset>
using namespace std;
using individual_list = vector<ControlledEPuck*>;

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
                ControlledEPuck *robot = new ControlledEPuck();
            
                robot->pos = Enki::Point(position_distr(generator), position_distr(generator));
                robot->angle = angle_distr(generator);

                individuals.push_back(robot);
            }
            
            return individuals;
        }

    public:
        vector<float> simulate(vector<bitset<32>> population) {
            Enki::World world(200, 200);
            vector<ControlledEPuck*> robots = this->createIndividuals(population);

            for (auto it = robots.begin(); it != robots.end(); ++it) {
                world.addObject(*it);
                std::cout << "E-puck pos is ( x = "<< (*it)->pos.x << ", y =" << (*it)->pos.y << ", angle = " << (*it)->angle << ")" << std::endl;
            }
	
            // Run for some times
            /* for (unsigned i=0; i<160; i++)
            {
                // step of 50 ms
                world.step(0.05);
                std::cout << "E-puck pos is (" << robot->pos.x << "," << robot->pos.y << ")" << std::endl;
            } */
            return {};
        }
};