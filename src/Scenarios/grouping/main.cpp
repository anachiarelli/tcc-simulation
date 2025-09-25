#include <iostream>
#include <boost/dynamic_bitset.hpp>
#include "../../Automaton/AutomatonFactory.cpp"
#include "../../Genetics/GeneMap/GeneMapBuilder.cpp"
#include "../../Genetics/GeneMap/GeneMap.cpp"
#include "../../Genetics/Algorithm/GeneticAlgorithm.cpp"
#include "../../Scenarios/grouping/GroupingEvaluator.cpp"
#include "./ControlledEPuckFactory.cpp"

const int WORLD_SIZE = 316; // World size of 316 taken from GAUCI_A
const int POPULATION_SIZE = 40;
const int SWARM_SIZE = 10;

int main(int argc, char *argv[]) {
	AutomatonFactory automaton_factory;

	std::cout << "Loading automaton from XML..." << std::endl;
	Automaton* automaton = automaton_factory.buildFromXMLFile("input/sync.xml");
	std::cout << "Automaton loaded successfully." << std::endl;

	GeneMapBuilder gene_map_builder;
	GeneMap gene_map = gene_map_builder.buildMapFromAutomaton(automaton);

	// TODO: remove hardcoded parameters once GeneMapBuilder is updated
	gene_map.addSection(8, "uint"); // speed v0_right
	gene_map.addSection(8, "uint"); // speed v0_left
	gene_map.addSection(8, "uint"); // speed v1_right
	gene_map.addSection(8, "uint"); // speed v1_left

	std::cout << "Gene map length: " << gene_map.getLength() << " bits." << std::endl;

	boost::dynamic_bitset<> bitmask(gene_map.getLength());
	std::cout << "Bitmask length: " << bitmask.size() << " bits." << std::endl;

	ControlledEPuckFactory robot_factory(automaton);
	SwarmSimulator *simulator = new SwarmSimulator(WORLD_SIZE, robot_factory);
	GroupingEvaluator evaluator(simulator, SWARM_SIZE);
	GeneticAlgorithm algorithm = GeneticAlgorithm(POPULATION_SIZE, gene_map, evaluator);
	algorithm.run();

	std::cout << "Simulation finished." << std::endl;
	return 0;
}
