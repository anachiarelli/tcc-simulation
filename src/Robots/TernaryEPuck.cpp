#ifndef TERNARYEPUCK_CPP
#define TERNARYEPUCK_CPP

#include <enki/robots/e-puck/EPuck.h>
#include <bitset>
#include <unordered_map>
#include "../Automaton/AutomatonPlayer.cpp"

using event_params = std::unordered_map<std::string, std::pair<double, double>>;
using namespace std;

class TernaryEPuck : public Enki::EPuck {
public:
    TernaryEPuck(AutomatonPlayer* player, event_params speeds_by_event, Enki::Color epuck_color, Enki::Color object_color, unsigned capabilities = CAPABILITY_CAMERA)
        : EPuck(capabilities),
          player(player),
          speeds_by_event(speeds_by_event) {
        this->setColor(epuck_color);
        this->object_color = object_color;
    }

    void controlStep(double dt) {
        auto image = camera.image;

        if (image[29] == this->getColor() || image[30] == this->getColor()) {
            // std::cout << "Dispatching event seeing_same" << std::endl;
            this->player->dispatch("s_s");
        } else if (image[29] == this->object_color || image[30] == this->object_color) {
            // std::cout << "Dispatching event seeing_other" << std::endl;
            this->player->dispatch("s_o");
        } else {
            // std::cout << "Dispatching event seeing_wall" << std::endl;
            this->player->dispatch("s_w");
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
    Enki::Color object_color;
};

#endif