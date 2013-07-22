<<<<<<< HEAD
#-----------------------------------------------------------------------------
set(MODULE_NAME LabelAddition)

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
endif()
=======

#-----------------------------------------------------------------------------
set(MODULE_NAME LabelAddition)

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
endif()
>>>>>>> c52fff7b917a21d2f7316a01a570d3a5801c6430
