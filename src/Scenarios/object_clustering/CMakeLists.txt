include_directories (${PROJECT_SOURCE_DIR})
link_directories (${PROJECT_BINARY_DIR})

add_executable(object_clustering main.cpp)
target_link_libraries(object_clustering enki)
target_link_libraries(object_clustering pugixml)