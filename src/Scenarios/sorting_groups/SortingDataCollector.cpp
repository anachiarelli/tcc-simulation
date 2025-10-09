#include "../../Simulator/DataCollectorInterface.cpp"
#include "enki/robots/e-puck/EPuck.h"
#include "enki/PhysicalEngine.h"
#include <vector>

using robots_list = std::vector<Enki::EPuck*>;
using objects_list = std::vector<Enki::PhysicalObject*>;

class SortingDataCollector : public DataCollectorInterface {
public:
    SortingDataCollector(robots_list& robots, objects_list& objects) : robots(robots), objects(objects) {}

    void collect() override {
        std::vector<std::vector<double>> robot_step_data;
        std::vector<std::vector<double>> object_step_data;
        // std::cout << "this->robots size" << this->robots.size() << std::endl;
        
        for (auto &robot : this->robots) {
            robot_step_data.push_back({robot->pos.x, robot->pos.y, robot->angle, robot->getColor().r(), robot->getColor().g(), robot->getColor().b()});
        }
        robots_data.push_back(robot_step_data);

        for (auto &object : this->objects) {
            object_step_data.push_back({object->pos.x, object->pos.y, object->getColor().r(), object->getColor().g(), object->getColor().b()});
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