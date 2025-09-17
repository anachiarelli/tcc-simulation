include_directories (${PROJECT_SOURCE_DIR})
link_directories (${PROJECT_BINARY_DIR})

add_executable(grouping simulation.cpp)
target_link_libraries(grouping enki)
