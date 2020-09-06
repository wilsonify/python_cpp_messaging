cmake_minimum_required(VERSION 3.0)
project(cpp-consumer)
add_definitions("-std=c++14")

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(consumer consumer.cpp)
target_link_libraries(consumer ${CONAN_LIBS})











