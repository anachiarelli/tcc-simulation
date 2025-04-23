#include <enki/robots/e-puck/EPuck.h>

class ControlledEPuck : public Enki::EPuck {
    public:
        void controlStep(double dt) {
            Enki::EPuck::controlStep(dt);
        }
};