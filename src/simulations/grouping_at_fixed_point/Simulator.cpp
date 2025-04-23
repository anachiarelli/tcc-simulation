#include <enki/PhysicalEngine.h>
#include "./ControlledEPuck.cpp"
#include <iostream>
#include <vector>
#include <bitset>
using namespace std;

class Simulator {
    public:
        vector<float> simulate(vector<bitset<32>> population) {
            Enki::World world(200, 200);
            ControlledEPuck *robot = new ControlledEPuck();
            robot->leftSpeed = 12.8;
            robot->rightSpeed = 12.8;
            robot->pos = Enki::Point(100, 100);

            world.addObject(robot);
	
            // Run for some times
            for (unsigned i=0; i<160; i++)
            {
                // step of 50 ms
                world.step(0.05);
                std::cout << "E-puck pos is (" << robot->pos.x << "," << robot->pos.y << ")" << std::endl;
            }
            cout << endl;
            return {};
        }
};