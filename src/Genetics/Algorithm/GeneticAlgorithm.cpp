#include <vector>
#include <boost/dynamic_bitset.hpp>
#include <random>
#include <iostream>
#include "../GeneMap/GeneMap.cpp"
#include "EvaluatorInterface.cpp"
using individual_type = boost::dynamic_bitset<>;
using population_type = std::vector<individual_type>;

class GeneticAlgorithm {
public:
    GeneticAlgorithm(int population_size, GeneMap gene_map, EvaluatorInterface& evaluator)
        : gene_map(gene_map),
          population_size(population_size),
          evaluator(evaluator) {}
    
    void run() {
        population_type population = this->createInitialPopulation();
        std::vector<double> fitnesses = this->evaluatePopulation(population);
        // Print fitnesses for debugging
        for (int i = 0; i < fitnesses.size(); ++i) {
            std::cout << population[i] << " Fitness: " << fitnesses[i] << std::endl;
        }

        for (int i = 0; i < 100; i++) {
            population = this->createNextPopulation(population, fitnesses);
            fitnesses = this->evaluatePopulation(population);
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

    population_type createInitialPopulation() {
        population_type population;

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

    std::vector<double> evaluatePopulation(population_type population) {
        std::vector<double> fitnesses;

        for (const auto& individual : population) {
            double fitness = this->evaluator.evaluateFitness(individual);
            fitnesses.push_back(fitness);
        }

        return fitnesses;
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

        std::random_device rand_dev;
        std::mt19937 generator(rand_dev());
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
        std::random_device rand_dev;
        std::mt19937 generator(rand_dev());
        std::uniform_int_distribution<int> distr(0, 1);

        individual_type left_mask(gene_map.getLength());
        individual_type right_mask(gene_map.getLength());

        for (size_t i = 0; i < gene_map.getLength(); ++i) {
            int pick = distr(generator);
            if (pick == 0) {
                left_mask.flip(i);
            } else {
                right_mask.flip(i);
            }
        }

        individual_type genes_from_parent_1 = parent_1 & left_mask;
        individual_type genes_from_parent_2 = parent_2 & right_mask;

        individual_type child_1 = genes_from_parent_1 | genes_from_parent_2;
        individual_type child_2 = genes_from_parent_2 | genes_from_parent_1;

        int pick = distr(generator);

        return pick == 0 ? child_1 : child_2;
    }

    individual_type mutate(const individual_type& child) {
        double chance = 0.001;

        std::random_device rand_dev;
        std::mt19937 generator(rand_dev());
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
};