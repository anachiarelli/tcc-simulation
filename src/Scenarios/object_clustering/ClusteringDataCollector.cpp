#include "../../Simulator/DataCollectorInterface.cpp"
#include "enki/robots/e-puck/EPuck.h"
#include "enki/PhysicalEngine.h"
#include <vector>

using robots_list = std::vector<Enki::EPuck*>;
using objects_list = std::vector<Enki::PhysicalObject*>;

class ClusteringDataCollector : public DataCollectorInterface {
public:
    ClusteringDataCollector(robots_list& robots, objects_list& objects) : robots(robots), objects(objects) {}

    void collect() override {
        std::vector<std::vector<double>> robot_step_data;
        std::vector<std::vector<double>> object_step_data;
        
        for (auto &robot : this->robots) {
            robot_step_data.push_back({robot->pos.x, robot->pos.y, robot->angle});
        }
        robots_data.push_back(robot_step_data);

        for (auto &object : this->objects) {
            object_step_data.push_back({object->pos.x, object->pos.y});
        }
        objects_data.push_back(object_step_data);
    }

    const std::vector<std::vector<std::vector<double>>>& getRobotsData() const {
        return robots_data;
    }

    const std::vector<std::vector<std::vector<double>>>& getObjectsData() const {
        return objects_data;
    }

private:
    robots_list& robots;
    objects_list& objects;
    std::vector<std::vector<std::vector<double>>> robots_data;
    std::vector<std::vector<std::vector<double>>> objects_data;
};