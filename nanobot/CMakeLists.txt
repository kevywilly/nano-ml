cmake_minimum_required(VERSION 3.10)

# set the project name
project(nanobot)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS "-fPIC -g -pedantic -Wall -Wextra")

if(LOG) 
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DLOG=1")
endif()

find_package(OpenCV 4.5 REQUIRED)
include_directories(${OpenCV_INCLUDE_DIR})

#add_subdirectory(CSI_Camera)
#include_directories(CSI_Camera/src)
#include_directories(src)

# Build the calibration tool
add_executable(nanobot main.cpp)
target_link_libraries(nanobot ${OpenCV_LIBRARIES})