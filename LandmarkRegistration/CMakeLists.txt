#-----------------------------------------------------------------------------
# Landmark Registration Module
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
set(MODULE_NAME "LandmarkRegistration")

#-----------------------------------------------------------------------------
 slicerMacroBuildScriptedModule(
   NAME LandmarkRegistration
   SCRIPTS "LandmarkRegistration.py"
   RESOURCES ""
   )

#-----------------------------------------------------------------------------
set(MODULE_NAME "CompareVolumes")

#-----------------------------------------------------------------------------
 slicerMacroBuildScriptedModule(
   NAME CompareVolumes
   SCRIPTS "CompareVolumes.py"
   RESOURCES ""
   )
