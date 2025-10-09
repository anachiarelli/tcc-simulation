include_directories (${PROJECT_SOURCE_DIR})
link_directories (${PROJECT_BINARY_DIR})

add_executable(sorting_groups main.cpp)
target_link_libraries(sorting_groups enki)
target_link_libraries(sorting_groups pugixml)