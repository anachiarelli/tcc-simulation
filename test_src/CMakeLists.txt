project(tcc_simulation)
cmake_minimum_required(VERSION 3.28.3)

add_subdirectory(pugixml)

include_directories (${PROJECT_SOURCE_DIR})
link_directories (${PROJECT_BINARY_DIR})

add_executable(load_input load_input.cpp)
target_link_libraries(load_input pugixml)
