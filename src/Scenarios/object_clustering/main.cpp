#include <iostream>
#include <boost/dynamic_bitset.hpp>
#include <chrono>
#include "../../Automaton/AutomatonFactory.cpp"
#include "../../Genetics/GeneMap/GeneMapBuilder.cpp"
#include "../../Genetics/GeneMap/GeneMap.cpp"
#include "../../Genetics/Algorithm/GeneticAlgorithm.cpp"
#include "./ClusteringEvaluator.cpp"
#include "../../Robots/TernaryEPuckFactory.cpp"
#include "../../Simulator/SwarmSimulator.cpp"
#include "../../Automaton/AutomatonWriter.cpp"
#include "./ObjectClusteringParamDecoder.cpp"

const int WORLD_SIZE = 112; // The objects and the robots were initialized with a uniform distribution in a virtual square of sides 111.80 cm
const int POPULATION_SIZE = 40; // In each generation, each of the λ = 40 candidate solutions (i.e. controllers) was evaluated by running it for 100 s on
const int SWARM_SIZE = 2; // n = 2 robots in an environment containing
const int NUMBER_OF_OBJECTS = 5; // m = 5 objects.

std::string buildOutputDirPath() {
	auto t = std::time(nullptr);
	auto tm = *std::localtime(&t);
	std::ostringstream output_dir_oss;
	output_dir_oss << "./output/object_clustering/" << std::put_time(&tm, "%d-%m-%Y %H-%M-%S");
	return output_dir_oss.str();
}

int main(int argc, char *argv[]) {
	AutomatonFactory automaton_factory;

	std::cout << "Loading automaton from XML..." << std::endl;
	Automaton* automaton = automaton_factory.buildFromXMLFile("src/Scenarios/object_clustering/input/sync.xml");
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

	ObjectClusteringParamDecoder *param_decoder = new ObjectClusteringParamDecoder();
	TernaryEPuckFactory *robot_factory = new TernaryEPuckFactory(automaton, &automaton_factory, param_decoder);
	SwarmSimulator *simulator = new SwarmSimulator(WORLD_SIZE);

	ClusteringDataWriter *data_writer = new ClusteringDataWriter(buildOutputDirPath());
	ClusteringEvaluator evaluator(simulator, SWARM_SIZE, NUMBER_OF_OBJECTS, robot_factory, data_writer);

	GeneticAlgorithm algorithm = GeneticAlgorithm(POPULATION_SIZE, gene_map, evaluator);
	std::cout << "Starting genetic algorithm..." << std::endl;
	individual_type best_individual = algorithm.run();

	Automaton best_automaton = *automaton_factory.buildModifiedAutomatonFromChromosome(best_individual, automaton);

	AutomatonWriter automaton_writer;
	automaton_writer.writeAutomatonToFile(best_automaton, "./output/object_clustering/best_automaton.xml");

	event_params best_event_params = param_decoder->decodeParams(best_individual);

	std::cout << "Best individual found: " << best_individual << std::endl;
	for (const auto& [event_name, speeds] : best_event_params) {
		std::cout << "Event " << event_name << ": v_right = " << speeds.first << ", v_left = " << speeds.second << std::endl;
	}


	std::cout << "Simulation finished." << std::endl;
	return 0;
}
