cmake_minimum_required(VERSION 2.8.9)

project(CMFreg)

#-----------------------------------------------------------------------------
set(EXTENSION_NAME "CMFreg")
set(EXTENSION_HOMEPAGE "https://www.slicer.org/slicerWiki/index.php/Documentation/4.4/Extensions/CMFreg")
set(EXTENSION_CATEGORY "Registration")
set(EXTENSION_CONTRIBUTORS "Vinicius Boen (Univ of Michigan), Manson Winsauer (UNC), Jean-Baptiste Vimort (Univ of Michigan)")
set(EXTENSION_DESCRIPTION "Tools package for the cranio-maxillofacial registration")
set(EXTENSION_ICONURL "https://www.slicer.org/slicerWiki/images/b/bc/BaselineFollowupSCANRegisteredCMFreg2.png")
set(EXTENSION_SCREENSHOTURLS "https://www.slicer.org/slicerWiki/images/1/15/BaselineFollowupSCANCMFreg.png https://www.slicer.org/slicerWiki/images/0/0b/GrowingInterface.png https://www.slicer.org/slicerWiki/images/4/4a/InputSegToExtractionCMFreg.png https://www.slicer.org/slicerWiki/images/4/46/BaselineSegmentationMaskCMFreg.png")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
add_subdirectory(ApplyMatrix)
add_subdirectory(Growing)
add_subdirectory(NonGrowing)
add_subdirectory(Downsize)
add_subdirectory(LabelAddition)
add_subdirectory(LabelExtraction)
add_subdirectory(MaskCreation)
add_subdirectory(SurfaceRegistration)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
