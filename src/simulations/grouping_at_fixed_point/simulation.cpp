#include <enki/PhysicalEngine.h>
#include <enki/robots/e-puck/EPuck.h>
#include <iostream>
#include <vector>
#include <random>
using namespace std;

int main(int argc, char *argv[])
{
	// Create the world
	const int world_size = 200;
	Enki::World world(world_size, world_size);
	
	vector<Enki::EPuck*> robots;

    random_device rand_dev;
    mt19937 generator(rand_dev());
    uniform_int_distribution<int> distr(0, world_size);

	for (unsigned i = 0; i < 40; ++i) {
		Enki::EPuck *ePuck = new Enki::EPuck;
		ePuck->pos = Enki::Point(distr(generator), distr(generator));
		robots.push_back(ePuck);
		world.addObject(ePuck);
	}

	for (auto it = robots.begin(); it != robots.end(); ++it) {
		cout << (*it)->pos.x << "," << (*it)->pos.y << "\n";
	}
}

