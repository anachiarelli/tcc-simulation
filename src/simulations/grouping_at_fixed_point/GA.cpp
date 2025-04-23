#include <iostream>
#include <vector>
#include <random>
#include <bitset>
using namespace std;
class GA {
    private:
        int population_size;

        vector<bitset<32>> createInitialPopulation() {
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

    public:
        GA(int population_size) {
            this->population_size = population_size;
        }

        void run() {
            vector<bitset<32>> population = this->createInitialPopulation();
            for (auto it = population.begin(); it != population.end(); ++it) {
                cout << *it << endl;
            }
        }
};