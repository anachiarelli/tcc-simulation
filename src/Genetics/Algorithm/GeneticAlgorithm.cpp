#include <vector>
#include <boost/dynamic_bitset.hpp>
#include <random>
#include <iostream>
#include <string>
#include <fstream>
#include <filesystem>
#include "../GeneMap/GeneMap.cpp"
#include "EvaluatorInterface.cpp"
using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;

class GeneticAlgorithm {
public:
    GeneticAlgorithm(int population_size, GeneMap gene_map, EvaluatorInterface& evaluator)
        : gene_map(gene_map),
          population_size(population_size),
          evaluator(evaluator) {
        std::random_device rand_dev;
        generator = std::mt19937(rand_dev());
    }
    
    void run() {
        population_type population = this->createInitialPopulation();
        std::cout << "Initial population created." << std::endl;
        // for (const auto& individual : population) {
        //     std::cout << individual << std::endl;
        // }

        std::vector<double> fitnesses = this->evaluatePopulation(population, 0);
        // Print fitnesses for debugging
        for (int i = 0; i < fitnesses.size(); ++i) {
            std::cout << population[i] << " Fitness: " << fitnesses[i] << std::endl;
        }

        // Clustering: Each evolution was run for 1000 generations. (GAUCI)
        for (int i = 1; i <= 200; i++) {
            population = this->createNextPopulation(population, fitnesses);
            fitnesses = this->evaluatePopulation(population, i);
            // Print fitnesses for debugging
            for (int j = 0; j < fitnesses.size(); ++j) {
                std::cout << i << " " << population[j] << " Fitness: " << fitnesses[j] << std::endl;
            }
        }
    }

private:
    int population_size;
    GeneMap gene_map;
    EvaluatorInterface& evaluator;

    std::mt19937 generator;
    std::uniform_int_distribution<int> bit_dist{0, 1};

    population_type createInitialPopulation() {
        population_type population;

        for (unsigned i = 0; i < this->population_size; ++i) {
            boost::dynamic_bitset<> chromosome(gene_map.getLength());
            for (size_t i = 0; i < gene_map.getLength(); ++i) {
                chromosome[i] = randomBit();
            }
            population.push_back(chromosome);
        }

        return population;
    }

    std::vector<double> evaluatePopulation(population_type population, int generation) {
        return this->evaluator.evaluatePopulation(population, generation);
    }

    population_type createNextPopulation(population_type current_population, std::vector<double> evaluation_result) {
        population_type next_population;
        double evaluation_sum = 0;

        int best_index = 0;
        for (int i = 0; i < evaluation_result.size(); ++i) {
            if (evaluation_result[best_index] < evaluation_result[i]) {
                best_index = i;
            }
            evaluation_sum += evaluation_result[i];
        }

        next_population.push_back(current_population[best_index]); // elitism
        for (int i = 0; i < current_population.size() - 1; ++i) {
            individual_type parent_1 = this->selectParent(current_population, evaluation_result, evaluation_sum);
            individual_type parent_2 = this->selectParent(current_population, evaluation_result, evaluation_sum);
            individual_type child = this->crossover(parent_1, parent_2);
            child = this->mutate(child);
            next_population.push_back(child);
        }

        return next_population;
    }

    individual_type selectParent(const population_type& population, const std::vector<double>& evaluation_result, double evaluation_sum) {
        std::uniform_real_distribution<double> distr(0, evaluation_sum);

        individual_type parent;
        double pick = distr(generator);

        for (size_t i = 0; i < population.size(); ++i) {
            pick -= evaluation_result[i];
            if (pick <= 0) {
                parent = population[i];
                break;
            }
        }

        return parent;
    }

    individual_type crossover(const individual_type& parent_1, const individual_type& parent_2) {
        individual_type left_mask(gene_map.getLength());
        individual_type right_mask(gene_map.getLength());

        for (size_t i = 0; i < gene_map.getLength(); ++i) {
            if (randomBit() == 0) {
                left_mask.flip(i);
            } else {
                right_mask.flip(i);
            }
        }
        individual_type child_1 = (parent_1 & left_mask) | (parent_2 & right_mask);
        individual_type child_2 = (parent_1 & right_mask) | (parent_2 & left_mask);

        return randomBit() == 0 ? child_1 : child_2;
    }

    individual_type mutate(const individual_type& child) {
        double chance = 0.005;
        
        std::uniform_real_distribution<double> distr(0, 1);
        individual_type mutated_child = child;

        for (size_t i = 0; i < gene_map.getLength(); ++i) {
            double pick = distr(generator);
            if (pick <= chance) {
                mutated_child.flip(i);
            }
        }

        return mutated_child;
    }

    int randomBit() {
        return bit_dist(generator);
    }
};