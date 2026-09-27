include_directories (${PROJECT_SOURCE_DIR})
link_directories (${PROJECT_BINARY_DIR})

add_executable(sorting_objects main.cpp)
target_link_libraries(sorting_objects enki)
target_link_libraries(sorting_objects pugixml)