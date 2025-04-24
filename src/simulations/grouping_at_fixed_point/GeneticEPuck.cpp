#include <enki/robots/e-puck/EPuck.h>
#include <bitset>

class GeneticEPuck : public Enki::EPuck {
    private:
        // TODO: Define shareable chromosome type
        bitset<32> chromosome;
    public:
        GeneticEPuck(bitset<32> chromosome, unsigned capabilities = CAPABILITY_CAMERA) : EPuck(capabilities) {
            this->chromosome = chromosome;
            this->setColor(Enki::Color(0.0, 1.0, 0.0, 1.0));
        }

        void controlStep(double dt) {
            Enki::EPuck::controlStep(dt);
        }
};