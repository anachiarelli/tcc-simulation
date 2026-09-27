#ifndef SORTING_GROUPS_PARAM_DECODER_CPP
#define SORTING_GROUPS_PARAM_DECODER_CPP

#include "../../Genetics/ParamDecoderInterface.cpp"
#include <boost/dynamic_bitset.hpp>
#include <unordered_map>
using individual_type = boost::dynamic_bitset<>;
using event_params = std::unordered_map<std::string, std::pair<double, double>>;

class SortingGroupsParamDecoder : public ParamDecoderInterface {
public:
    event_params decodeParams(individual_type chromosome) override {
        event_params speeds_by_event;

        // TODO: replace hardcoded params with dynamic params from GeneMap
        speeds_by_event["v_s"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(27, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(35, 8, chromosome))
        );
        speeds_by_event["v_w"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(43, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(51, 8, chromosome))
        );
        speeds_by_event["v_o"] = std::make_pair(
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(59, 8, chromosome)),
            this->transformChromosomeSegmentValueIntoSpeed(this->decodeChromosomeSegment(67, 8, chromosome))
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

#endif // SORTING_GROUPS_PARAM_DECODER_CPP