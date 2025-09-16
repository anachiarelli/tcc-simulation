#include <iostream>
#include <vector>
#include <random>
#include <bitset>
#include <filesystem>
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

            // bitset<32> gauci("00000000001001100000000011111111");
            // population.push_back(gauci);
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
        vector<double> evaluate_population(population_type population, int generation) {
            vector<double> fitnesses;

            string generation_str = to_string(generation);
            generation_str = string(3 - generation_str.length(), '0') + generation_str;
            string output_dir = "/root/simulation/output/current/" + generation_str;

            filesystem::create_directory(output_dir);
            ofstream fitness_file(output_dir + "/fitness.txt");
            if (!fitness_file.is_open()) {
                cerr << "Unable to open fitness file: " << output_dir + "/fitness.txt" << endl;
                exit(-1);
            }

            int num = 0;

            for (auto p = population.begin(); p != population.end(); ++p) {
                // World size of 316 taken from GAUCI_A
                Simulator *simulator = new Simulator(316);
                population_type clones;

                for (int i = 0; i < 10; i++) {
                    clones.push_back(*p);
                }

                string num_str = to_string(num);
                num_str = string(3 - num_str.length(), '0') + num_str;
                string simulation_name = num_str + "_" + (*p).to_string();
                double cost = simulator->simulate(clones, simulation_name, output_dir);
                num += 1;

                // Setting fitness to 1/cost, as the algorithm's goal is to maximize it
                // Also, multiplying fitness by 100,000,000 to make it easier to read on logs - it shouldn't affect performance at all
                double fitness = 100000000 / cost;
                fitness_file << fitness << endl;
                fitnesses.push_back(fitness);
            }

            fitness_file.close();
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
                current_evaluation_sum += (*evaluation_it);
                if (current_evaluation_sum >= pick) {
                    return (*population_it);
                }
                ++population_it;
            }

            // TODO: verify if a more precise type than double is necessary
            return current_population.back();
        }

        bitset<32> crossover(bitset<32> parent_1, bitset<32>parent_2) {
            // bitset<32> left_mask("00001111000011110000111100001111");
            // bitset<32> right_mask("11110000111100001111000011110000");
            
            //bitset<32> left_mask("00000000000000001111111111111111"); // single point crossover
            //bitset<32> right_mask("11111111111111110000000000000000");

            random_device rand_dev;
            mt19937 generator(rand_dev());
            uniform_int_distribution<int> distr(0, 1);
            
            // uniform crossover
            bitset<32> left_mask("00000000000000000000000000000000");
            bitset<32> right_mask("00000000000000000000000000000000");

            for (int i = 0; i < 32; ++i) {
                if (distr(generator) == 0) {
                    left_mask.flip(i);
                } else {
                    right_mask.flip(i);
                }
            }

            bitset<32> genes_from_parent_1 = parent_1 & left_mask;
            bitset<32> genes_from_parent_2 = parent_2 & right_mask;

            bitset<32> child_1 = genes_from_parent_1 | genes_from_parent_2;
            bitset<32> child_2 = genes_from_parent_2 | genes_from_parent_1;

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

            int best_index = 0;
            for (int i = 0; i < evaluation_result.size(); ++i) {
                if (evaluation_result[best_index] < evaluation_result[i]) {
                    best_index = i;
                }
                evaluation_sum += evaluation_result[i];
            }

            next_population.push_back(current_population[best_index]); // elitism
            for (int i = 0; i < current_population.size() - 1; ++i) {
                bitset<32> parent_1 = this->selectParent(current_population, evaluation_result, evaluation_sum);
                bitset<32> parent_2 = this->selectParent(current_population, evaluation_result, evaluation_sum);
                bitset<32> child = this->crossover(parent_1, parent_2);
                
                next_population.push_back(this->mutate(child));

                //cout << "parent 1: " << parent_1 << " parent 2:" << parent_2 << " child:" << child << endl;
            }

            return next_population;
        }

    public:
        uint64_t decodeChromosomeSegment(int begin, int length, bitset<32> chromosome) {
            uint64_t value = 0;

            for (size_t i = begin; i < (length + begin); ++i) {
                if (chromosome[i]) {
                    value |= (1ULL << (i - begin));
                }
            }
            return value;
        }

        double transformChromosomeSegmentValueIntoSpeed(uint64_t value) {
            //cout << value << endl;
            return (-12.8 + (value * 0.1));
        }

        GA(int population_size) {
            this->population_size = population_size;
        }

        void printFitness(vector<double> evaluation_result, population_type population) {
            int best_index = 0;
            double fitness_sum = 0;

            for (int i = 0; i < evaluation_result.size(); ++i) {
                fitness_sum += evaluation_result[i];
                if (evaluation_result[best_index] < evaluation_result[i]) {
                    best_index = i;
                }
            }

            cout << "\"" << evaluation_result[best_index] << "\",";
            cout << "\"" << (fitness_sum / evaluation_result.size()) << "\",";

            double speed1 = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(0, 8, population[best_index]));
            double speed2 = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(8, 8, population[best_index]));
            double speed3 = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(16, 8, population[best_index]));
            double speed4 = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(24, 8, population[best_index]));

            cout << "\"" << population[best_index] << "\"," 
                << "\"" << speed1 << "\","
                << "\"" << speed2 << "\","
                << "\"" << speed3 << "\","
                << "\"" << speed4 << "\",";

            for (int i = 0; i < population.size(); ++i) {
                double speed1 = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(0, 8, population[i]));
                double speed2 = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(8, 8, population[i]));
                double speed3 = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(16, 8, population[i]));
                double speed4 = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(24, 8, population[i]));

                cout << "\"" << population[i] << "\"," 
                     << "\"" << speed1 << "\","
                     << "\"" << speed2 << "\","
                     << "\"" << speed3 << "\","
                     << "\"" << speed4 << "\","
                     << "\"" << evaluation_result[i] << "\",";
            }

            cout << endl;
        }


        void run() {
            population_type population = this->createInitialPopulation();
            vector<double> evaluation_result = this->evaluate_population(population, 0);	
            this->printFitness(evaluation_result, population);

            for (int i = 0; i < 39; ++i) {
                population = this->createNextPopulation(population, evaluation_result);
                evaluation_result = this->evaluate_population(population, (i+1));
                this->printFitness(evaluation_result, population);
            }
        }
};