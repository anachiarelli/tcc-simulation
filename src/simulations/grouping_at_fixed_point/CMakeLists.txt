include_directories (${PROJECT_SOURCE_DIR})
link_directories (${PROJECT_BINARY_DIR})

add_executable(grouping_at_fixed_point simulation.cpp)
target_link_libraries(grouping_at_fixed_point enki)
