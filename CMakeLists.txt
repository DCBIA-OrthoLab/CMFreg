cmake_minimum_required(VERSION 2.8.9)

project(CMFreg)

set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_INSTALL_PREFIX})

#-----------------------------------------------------------------------------
set(EXTENSION_NAME "CMFreg")
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/4.3/Extensions/CMFreg")
set(EXTENSION_CATEGORY "Registration")
set(EXTENSION_CONTRIBUTORS "Vinicius Boen (Univ of Michigan), Manson Winsauer(UNC)")
set(EXTENSION_DESCRIPTION "Tools package for the cranio-maxillofacial registration")
set(EXTENSION_ICONURL "http://www.slicer.org/slicerWiki/images/b/bc/BaselineFollowupSCANRegisteredCMFreg2.png")
set(EXTENSION_SCREENSHOTURLS "http://www.slicer.org/slicerWiki/images/1/15/BaselineFollowupSCANCMFreg.png http://www.slicer.org/slicerWiki/images/0/0b/GrowingInterface.png http://www.slicer.org/slicerWiki/images/4/4a/InputSegToExtractionCMFreg.png http://www.slicer.org/slicerWiki/images/4/46/BaselineSegmentationMaskCMFreg.png")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

find_package(ITK REQUIRED)
if(${ITK_VERSION_MAJOR} GREATER 3)
  set(ITK_NO_IO_FACTORY_REGISTER_MANAGER 1) # See Libs/ITKFactoryRegistration/CMakeLists.txt
  list(APPEND ITK_LIBRARIES ITKFactoryRegistration)
endif()
if (ITK_FOUND)
  include(${USE_ITK_FILE})
else(ITK_FOUND)
  message(FATAL_ERROR, "ITK not found. Please set ITK_DIR.")
endif (ITK_FOUND)

find_package(VTK REQUIRED)
if (VTK_FOUND)
  include(${USE_VTK_FILE})
else(VTK_FOUND)
  message(FATAL_ERROR, "VTK not found. Please set VTK_DIR.")
endif (VTK_FOUND)

find_package(GenerateCLP REQUIRED)
if (GenerateCLP_FOUND)
  include(${GenerateCLP_USE_FILE})
else (GenerateCLP_FOUND)
  message(FATAL_ERROR, "GenerateCLP not found. Please set GenerateCLP_DIR")
endif (GenerateCLP_FOUND)

#-----------------------------------------------------------------------------
add_subdirectory(Growing)
add_subdirectory(NonGrowing)
add_subdirectory(Downsize)
add_subdirectory(LabelAddition)
add_subdirectory(LabelExtraction)
add_subdirectory(MaskCreation)
#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
