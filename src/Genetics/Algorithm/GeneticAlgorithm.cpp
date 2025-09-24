#include <vector>
#include <boost/dynamic_bitset.hpp>
#include <random>
#include <iostream>

#include "../GeneMap/GeneMap.cpp"

class GeneticAlgorithm {
public:
    GeneticAlgorithm(GeneMap gene_map, int population_size): gene_map(gene_map), population_size(population_size) {}
    void run() {
        std::vector<boost::dynamic_bitset<>> initial_population = this->createInitialPopulation();
    }
private:
    GeneMap gene_map;
    int population_size;

    std::vector<boost::dynamic_bitset<>> createInitialPopulation() {
        std::vector<boost::dynamic_bitset<>> population;

        std::random_device rand_dev;
        std::mt19937 generator(rand_dev());
        std::uniform_int_distribution<uint8_t> distr(0, 1);

        for (unsigned i = 0; i < this->population_size; ++i) {
            boost::dynamic_bitset<> chromosome(gene_map.getLength());
            for (size_t i = 0; i < gene_map.getLength(); ++i) {
                chromosome[i] = distr(generator);
            }
            population.push_back(chromosome);
        }

        // print population for debugging
        for (const auto& individual : population) {
            std::cout << individual << std::endl;
        }

        return population;
    }
};