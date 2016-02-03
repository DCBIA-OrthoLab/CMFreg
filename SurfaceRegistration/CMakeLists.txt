#-----------------------------------------------------------------------------
# Surface Registration Module
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
set(MODULE_NAME "SurfaceRegistration")

set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/UI/${MODULE_NAME}.ui
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

slicer_add_python_unittest(SCRIPT "SurfaceRegistration.py")

endif()