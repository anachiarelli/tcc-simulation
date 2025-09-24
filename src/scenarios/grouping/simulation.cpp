#include <iostream>
#include "../../automaton/AutomatonFactory.cpp"

#include "./GA.cpp"

int main(int argc, char *argv[]) {
	AutomatonFactory automaton_factory;

	automaton_factory.buildFromXMLFile("input/sync.xml");

	// GA* algorithm = new GA(40);
	// algorithm->run();
}
