#include <enki/robots/e-puck/EPuck.h>
#include <bitset>

class GeneticEPuck : public Enki::EPuck {
    private:
        // TODO: Define shareable chromosome type
        bitset<32> chromosome;
        double speed_seeing_robot[2];
        double speed_seeing_wall[2];

        uint64_t decodeChromosomeSegment(int begin, int length) {
            uint64_t value = 0;

            for (size_t i = begin; i < length; ++i) {
                if (this->chromosome[i]) {
                    value |= (1ULL << (i - begin));
                }
            }
            return value;
        }

        double transformChromosomeSegmentValueIntoSpeed(uint64_t value) {
            return (-12.8 + (value * 0.1));
        }

        void decodeChromosome() {
            this->speed_seeing_robot[0] = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(0, 8));
            this->speed_seeing_robot[1] = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(8, 8));
            this->speed_seeing_wall[0] = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(16, 8));
            this->speed_seeing_wall[1] = this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(24, 8));
        }

    public:
        GeneticEPuck(bitset<32> chromosome, unsigned capabilities = CAPABILITY_CAMERA) : EPuck(capabilities) {
            this->chromosome = chromosome;
            this->setColor(Enki::Color(0.0, 1.0, 0.0, 1.0));
        }

        void controlStep(double dt) {
            auto image = camera.image;

            if (image[29] == this->getColor() || image[30] == this->getColor()) {
                this->leftSpeed = this->speed_seeing_robot[0];
                this->rightSpeed = this->speed_seeing_robot[1];
            } else {
                this->leftSpeed = this->speed_seeing_wall[0];
                this->rightSpeed = this->speed_seeing_wall[1];
            }

            Enki::EPuck::controlStep(dt);
        }
};