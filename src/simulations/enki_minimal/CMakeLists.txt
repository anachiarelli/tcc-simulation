include_directories (${PROJECT_SOURCE_DIR})
link_directories (${PROJECT_BINARY_DIR})

add_executable(enki_minimal simulation.cpp)
target_link_libraries(enki_minimal enki)
