#ifndef CONTROLLEDEPUCK_CPP
#define CONTROLLEDEPUCK_CPP

#include <enki/robots/e-puck/EPuck.h>
#include <bitset>
#include <unordered_map>
#include "../../Automaton/AutomatonPlayer.cpp"

using event_params = std::unordered_map<std::string, std::pair<double, double>>;
using namespace std;

class ControlledEPuck : public Enki::EPuck {
public:
    ControlledEPuck(AutomatonPlayer* player, event_params speeds_by_event, unsigned capabilities = CAPABILITY_CAMERA)
        : EPuck(capabilities),
          player(player),
          speeds_by_event(speeds_by_event) {
        this->setColor(Enki::Color(0.0, 1.0, 0.0, 1.0));
    }

    void controlStep(double dt) {
        auto image = camera.image;

        if (image[29] == this->getColor() || image[30] == this->getColor()) {
            // std::cout << "Dispatching event v1" << std::endl;
            this->player->dispatch("v1");
        } else {
            // std::cout << "Dispatching event v0" << std::endl;
            this->player->dispatch("v0");
        }

        std::string action = this->player->step();
        // std::cout << "Action: " << action << std::endl;
        if (this->speeds_by_event.find(action) != this->speeds_by_event.end()) {
            auto speeds = this->speeds_by_event[action];
            this->leftSpeed = speeds.first;
            this->rightSpeed = speeds.second;
        } else {
            // TODO: checar se o evento é mudar de velocidade ou andar na velocidade
            // caso seja andar, o robô deve parar caso nenhum evento seja encontrado
            this->leftSpeed = 0.0;
            this->rightSpeed = 0.0;
        }

        Enki::EPuck::controlStep(dt);
    }
private:
    AutomatonPlayer* player;
    event_params speeds_by_event;
};

#endif