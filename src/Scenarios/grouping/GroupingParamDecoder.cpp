#ifndef GROUPING_PARAM_DECODER_CPP
#define GROUPING_PARAM_DECODER_CPP

#include "../../Genetics/ParamDecoderInterface.cpp"
#include <boost/dynamic_bitset.hpp>
#include <unordered_map>
using individual_type = boost::dynamic_bitset<>;
using event_params = std::unordered_map<std::string, std::pair<double, double>>;

class GroupingParamDecoder : public ParamDecoderInterface {
public:
    event_params decodeParams(individual_type chromosome) override {
        event_params speeds_by_event;

        // TODO: replace hardcoded params with dynamic params from GeneMap
        speeds_by_event["v0"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(8, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(16, 8, chromosome))
        );
        speeds_by_event["v1"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(24, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(32, 8, chromosome))
        );

        return speeds_by_event;
    }
    
    uint64_t decodeChromosomeSegment(int begin, int length, individual_type chromosome) {
        uint64_t value = 0;

        for (size_t i = begin; i < (length + begin); ++i) {
            if (chromosome[i]) {
                value |= (1ULL << (i - begin));
            }
        }
        return value;
    }

    double transformChromosomeSegmentValueIntoSpeed(uint64_t value) {
        return (-12.8 + (value * 0.1));
    }
};

#endif // GROUPING_PARAM_DECODER_CPP