#include "../../Simulator/DataCollectorInterface.cpp"
#include "enki/robots/e-puck/EPuck.h"
#include <vector>

using robots_list = std::vector<Enki::EPuck*>;

class GroupingDataCollector : public DataCollectorInterface {
public:
    GroupingDataCollector(robots_list& robots) : robots(robots) {}

    void collect() override {
        std::vector<std::vector<double>> step_data;
        for (auto &robot : this->robots) {
            std::vector<double> robot_data;
            step_data.push_back({robot->pos.x, robot->pos.y, robot->angle});
        }
        data.push_back(step_data);
    }

    const std::vector<std::vector<std::vector<double>>>& getData() const {
        return data;
    }

private:
    robots_list& robots;
    std::vector<std::vector<std::vector<double>>> data;
};