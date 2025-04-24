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
        
        vector<double> evaluate_population(population_type population) {
            Simulator *simulator = new Simulator();
            return simulator->simulate(population);
        }

        population_type createNextPopulation(population_type current_population, vector<double> evaluation_result) {
            population_type nextPopulation;
            // TODO
            return nextPopulation;
        }

    public:
        GA(int population_size) {
            this->population_size = population_size;
        }

        void run() {
            population_type population = this->createInitialPopulation();
            vector<double> evaluation_result = this->evaluate_population(population);

            for (int i = 0; i < 10; ++i) {
                population = this->createNextPopulation(population, evaluation_result);
                evaluation_result = this->evaluate_population(population);
            }
        }
};