<<<<<<< HEAD
cmake_minimum_required(VERSION 2.8.9)

project(CMFreg)

set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_INSTALL_PREFIX})

#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "http://www.nitrc.org/plugins/mwiki/index.php/cmfreg:MainPage")
set(EXTENSION_CATEGORY "Registration")
set(EXTENSION_CONTRIBUTORS "Vinicius Boen (Univ of Michigan), Manson Winsauer(UNC)")
set(EXTENSION_DESCRIPTION "Tools package for the cranio-maxillofacial registration")
set(EXTENSION_ICONURL "http://www.na-mic.org/Wiki/index.php/File:SkulbaseRegistration.png")
set(EXTENSION_SCREENSHOTURLS "")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

find_package(ITK REQUIRED)
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
=======
cmake_minimum_required(VERSION 2.8.9)

project(CMFreg)

set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_INSTALL_PREFIX})
    
set(EXTENSION_HOMEPAGE "http://www.nitrc.org/plugins/mwiki/index.php/cmfreg:MainPage")
set(EXTENSION_CATEGORY "Registration")
set(EXTENSION_CONTRIBUTORS "Vinicius Boen (Univ of Michigan), Manson Winsauer(UNC)")
set(EXTENSION_DESCRIPTION "Tools package for the cranio-maxillofacial registration")
set(EXTENSION_ICONURL "http://www.na-mic.org/Wiki/images/a/a6/SkulbaseRegistration.png")
set(EXTENSION_SCREENSHOTS "")
    
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

find_package(ITK REQUIRED)
if (ITK_FOUND)
  include(${USE_ITK_FILE})
else (ITK_FOUND)
  message(FATAL_ERROR, "ITK not found. Please set ITK_DIR.")
endif (ITK_FOUND)

find_package(VTK REQUIRED)
if (VTK_FOUND)
  include(${USE_VTK_FILE})
else (VTK_FOUND)
  message(FATAL_ERROR, "VTK not found. Please set VTK_DIR.")
endif (VTK_FOUND)

find_package(GenerateCLP REQUIRED)
if (GenerateCLP_FOUND)
  include(${GenerateCLP_USE_FILE})
else (GenerateCLP_FOUND)
  message(FATAL_ERROR, "GenerateCLP not found. Please set GenerateCLP_DIR.")
endif (GenerateCLP_FOUND)

include(${Slicer_EXTENSION_CPACK})

add_subdirectory(Growing)
add_subdirectory(NonGrowing)
add_subdirectory(Downsize)
add_subdirectory(LabelAddition)
add_subdirectory(LabelExtraction)
add_subdirectory(MaskCreation)
>>>>>>> c52fff7b917a21d2f7316a01a570d3a5801c6430
