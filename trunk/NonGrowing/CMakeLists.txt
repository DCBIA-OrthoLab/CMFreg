project(NonGrowing)
cmake_minimum_required(VERSION 2.6)

#######################
# Non-Growing Registration plugin

set (CLP NonGrowing)
set (${CLP}_SOURCE ${CLP}.cxx)
generateclp(${CLP}_SOURCE ${CLP}.xml)

add_executable(${CLP} ${${CLP}_SOURCE})
target_link_libraries(${CLP} ${ITK_LIBRARIES})
