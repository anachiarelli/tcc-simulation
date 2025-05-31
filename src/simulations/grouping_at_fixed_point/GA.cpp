#include <iostream>
#include <vector>
#include <random>
#include <bitset>
#include "./Simulator.cpp"
using namespace std;
using population_type = vector<bitset<32>>;

class GA {
    private:
        int population_size;

        population_type createInitialPopulation() {
            vector<bitset<32>> population;

            random_device rand_dev;
            mt19937 generator(rand_dev());
            uniform_int_distribution<uint8_t> distr(0, 1);

            for (unsigned i = 0; i < this->population_size; ++i) {
                bitset<32> chromosome;
                for (size_t i = 0; i < 32; ++i) {
                    chromosome[i] = distr(generator);
                }
                population.push_back(chromosome);
            }
            return population;
        }

        /**
         * @return positionally encoded list of fitness where the position of fitness matches the position of the individual in the given population vector
         */
        vector<double> evaluate_population(population_type population) {
            vector<double> fitnesses;

            for (auto p = population.begin(); p != population.end(); ++p) {
                Simulator *simulator = new Simulator();
                population_type clones;

                for (int i = 0; i < 25; i++) {
                    clones.push_back(*p);
                }

                fitnesses.push_back(10000000/(simulator->simulate(clones)));
            }

            return fitnesses;
        }

        //TODO: create a type for bitset<32>
        bitset<32> selectParent(population_type current_population, vector<double> evaluation_result, double evaluation_sum) {
            random_device rand_dev;
            mt19937 generator(rand_dev());
            uniform_real_distribution<double> distr(0, evaluation_sum);

            double pick = distr(generator);

            auto population_it = current_population.begin();
            double current_evaluation_sum = 0;

            for (auto evaluation_it = evaluation_result.begin(); evaluation_it != evaluation_result.end(); ++evaluation_it) {
                if (current_evaluation_sum >= pick) {
                    return (*population_it);
                }
                ++population_it;
            }

            // TODO: verify if a more precise type than double is necessary
            return current_population.back();
        }

        bitset<32> crossover(bitset<32> parent_1, bitset<32>parent_2) {
            bitset<32> left_mask("00001111000011110000111100001111");
            bitset<32> right_mask("11110000111100001111000011110000");
            
            bitset<32> genes_from_parent_1 = parent_1 & left_mask;
            bitset<32> genes_from_parent_2 = parent_2 & right_mask;

            bitset<32> child_1 = genes_from_parent_1 | genes_from_parent_2;
            bitset<32> child_2 = genes_from_parent_2 | genes_from_parent_1;

            random_device rand_dev;
            mt19937 generator(rand_dev());
            uniform_int_distribution<int> distr(0, 1);

            int pick = distr(generator);

            if (pick == 0) {
                return child_1;
            }

            return child_2;
        }

        bitset<32> mutate(bitset<32> child) {
            double chance = 0.001;

            random_device rand_dev;
            mt19937 generator(rand_dev());
            uniform_real_distribution<double> distr(0, 1);
            double pick = 0.0;

            for (int i = 0; i < 32; ++i) {
                pick = distr(generator);
                if (pick <= chance) {
                    child.flip(i);
                }
            }

            return child;
        }

        population_type createNextPopulation(population_type current_population, vector<double> evaluation_result) {
            population_type next_population;
            double evaluation_sum = 0;

            for (auto it = evaluation_result.begin(); it != evaluation_result.end(); ++it) {
                evaluation_sum += (*it);
            }

            for (int i = 0; i < current_population.size(); ++i) {
                bitset<32> parent_1 = this->selectParent(current_population, evaluation_result, evaluation_sum);
                bitset<32> parent_2 = this->selectParent(current_population, evaluation_result, evaluation_sum);
                bitset<32> child = this->crossover(parent_1, parent_2);

                next_population.push_back(this->mutate(child));
            }

            return next_population;
        }

    public:
        GA(int population_size) {
            this->population_size = population_size;
        }

        void printFitness(vector<double> evaluation_result) {
            double best_fitness = 0;
            double fitness_sum = 0;

            for (auto it = evaluation_result.begin(); it != evaluation_result.end(); ++it) {
                fitness_sum += (*it);
                best_fitness = max(best_fitness, (*it));
            }

            cout << best_fitness << " " << (fitness_sum / evaluation_result.size()) << endl;
        }

        void run() {
            population_type population = this->createInitialPopulation();
            vector<double> evaluation_result = this->evaluate_population(population);	
            this->printFitness(evaluation_result);

            for (int i = 0; i < 1000; ++i) {
                population = this->createNextPopulation(population, evaluation_result);
                evaluation_result = this->evaluate_population(population);
                this->printFitness(evaluation_result);
            }
        }
};