#include <iostream>
#include <chrono>
#include <boost/dynamic_bitset.hpp>
#include <unordered_map>
#include "../../Automaton/AutomatonFactory.cpp"
#include "../../Genetics/GeneMap/GeneMapBuilder.cpp"
#include "../../Genetics/GeneMap/GeneMap.cpp"
#include "../../Genetics/Algorithm/GeneticAlgorithm.cpp"
#include "./GroupingEvaluator.cpp"
#include "../../Robots/BinaryEPuckFactory.cpp"
#include "../../Simulator/SwarmSimulator.cpp"
#include "./GroupingDataWriter.cpp"
#include "../../Automaton/AutomatonWriter.cpp"
#include "./GroupingParamDecoder.cpp"
using individual_type = boost::dynamic_bitset<>;
using event_params = std::unordered_map<std::string, std::pair<double, double>>;


const int WORLD_SIZE = 316; // World size of 316 taken from GAUCI_A
const int POPULATION_SIZE = 40;
const int SWARM_SIZE = 10;

std::string buildOutputDirPath() {
	auto t = std::time(nullptr);
	auto tm = *std::localtime(&t);
	std::ostringstream output_dir_oss;
	output_dir_oss << "./output/grouping/" << std::put_time(&tm, "%d-%m-%Y %H-%M-%S");
	return output_dir_oss.str();
}

int main(int argc, char *argv[]) {
	AutomatonFactory automaton_factory;

	std::cout << "Loading automaton from XML..." << std::endl;
	Automaton* automaton = automaton_factory.buildFromXMLFile("src/Scenarios/grouping/input/sync.xml");
	std::cout << "Automaton loaded successfully." << std::endl;

	GeneMapBuilder gene_map_builder;
	GeneMap gene_map = gene_map_builder.buildMapFromAutomaton(automaton);

	// TODO: remove hardcoded parameters once GeneMapBuilder is updated
	gene_map.addSection(8, "uint"); // speed v0_right
	gene_map.addSection(8, "uint"); // speed v0_left
	gene_map.addSection(8, "uint"); // speed v1_right
	gene_map.addSection(8, "uint"); // speed v1_left

	std::cout << "Gene map length: " << gene_map.getLength() << " bits." << std::endl;

	GroupingParamDecoder *param_decoder = new GroupingParamDecoder();
	BinaryEPuckFactory *robot_factory = new BinaryEPuckFactory(automaton, &automaton_factory, param_decoder);
	SwarmSimulator *simulator = new SwarmSimulator(WORLD_SIZE);

	GroupingDataWriter *data_writer = new GroupingDataWriter(buildOutputDirPath());
	GroupingEvaluator evaluator(simulator, SWARM_SIZE, robot_factory, data_writer);

	GeneticAlgorithm algorithm = GeneticAlgorithm(POPULATION_SIZE, gene_map, evaluator);
	std::cout << "Starting genetic algorithm..." << std::endl;
	individual_type best_individual = algorithm.run();

	Automaton best_automaton = *automaton_factory.buildModifiedAutomatonFromChromosome(best_individual, automaton);

	AutomatonWriter automaton_writer;
	automaton_writer.writeAutomatonToFile(best_automaton, "./output/grouping/best_automaton.xml");

	event_params best_event_params = param_decoder->decodeParams(best_individual);

	std::cout << "Best individual found: " << best_individual << std::endl;
	for (const auto& [event_name, speeds] : best_event_params) {
		std::cout << "Event " << event_name << ": v_right = " << speeds.first << ", v_left = " << speeds.second << std::endl;
	}

	std::cout << "Simulation finished." << std::endl;
	return 0;
}