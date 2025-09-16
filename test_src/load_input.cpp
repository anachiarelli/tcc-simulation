#include <pugixml/src/pugixml.hpp>
#include <iostream>
#include <string>

int main()
{
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_file("input/sync.xml");
    if (!result) {
        std::cout << "erro" << std::endl;
        std::cout << "description" << result.description() << std::endl;
        return 0;
    }

    for (pugi::xml_node event: doc.child("model").child("data").children("event")) {
        std::string name = event.attribute("name").as_string();
        std::cout << name << std::endl;
    }

    std::cout << "ok" << std::endl;
    return 0;
}