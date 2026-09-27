#ifndef GROUPING_DATA_WRITER_CPP
#define GROUPING_DATA_WRITER_CPP

#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <boost/dynamic_bitset.hpp>
using individual_type = boost::dynamic_bitset<>;

class GroupingDataWriter {
public:
    GroupingDataWriter(std::string output_dir) : output_dir(output_dir) {}

    void writePositions(int generation, int individual_id, const std::vector<std::vector<std::vector<double>>>& data, individual_type individual, int run) {
        std::string individual_id_str = padInteger(individual_id, 3);
        std::string generation_str = padInteger(generation, 3);
        std::string output_dir = this->output_dir + "/" + generation_str + "/positions";
        std::filesystem::create_directories(output_dir);
        std::string buffer;
		boost::to_string(individual, buffer);

        std::string path = output_dir + "/" + individual_id_str + "_" + buffer + "_" + std::to_string(run) + ".csv";
        std::ofstream file(path);

        if (!file.is_open()) {
            std::cerr << "Unable to open file " << path << " for writing positions." << std::endl;
            return;
        }

        for (const auto& step_data : data) {
            for (const auto& robot_data : step_data) {
                file << robot_data[0] << "," << robot_data[1] << "," << robot_data[2] << ",";
            }
            file << "\n";
        }

        file.close();
    }

    void writeDispersion(int generation, int individual_id, const std::vector<double>& dispersion_data, individual_type individual, int run) {
        std::string individual_id_str = padInteger(individual_id, 3);
        std::string generation_str = padInteger(generation, 3);
        std::string output_dir = this->output_dir + "/" + generation_str + "/dispersions";
        std::filesystem::create_directories(output_dir);
        std::string buffer;
        boost::to_string(individual, buffer);

        std::string path = output_dir + "/" + individual_id_str + "_" + buffer + "_" + std::to_string(run) + ".csv";
        std::ofstream file(path);

        if (!file.is_open()) {
            std::cerr << "Unable to open file " << path << " for writing dispersion." << std::endl;
            return;
        }

        for (const auto& value : dispersion_data) {
            file << value << "\n";
        }

        file.close();
    }

    void writeFitness(int generation, std::vector<double> fitness_values) {
        std::string generation_str = padInteger(generation, 3);
        std::string output_dir = this->output_dir + "/" + generation_str;
        std::filesystem::create_directories(output_dir);
        std::string path = output_dir + "/fitness.csv";
        std::ofstream file(path);

        if (!file.is_open()) {
            std::cerr << "Unable to open file " << path << " for writing fitness values." << std::endl;
            return;
        }

        for (const auto& value : fitness_values) {
            file << value << "\n";
        }

        file.close();
    }

private:
    std::string output_dir;

    std::string padInteger(int number, int width) {
        std::string num_str = std::to_string(number);
        return std::string(width - num_str.length(), '0') + num_str;
    }
};

#endif // GROUPING_DATA_WRITER_CPP