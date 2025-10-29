#include <iostream>
#include <boost/dynamic_bitset.hpp>
#include "../../Automaton/AutomatonFactory.cpp"
#include "../../Genetics/GeneMap/GeneMapBuilder.cpp"
#include "../../Genetics/GeneMap/GeneMap.cpp"
#include "../../Genetics/Algorithm/GeneticAlgorithm.cpp"
#include "./SortingEvaluator.cpp"
#include "./SortingDataWriter.cpp"
#include "../../Robots/TernaryEPuckFactory.cpp"
#include "../../Simulator/SwarmSimulator.cpp"
#include "../../Automaton/AutomatonWriter.cpp"
#include "./SortingGroupsParamDecoder.cpp"

const int SWARM_SIZE = 30; // In each trial, r = 30 robots
const int NUMBER_OF_GROUPS = 3;
const int GROUP_SIZE = 10;
const int NUMBER_OF_OBJECTS = 0; // and no objects
const int WORLD_SIZE = 450; // The objects and the robots were initialized with a uniform distribution in a virtual square of sides 450 cm
const int POPULATION_SIZE = 10;

std::string buildOutputDirPath() {
	auto t = std::time(nullptr);
	auto tm = *std::localtime(&t);
	std::ostringstream output_dir_oss;
	output_dir_oss << "./output/sorting_groups/" << std::put_time(&tm, "%d-%m-%Y %H-%M-%S");
	return output_dir_oss.str();
}

int main(int argc, char *argv[]) {
	AutomatonFactory automaton_factory;

	std::cout << "Loading automaton from XML..." << std::endl;
	Automaton* automaton = automaton_factory.buildFromXMLFile("src/Scenarios/sorting_groups/input/sync.xml");
	std::cout << "Automaton loaded successfully." << std::endl;

	GeneMapBuilder gene_map_builder;
	GeneMap gene_map = gene_map_builder.buildMapFromAutomaton(automaton);

	std::cout << "Gene map length: " << gene_map.getLength() << " bits." << std::endl;

	// TODO: remove hardcoded parameters once GeneMapBuilder is updated
	gene_map.addSection(8, "uint"); // speed v0_right -> wall
	gene_map.addSection(8, "uint"); // speed v0_left -> wall
	gene_map.addSection(8, "uint"); // speed v1_right -> same color robot
	gene_map.addSection(8, "uint"); // speed v1_left -> same color robot
	gene_map.addSection(8, "uint"); // speed v2_right -> object
	gene_map.addSection(8, "uint"); // speed v2_left -> object

	std::cout << "Gene map length: " << gene_map.getLength() << " bits." << std::endl;

	SortingGroupsParamDecoder *param_decoder = new SortingGroupsParamDecoder();
	TernaryEPuckFactory *robot_factory = new TernaryEPuckFactory(automaton, &automaton_factory, param_decoder);
	SwarmSimulator *simulator = new SwarmSimulator(WORLD_SIZE);

	SortingDataWriter *data_writer = new SortingDataWriter(buildOutputDirPath());
	SortingEvaluator evaluator(simulator, GROUP_SIZE, NUMBER_OF_GROUPS, NUMBER_OF_OBJECTS, robot_factory, data_writer);

	GeneticAlgorithm algorithm = GeneticAlgorithm(POPULATION_SIZE, gene_map, evaluator);
	std::cout << "Starting genetic algorithm..." << std::endl;
	individual_type best_individual = algorithm.run();

	Automaton best_automaton = *automaton_factory.buildModifiedAutomatonFromChromosome(best_individual, automaton);

	AutomatonWriter automaton_writer;
	automaton_writer.writeAutomatonToFile(best_automaton, "./output/sorting_groups/best_automaton.xml");

	event_params best_event_params = param_decoder->decodeParams(best_individual);

	std::cout << "Best individual found: " << best_individual << std::endl;
	for (const auto& [event_name, speeds] : best_event_params) {
		std::cout << "Event " << event_name << ": v_right = " << speeds.first << ", v_left = " << speeds.second << std::endl;
	}

	std::cout << "Simulation finished." << std::endl;
	return 0;
}
