#ifndef PARAM_DECODER_INTERFACE_CPP
#define PARAM_DECODER_INTERFACE_CPP

#include <boost/dynamic_bitset.hpp>
#include <unordered_map>
using individual_type = boost::dynamic_bitset<>;
using event_params = std::unordered_map<std::string, std::pair<double, double>>;


class ParamDecoderInterface {
public:
    virtual event_params decodeParams(individual_type chromosome) = 0;
};

#endif // PARAM_DECODER_INTERFACE_CPP