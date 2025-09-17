#include <enki/PhysicalEngine.h>
#include <enki/robots/e-puck/EPuck.h>
#include <iostream>
#include <vector>
#include <random>
#include <bitset>

#include "./GA.cpp"

using namespace std;

int main(int argc, char *argv[])
{
	GA* algorithm = new GA(40);
	algorithm->run();
}
