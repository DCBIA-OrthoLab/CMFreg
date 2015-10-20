#-----------------------------------------------------------------------------
# Surface Registration Module
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
set(MODULE_NAME "SurfaceRegistration")

#-----------------------------------------------------------------------------
 slicerMacroBuildScriptedModule(
   NAME SurfaceRegistration
   SCRIPTS "SurfaceRegistration.py"
   RESOURCES ""
   )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

slicer_add_python_unittest(SCRIPT "SurfaceRegistration.py")

endif()