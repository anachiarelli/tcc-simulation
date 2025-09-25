#ifndef GENEMAP_CPP
#define GENEMAP_CPP 1

#include <vector>
#include <string>

class GeneMap {
    std::vector<std::pair<int, std::string>> sections;
    
    public:
        void addGene(int length, const std::string& type) {
            sections.push_back(std::make_pair(length, type));
        }
        
        int getLength() {
            int total_length = 0;
            for (const auto& section : sections) {
                total_length += section.first;
            }
            return total_length;
        }

        void addSection(int length, const std::string& type) {
            sections.push_back(std::make_pair(length, type));
        }
};

#endif // GENEMAP_CPP