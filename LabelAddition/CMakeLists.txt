#-----------------------------------------------------------------------------
set(MODULE_NAME LabelAddition)

#-----------------------------------------------------------------------------

set(MODULE_TARGET_LIBRARIES
  ${ITK_LIBRARIES}
  )

#-----------------------------------------------------------------------------
SEMMacroBuildCLI(
  NAME ${MODULE_NAME}
  INCLUDE_DIRECTORIES ${Slicer_HOME}  # Contains vtkSlicerConfigure.h which contains the CLI paths in Slicer
  TARGET_LIBRARIES ${MODULE_TARGET_LIBRARIES}
  EXECUTABLE_ONLY
  )

#-----------------------------------------------------------------------------
# if(BUILD_TESTING)
#   add_subdirectory(Testing)
# endif()
