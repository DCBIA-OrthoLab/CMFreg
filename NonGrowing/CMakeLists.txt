<<<<<<< HEAD
#-----------------------------------------------------------------------------
set(MODULE_NAME NonGrowing)

#-----------------------------------------------------------------------------

set(MODULE_TARGET_LIBRARIES
  ${ITK_LIBRARIES}
  )

#-----------------------------------------------------------------------------
SEMMacroBuildCLI(
  NAME ${MODULE_NAME}
  TARGET_LIBRARIES ${MODULE_TARGET_LIBRARIES}
  )

#-----------------------------------------------------------------------------
if(NOT BUILD_TESTING)
  add_subdirectory(Testing)
=======

#-----------------------------------------------------------------------------
set(MODULE_NAME NonGrowing)

#-----------------------------------------------------------------------------

set(MODULE_TARGET_LIBRARIES
  ${ITK_LIBRARIES}
  )

#-----------------------------------------------------------------------------
SEMMacroBuildCLI(
  NAME ${MODULE_NAME}
  TARGET_LIBRARIES ${MODULE_TARGET_LIBRARIES}
  )

#-----------------------------------------------------------------------------
if(NOT BUILD_TESTING)
  add_subdirectory(Testing)
>>>>>>> c52fff7b917a21d2f7316a01a570d3a5801c6430
endif()
