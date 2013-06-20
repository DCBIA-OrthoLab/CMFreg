
#-----------------------------------------------------------------------------
set(MODULE_NAME Downsize)

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
