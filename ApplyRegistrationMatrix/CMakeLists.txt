#-----------------------------------------------------------------------------
set(MODULE_NAME ApplyRegistrationMatrix)

#-----------------------------------------------------------------------------

set(MODULE_PYTHON_SCRIPTS
	${MODULE_NAME}.py
	)

set(MODULE_PYTHON_RESOURCES
	)

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
	NAME ${MODULE_NAME}
	SCRIPTS ${MODULE_PYTHON_SCRIPTS}
	RESOURCES ${MODULE_PYTHON_RESOURCES}
	)

#-----------------------------------------------------------------------------

if(NOT BUILD_TESTING)
  add_subdirectory(Testing)
endif()
