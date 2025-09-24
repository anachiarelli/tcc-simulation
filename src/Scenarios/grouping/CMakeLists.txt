include_directories (${PROJECT_SOURCE_DIR})
link_directories (${PROJECT_BINARY_DIR})

add_executable(grouping main.cpp)
target_link_libraries(grouping enki)
target_link_libraries(grouping pugixml)