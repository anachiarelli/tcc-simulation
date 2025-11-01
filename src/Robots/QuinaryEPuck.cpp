#ifndef QUINARYEPUCK_CPP
#define QUINARYEPUCK_CPP

#include <enki/robots/e-puck/EPuck.h>
#include <bitset>
#include <unordered_map>
#include "../Automaton/AutomatonPlayer.cpp"

using event_params = std::unordered_map<std::string, std::pair<double, double>>;
using namespace std;

class QuinaryEPuck : public Enki::EPuck {
public:
    QuinaryEPuck(
        AutomatonPlayer* player,
        event_params speeds_by_event,
        Enki::Color epuck_color,
        Enki::Color interest_color,
        std::vector<Enki::Color> non_interest_colors,
        unsigned capabilities = CAPABILITY_CAMERA
    )
        : EPuck(capabilities),
          player(player),
          speeds_by_event(speeds_by_event),
          interest_color(interest_color),
          non_interest_colors(non_interest_colors) {
        this->setColor(epuck_color);
    }

    void controlStep(double dt) {
        auto image = camera.image;

        if (image[29] == this->getColor() || image[30] == this->getColor()) {
            // std::cout << "Dispatching event seeing_robot_same (s_r_s)" << std::endl;
            this->player->dispatch("s_r_s");
        } else if (image[29] == Enki::Color::gray || image[30] == Enki::Color::gray) {
            // std::cout << "Dispatching event seeing_wall (s_w)" << std::endl;
            this->player->dispatch("s_w");
        } else if (image[29] == this->interest_color || image[30] == this->interest_color) {
            // std::cout << "Dispatching event seeing_object_same (s_o_s)" << std::endl;
            this->player->dispatch("s_o_s");
        } else if (image[29] == this->non_interest_colors[0] || image[30] == this->non_interest_colors[0] ||
                   image[29] == this->non_interest_colors[1] || image[30] == this->non_interest_colors[1]) {
            // std::cout << "Dispatching event seeing_object_other (s_o_o)" << std::endl;
            this->player->dispatch("s_o_o");
        } else {
            // std::cout << "Dispatching event seeing_robot_other (s_r_o)" << std::endl;
            this->player->dispatch("s_r_o");
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
    Enki::Color interest_color;
    std::vector<Enki::Color> non_interest_colors;
};

#endif