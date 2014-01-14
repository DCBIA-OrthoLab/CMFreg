import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# LandmarkRegistration
#

class LandmarkRegistration:
  def __init__(self, parent):
    parent.title = "Landmark Registration"
    parent.categories = ["CMF Registration"]
    parent.dependencies = []
    parent.contributors = ["Steve Pieper (Isomics)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This module organizes a fixed and moving volume along with a set of corresponding
    landmarks (paired fiducials) to assist in manual registration.
    """
    parent.acknowledgementText = """
    This file was developed by Steve Pieper, Isomics, Inc.
    It was partially funded by NIH grant 3P41RR013218-12S1
    and this work is part of the National Alliance for Medical Image
    Computing (NAMIC), funded by the National Institutes of Health
    through the NIH Roadmap for Medical Research, Grant U54 EB005149.
    Information on the National Centers for Biomedical Computing
    can be obtained from http://nihroadmap.nih.gov/bioinformatics.
    """ # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['LandmarkRegistration'] = self.runTest

  def runTest(self):
    tester = LandmarkRegistrationTest()
    tester.runTest()

#
# qLandmarkRegistrationWidget
#

class LandmarkRegistrationWidget:
  """The module GUI widget"""
  def __init__(self, parent = None):
    self.logic = LandmarkRegistrationLogic()
    self.sliceNodesByViewName = {}
    self.sliceNodesByVolumeID = {}
    self.observerTags = []
    self.viewNames = ("Fixed", "Moving", "Transformed")
    self.volumeSelectDialog = None

    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    """Instantiate and connect widgets ..."""

    self.selectVolumesButton = qt.QPushButton("Select Volumes To Register")
    self.selectVolumesButton.connect('clicked(bool)', self.enter)
    self.layout.addWidget(self.selectVolumesButton)

    self.interfaceFrame = qt.QWidget(self.parent)
    self.interfaceFrame.setLayout(qt.QVBoxLayout())
    self.layout.addWidget(self.interfaceFrame)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.interfaceFrame.layout().addWidget(parametersCollapsibleButton)
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    self.volumeSelectors = {}
    for viewName in self.viewNames:
      self.volumeSelectors[viewName] = slicer.qMRMLNodeComboBox()
      self.volumeSelectors[viewName].nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
      self.volumeSelectors[viewName].selectNodeUponCreation = False
      self.volumeSelectors[viewName].addEnabled = False
      self.volumeSelectors[viewName].removeEnabled = True
      self.volumeSelectors[viewName].noneEnabled = True
      self.volumeSelectors[viewName].showHidden = False
      self.volumeSelectors[viewName].showChildNodeTypes = True
      self.volumeSelectors[viewName].setMRMLScene( slicer.mrmlScene )
      self.volumeSelectors[viewName].setToolTip( "Pick the %s volume." % viewName.lower() )
      self.volumeSelectors[viewName].enabled = False
      parametersFormLayout.addRow("%s Volume " % viewName, self.volumeSelectors[viewName])

    self.volumeSelectors["Transformed"].addEnabled = True
    self.volumeSelectors["Transformed"].selectNodeUponCreation = True
    self.volumeSelectors["Transformed"].setToolTip( "Pick the transformed volume, which is the target for the registration." )

    #
    # Visualization Widget
    # - handy options for controlling the view
    #
    self.visualizationWidget = VisualizationWidget(self.logic)
    self.visualizationWidget.connect("layoutRequested(mode,volumesToShow)", self.onLayout)
    parametersFormLayout.addRow(self.visualizationWidget.widget)

    #
    # Landmarks Widget
    # - manages landmarks
    #
    self.landmarksWidget = LandmarksWidget(self.logic)
    self.landmarksWidget.connect("landmarkPicked(landmarkName)", self.onLandmarkPicked)
    self.landmarksWidget.connect("landmarkMoved(landmarkName)", self.onLandmarkMoved)
    parametersFormLayout.addRow(self.landmarksWidget.widget)

    #
    # Registration Options
    #
    registrationCollapsibleButton = ctk.ctkCollapsibleButton()
    registrationCollapsibleButton.text = "Registration"
    self.interfaceFrame.layout().addWidget(registrationCollapsibleButton)
    registrationFormLayout = qt.QFormLayout(registrationCollapsibleButton)

    #
    # registration type selection
    # - allows selection of the active registration type to display
    #
    self.registrationTypeBox = qt.QGroupBox("Registration Type")
    self.registrationTypeBox.setLayout(qt.QFormLayout())
    self.registrationTypeButtons = {}
    self.registrationTypes = ("Linear", "Thin Plate", "Hybrid B-Spline")
    self.enabledRegistrationTypes = ("Linear",)
    for registrationType in self.registrationTypes:
      self.registrationTypeButtons[registrationType] = qt.QRadioButton()
      self.registrationTypeButtons[registrationType].text = registrationType
      self.registrationTypeButtons[registrationType].setToolTip("Pick the type of registration")
      self.registrationTypeButtons[registrationType].connect("clicked()",
                                      lambda t=registrationType: self.onRegistrationType(t))
      self.registrationTypeBox.layout().addWidget(self.registrationTypeButtons[registrationType])
      if registrationType not in self.enabledRegistrationTypes:
        self.registrationTypeButtons[registrationType].enabled = False
    if len(self.enabledRegistrationTypes) <= 1:
      self.registrationTypeBox.hide()

    registrationFormLayout.addWidget(self.registrationTypeBox)

    #
    # Linear Registration Pane - initially hidden
    # - interface options for linear registration
    # - TODO: move registration code into separate plugins
    #
    self.linearCollapsibleButton = ctk.ctkCollapsibleButton()
    self.linearCollapsibleButton.text = "Linear Registration"
    linearFormLayout = qt.QFormLayout()
    self.linearCollapsibleButton.setLayout(linearFormLayout)
    registrationFormLayout.addWidget(self.linearCollapsibleButton)

    self.linearRegistrationActive = qt.QCheckBox()
    self.linearRegistrationActive.checked = True
    self.linearRegistrationActive.connect("toggled(bool)", self.onLinearActive)
    linearFormLayout.addRow("Registration Active: ", self.linearRegistrationActive)

    buttonLayout = qt.QVBoxLayout()
    self.linearModeButtons = {}
    self.linearModes = ("Rigid", "Similarity", "Affine")
    for mode in self.linearModes:
      self.linearModeButtons[mode] = qt.QRadioButton()
      self.linearModeButtons[mode].text = mode
      self.linearModeButtons[mode].setToolTip( "Run the registration in %s mode." % mode )
      buttonLayout.addWidget(self.linearModeButtons[mode])
      self.linearModeButtons[mode].connect('clicked(bool)', self.onLinearTransform)
    self.linearModeButtons[self.logic.linearMode].checked = True
    linearFormLayout.addRow("Registration Mode ", buttonLayout)

    self.linearTransformSelector = slicer.qMRMLNodeComboBox()
    self.linearTransformSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.linearTransformSelector.selectNodeUponCreation = True
    self.linearTransformSelector.addEnabled = True
    self.linearTransformSelector.removeEnabled = True
    self.linearTransformSelector.noneEnabled = True
    self.linearTransformSelector.showHidden = False
    self.linearTransformSelector.showChildNodeTypes = False
    self.linearTransformSelector.setMRMLScene( slicer.mrmlScene )
    self.linearTransformSelector.setToolTip( "Pick the transform for linear registration" )
    linearFormLayout.addRow("Target Linear Transform ", self.linearTransformSelector)

    #
    # Thin Plate Spline Registration Pane - initially hidden
    #
    self.thinPlateCollapsibleButton = ctk.ctkCollapsibleButton()
    self.thinPlateCollapsibleButton.text = "Thin Plate Spline Registration"
    thinPlateFormLayout = qt.QFormLayout()
    self.thinPlateCollapsibleButton.setLayout(thinPlateFormLayout)
    registrationFormLayout.addWidget(self.thinPlateCollapsibleButton)

    self.thinPlateApply = qt.QPushButton("Apply")
    self.thinPlateApply.connect('clicked(bool)', self.onThinPlateApply)
    thinPlateFormLayout.addWidget(self.thinPlateApply)

    #
    # Hybrid B-Spline Registration Pane - initially hidden
    #
    self.hybridCollapsibleButton = ctk.ctkCollapsibleButton()
    self.hybridCollapsibleButton.text = "Hybrid B-Spline Registration"
    hybridFormLayout = qt.QFormLayout()
    self.hybridCollapsibleButton.setLayout(hybridFormLayout)
    registrationFormLayout.addWidget(self.hybridCollapsibleButton)

    self.hybridApply = qt.QPushButton("Apply")
    self.hybridApply.connect('clicked(bool)', self.onHybridTransformApply)
    hybridFormLayout.addWidget(self.hybridApply)

    if False:
      # no transform representation yet
      self.hybridTransformSelector = slicer.qMRMLNodeComboBox()
      self.hybridTransformSelector.nodeTypes = ( ("vtkMRMLBSplineTransformNode"), "" )
      self.hybridTransformSelector.selectNodeUponCreation = True
      self.hybridTransformSelector.addEnabled = True
      self.hybridTransformSelector.removeEnabled = True
      self.hybridTransformSelector.noneEnabled = True
      self.hybridTransformSelector.showHidden = False
      self.hybridTransformSelector.showChildNodeTypes = False
      self.hybridTransformSelector.setMRMLScene( slicer.mrmlScene )
      self.hybridTransformSelector.setToolTip( "Pick the transform for Hybrid B-Spline registration" )
      hybridFormLayout.addRow("Target B-Spline Transform ", self.hybridTransformSelector)

    self.registrationTypeInterfaces = {}
    self.registrationTypeInterfaces['Linear'] = self.linearCollapsibleButton
    self.registrationTypeInterfaces['Thin Plate'] = self.thinPlateCollapsibleButton
    self.registrationTypeInterfaces['Hybrid B-Spline'] = self.hybridCollapsibleButton

    for registrationType in self.registrationTypes:
      self.registrationTypeInterfaces[registrationType].enabled = False
      self.registrationTypeInterfaces[registrationType].hide()

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Advanced - Reload && Test"
    reloadCollapsibleButton.collapsed = True
    self.interfaceFrame.layout().addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "LandmarkRegistration Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    # reload and run specific tests
    scenarios = ("Basic", "Linear", "Thin Plate")
    for scenario in scenarios:
      button = qt.QPushButton("Reload and Test %s" % scenario)
      self.reloadAndTestButton.toolTip = "Reload this module and then run the %s self test." % scenario
      reloadFormLayout.addWidget(button)
      button.connect('clicked()', lambda s=scenario: self.onReloadAndTest(scenario=s))


    # connections
    for selector in self.volumeSelectors.values():
      selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onVolumeNodeSelect)

    # listen to the scene
    self.addObservers()

    # Add vertical spacer
    self.layout.addStretch(1)

  def enter(self):
    self.interfaceFrame.enabled = False
    self.setupDialog()

  def setupDialog(self):
    """setup dialog"""

    if not self.volumeSelectDialog:
      self.volumeSelectDialog = qt.QDialog(slicer.util.mainWindow())
      self.volumeSelectDialog.objectName = 'LandmarkRegistrationVolumeSelect'
      self.volumeSelectDialog.setLayout( qt.QVBoxLayout() )

      self.volumeSelectLabel = qt.QLabel()
      self.volumeSelectDialog.layout().addWidget( self.volumeSelectLabel )

      self.volumeSelectorFrame = qt.QFrame()
      self.volumeSelectorFrame.objectName = 'VolumeSelectorFrame'
      self.volumeSelectorFrame.setLayout( qt.QFormLayout() )
      self.volumeSelectDialog.layout().addWidget( self.volumeSelectorFrame )

      self.volumeDialogSelectors = {}
      for viewName in ('Fixed', 'Moving',):
        self.volumeDialogSelectors[viewName] = slicer.qMRMLNodeComboBox()
        self.volumeDialogSelectors[viewName].nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
        self.volumeDialogSelectors[viewName].selectNodeUponCreation = False
        self.volumeDialogSelectors[viewName].addEnabled = False
        self.volumeDialogSelectors[viewName].removeEnabled = True
        self.volumeDialogSelectors[viewName].noneEnabled = True
        self.volumeDialogSelectors[viewName].showHidden = False
        self.volumeDialogSelectors[viewName].showChildNodeTypes = True
        self.volumeDialogSelectors[viewName].setMRMLScene( slicer.mrmlScene )
        self.volumeDialogSelectors[viewName].setToolTip( "Pick the %s volume." % viewName.lower() )
        self.volumeSelectorFrame.layout().addRow("%s Volume " % viewName, self.volumeDialogSelectors[viewName])

      self.volumeButtonFrame = qt.QFrame()
      self.volumeButtonFrame.objectName = 'VolumeButtonFrame'
      self.volumeButtonFrame.setLayout( qt.QHBoxLayout() )
      self.volumeSelectDialog.layout().addWidget( self.volumeButtonFrame )

      self.volumeDialogApply = qt.QPushButton("Apply", self.volumeButtonFrame)
      self.volumeDialogApply.objectName = 'VolumeDialogApply'
      self.volumeDialogApply.setToolTip( "Use currently selected volume nodes." )
      self.volumeButtonFrame.layout().addWidget(self.volumeDialogApply)

      self.volumeDialogCancel = qt.QPushButton("Cancel", self.volumeButtonFrame)
      self.volumeDialogCancel.objectName = 'VolumeDialogCancel'
      self.volumeDialogCancel.setToolTip( "Cancel current operation." )
      self.volumeButtonFrame.layout().addWidget(self.volumeDialogCancel)

      self.volumeDialogApply.connect("clicked()", self.onVolumeDialogApply)
      self.volumeDialogCancel.connect("clicked()", self.volumeSelectDialog.hide)

    self.volumeSelectLabel.setText( "Pick the volumes to use for landmark-based linear registration" )
    self.volumeSelectDialog.show()

  # volumeSelectDialog callback (slot)
  def onVolumeDialogApply(self):
    self.volumeSelectDialog.hide()
    fixedID = self.volumeDialogSelectors['Fixed'].currentNodeID
    movingID = self.volumeDialogSelectors['Moving'].currentNodeID
    if fixedID and movingID:
      self.volumeSelectors['Fixed'].setCurrentNodeID(fixedID)
      self.volumeSelectors['Moving'].setCurrentNodeID(movingID)
      self.linearRegistrationActive.checked = True
      self.onLinearActive(self.linearRegistrationActive.checked)
      self.onLayout()

    self.interfaceFrame.enabled = True

  def cleanup(self):
    self.removeObservers()
    self.landmarksWidget.removeLandmarkObservers()

  def addObservers(self):
    """Observe the mrml scene for changes that we wish to respond to.
    scene observer:
     - whenever a new node is added, check if it was a new fiducial.
       if so, transform it into a landmark by creating a matching
       fiducial for other volumes
    fiducial obserers:
     - when fiducials are manipulated, perform (or schedule) an update
       to the currently active registration method.
    """
    tag = slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAddedEvent, self.landmarksWidget.requestNodeAddedUpdate)
    tag = slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeRemovedEvent, self.landmarksWidget.requestNodeAddedUpdate)
    self.observerTags.append( (slicer.mrmlScene, tag) )

  def removeObservers(self):
    """Remove observers and any other cleanup needed to
    disconnect from the scene"""
    for obj,tag in self.observerTags:
      obj.RemoveObserver(tag)
    self.observerTags = []

  def currentVolumeNodes(self):
    """List of currently selected volume nodes"""
    volumeNodes = []
    for selector in self.volumeSelectors.values():
      volumeNode = selector.currentNode()
      if volumeNode:
        volumeNodes.append(volumeNode)
    return(volumeNodes)

  def onVolumeNodeSelect(self):
    """When one of the volume selectors is changed"""
    volumeNodes = self.currentVolumeNodes()
    self.landmarksWidget.setVolumeNodes(volumeNodes)
    fixed = self.volumeSelectors['Fixed'].currentNode()
    moving = self.volumeSelectors['Moving'].currentNode()
    transformed = self.volumeSelectors['Transformed'].currentNode()
    for registrationType in self.registrationTypes:
      self.registrationTypeInterfaces[registrationType].enabled = bool(fixed and moving)
    self.logic.hiddenFiducialVolumes = (transformed,)

  def onLayout(self, layoutMode="Axi/Sag/Cor",volumesToShow=None):
    """When the layout is changed by the VisualizationWidget
    volumesToShow: list of the volumes to include, None means include all
    """
    volumeNodes = []
    activeViewNames = []
    for viewName in self.viewNames:
      volumeNode = self.volumeSelectors[viewName].currentNode()
      if volumeNode and not (volumesToShow and viewName not in volumesToShow):
        volumeNodes.append(volumeNode)
        activeViewNames.append(viewName)
    import CompareVolumes
    compareLogic = CompareVolumes.CompareVolumesLogic()
    oneViewModes = ('Axial', 'Sagittal', 'Coronal',)
    if layoutMode in oneViewModes:
      self.sliceNodesByViewName = compareLogic.viewerPerVolume(volumeNodes,viewNames=activeViewNames,orientation=layoutMode)
    elif layoutMode == 'Axi/Sag/Cor':
      self.sliceNodesByViewName = compareLogic.viewersPerVolume(volumeNodes)
    self.overlayFixedOnTransformed()
    self.updateSliceNodesByVolumeID()
    self.onLandmarkPicked(self.landmarksWidget.selectedLandmark)

  def overlayFixedOnTransformed(self):
    """If there are viewers showing the tranfsformed volume
    in the background, make the foreground volume be the fixed volume
    and set opacity to 0.5"""
    fixedNode = self.volumeSelectors['Fixed'].currentNode()
    transformedNode = self.volumeSelectors['Transformed'].currentNode()
    if transformedNode:
      compositeNodes = slicer.util.getNodes('vtkMRMLSliceCompositeNode*')
      for compositeNode in compositeNodes.values():
        if compositeNode.GetBackgroundVolumeID() == transformedNode.GetID():
          compositeNode.SetForegroundVolumeID(fixedNode.GetID())
          compositeNode.SetForegroundOpacity(0.5)

  def onRegistrationType(self,pickedRegistrationType):
    """Pick which registration type to display"""
    for registrationType in self.registrationTypes:
      self.registrationTypeInterfaces[registrationType].hide()
    self.registrationTypeInterfaces[pickedRegistrationType].show()

  def onLinearActive(self,active):
    """Turn on linear mode if possible"""
    if not active:
      print('skipping registration')
      self.logic.disableLinearRegistration()
    else:
      # ensure we have fixed and moving
      fixed = self.volumeSelectors['Fixed'].currentNode()
      moving = self.volumeSelectors['Moving'].currentNode()
      if not (fixed and moving):
        return
      else:
        # create transform and transformed if needed
        transform = self.linearTransformSelector.currentNode()
        if not transform:
          self.linearTransformSelector.addNode()
          transform = self.linearTransformSelector.currentNode()
        transformed = self.volumeSelectors['Transformed'].currentNode()
        if not transformed:
          volumesLogic = slicer.modules.volumes.logic()
          transformedName = "%s-transformed" % moving.GetName()
          transformed = slicer.util.getNode(transformedName)
          if not transformed:
            transformed = volumesLogic.CloneVolume(slicer.mrmlScene, moving, transformedName)
          self.volumeSelectors['Transformed'].setCurrentNode(transformed)
        landmarks = self.logic.landmarksForVolumes((fixed,moving))
        self.logic.enableLinearRegistration(fixed,moving,landmarks,transform,transformed)

  def onLinearTransform(self):
    """Call this whenever linear transform needs to be updated"""
    for mode in self.linearModes:
      if self.linearModeButtons[mode].checked:
        self.logic.linearMode = mode
        self.onLinearActive(self.linearRegistrationActive.checked)
        break

  def onThinPlateApply(self):
    """Call this whenever thin plate needs to be calculated"""
    fixed = self.volumeSelectors['Fixed'].currentNode()
    moving = self.volumeSelectors['Moving'].currentNode()
    if fixed and moving:
      transformed = self.volumeSelectors['Transformed'].currentNode()
      if not transformed:
        volumesLogic = slicer.modules.volumes.logic()
        transformedName = "%s-transformed" % moving.GetName()
        transformed = volumesLogic.CloneVolume(slicer.mrmlScene, moving, transformedName)
        self.volumeSelectors['Transformed'].setCurrentNode(transformed)
      landmarks = self.logic.landmarksForVolumes((fixed,moving))
      self.logic.performThinPlateRegistration(fixed,moving,landmarks,transformed)

  def onHybridTransformApply(self):
    """Call this whenever hybrid transform needs to be calculated"""
    import os,sys
    loadablePath = os.path.join(slicer.modules.plastimatch_slicer_bspline.path,'../../qt-loadable-modules')
    if loadablePath not in sys.path:
      sys.path.append(loadablePath)
    import vtkSlicerPlastimatchModuleLogicPython
    print('running hybrid...')

  def updateSliceNodesByVolumeID(self):
    """Build a mapping to a list of slice nodes
    node that are currently displaying a given volumeID"""
    compositeNodes = slicer.util.getNodes('vtkMRMLSliceCompositeNode*')
    self.sliceNodesByVolumeID = {}
    if self.sliceNodesByViewName:
      for sliceNode in self.sliceNodesByViewName.values():
        for compositeNode in compositeNodes.values():
          if compositeNode.GetLayoutName() == sliceNode.GetLayoutName():
            volumeID = compositeNode.GetBackgroundVolumeID()
            if self.sliceNodesByVolumeID.has_key(volumeID):
              self.sliceNodesByVolumeID[volumeID].append(sliceNode)
            else:
              self.sliceNodesByVolumeID[volumeID] = [sliceNode,]

  def restrictLandmarksToViews(self):
    """Set fiducials so they only show up in the view
    for the volume on which they were defined"""
    volumeNodes = self.currentVolumeNodes()
    if self.sliceNodesByViewName:
      landmarks = self.logic.landmarksForVolumes(volumeNodes)
      for landmarkName in landmarks:
        for fiducialList,index in landmarks[landmarkName]:
          displayNode = fiducialList.GetDisplayNode()
          displayNode.RemoveAllViewNodeIDs()
          volumeNodeID = fiducialList.GetAttribute("AssociatedNodeID")
          if volumeNodeID:
            if self.sliceNodesByVolumeID.has_key(volumeNodeID):
              for sliceNode in self.sliceNodesByVolumeID[volumeNodeID]:
                displayNode.AddViewNodeID(sliceNode.GetID())
                for hiddenVolume in self.logic.hiddenFiducialVolumes:
                  if hiddenVolume and volumeNodeID == hiddenVolume.GetID():
                    displayNode.SetVisibility(False)

  def onLandmarkPicked(self,landmarkName):
    """Jump all slice views such that the selected landmark
    is visible"""
    if not self.landmarksWidget.movingView:
      # only change the fiducials if they are not being manipulated
      self.restrictLandmarksToViews()
    self.updateSliceNodesByVolumeID()
    volumeNodes = self.currentVolumeNodes()
    landmarksByName = self.logic.landmarksForVolumes(volumeNodes)
    if landmarksByName.has_key(landmarkName):
      for fiducialList,index in landmarksByName[landmarkName]:
        volumeNodeID = fiducialList.GetAttribute("AssociatedNodeID")
        if self.sliceNodesByVolumeID.has_key(volumeNodeID):
          point = [0,]*3
          fiducialList.GetNthFiducialPosition(index,point)
          for sliceNode in self.sliceNodesByVolumeID[volumeNodeID]:
            if sliceNode.GetLayoutName() != self.landmarksWidget.movingView:
              sliceNode.JumpSliceByCentering(*point)

  def onLandmarkMoved(self,landmarkName):
    """Called when a landmark is moved (probably through
    manipulation of the widget in the slice view).
    This updates the active registration"""
    # if self.linearRegistrationActive.checked and not self.landmarksWidget.movingView:
    if self.linearRegistrationActive.checked:
      self.onLinearActive(True)

  def onReload(self,moduleName="LandmarkRegistration"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    # delete the old widget instance
    if hasattr(globals()['slicer'].modules, widgetName):
      getattr(globals()['slicer'].modules, widgetName).cleanup()

    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
    setattr(globals()['slicer'].modules, widgetName, globals()[widgetName.lower()])

  def onReloadAndTest(self,moduleName="LandmarkRegistration",scenario=None):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest(scenario=scenario)
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")

class pqWidget(object):
  """
  A "QWidget"-like widget class that manages provides some
  helper functionality (signals, slots...)
  """
  def __init__(self):
    self.connections = {} # list of slots per signal

  def connect(self,signal,slot):
    """pseudo-connect - signal is arbitrary string and slot if callable"""
    if not self.connections.has_key(signal):
      self.connections[signal] = []
    self.connections[signal].append(slot)

  def disconnect(self,signal,slot):
    """pseudo-disconnect - remove the connection if it exists"""
    if self.connections.has_key(signal):
      if slot in self.connections[signal]:
        self.connections[signal].remove(slot)

  def emit(self,signal,args):
    """pseudo-emit - calls any slots connected to signal"""
    if self.connections.has_key(signal):
      for slot in self.connections[signal]:
        slot(*args)


class VisualizationWidget(pqWidget):
  """
  A "QWidget"-like class that manages some of the viewer options
  used during registration
  """

  def __init__(self,logic):
    super(VisualizationWidget,self).__init__()
    self.logic = logic
    self.volumes = ("Fixed", "Moving", "Transformed",)
    self.layoutOptions = ("Axial", "Coronal", "Sagittal", "Axi/Sag/Cor",)
    self.layoutOption = 'Axi/Sag/Cor'
    self.volumeDisplayCheckboxes = {}

    # mimic the structure of the LandmarksWidget for visual
    # consistency (it needs sub widget so it can delete and refresh the internals)
    self.widget = qt.QWidget()
    self.layout = qt.QFormLayout(self.widget)
    self.boxHolder = qt.QWidget()
    self.boxHolder.setLayout(qt.QVBoxLayout())
    self.layout.addRow(self.boxHolder)
    self.groupBox = qt.QGroupBox("Visualization")
    self.groupBoxLayout = qt.QFormLayout(self.groupBox)
    self.boxHolder.layout().addWidget(self.groupBox)

    #
    # layout selection
    #
    layoutHolder = qt.QWidget()
    layout = qt.QHBoxLayout()
    layoutHolder.setLayout(layout)
    for layoutOption in self.layoutOptions:
      layoutButton = qt.QPushButton(layoutOption)
      layoutButton.connect('clicked()', lambda lo=layoutOption: self.selectLayout(lo))
      layout.addWidget(layoutButton)
    self.groupBoxLayout.addRow("Layout", layoutHolder)

    #
    # Volume display selection
    #
    checkboxHolder = qt.QWidget()
    layout = qt.QHBoxLayout()
    checkboxHolder.setLayout(layout)
    for volume in self.volumes:
      checkBox = qt.QCheckBox()
      checkBox.text = volume
      checkBox.checked = True
      checkBox.connect('toggled(bool)', self.updateVisualization)
      layout.addWidget(checkBox)
      self.volumeDisplayCheckboxes[volume] = checkBox
    self.groupBoxLayout.addRow("Display", checkboxHolder)

    #
    # fade slider
    #
    self.fadeSlider = ctk.ctkSliderWidget()
    self.fadeSlider.minimum = 0
    self.fadeSlider.maximum = 1.0
    self.fadeSlider.value = 0.5
    self.fadeSlider.singleStep = 0.05
    self.fadeSlider.connect('valueChanged(double)', self.onFadeChanged)
    self.groupBoxLayout.addRow("Cross Fade", self.fadeSlider)

    #
    # zoom control
    #
    zoomHolder = qt.QWidget()
    layout = qt.QHBoxLayout()
    zoomHolder.setLayout(layout)
    zooms = {"+": 0.9, "-": 1.1, "Fit": "Fit",}
    for zoomLabel,zoomFactor in zooms.items():
      zoomButton = qt.QPushButton(zoomLabel)
      zoomButton.connect('clicked()', lambda zf=zoomFactor: self.onZoom(zf))
      layout.addWidget(zoomButton)
    self.groupBoxLayout.addRow("Zoom", zoomHolder)

  def selectLayout(self,layoutOption):
    """Keep track of the currently selected layout and trigger an update"""
    self.layoutOption = layoutOption
    self.updateVisualization()

  def updateVisualization(self):
    """When there's a change in the layout requested by either
    the layout or the volume display options, emit a signal that
    summarizes their state"""
    volumesToShow = []
    for volume in self.volumes:
      if self.volumeDisplayCheckboxes[volume].checked:
        volumesToShow.append(volume)
    self.fadeSlider.enabled = "Transformed" in volumesToShow
    self.emit("layoutRequested(mode,volumesToShow)", (self.layoutOption,volumesToShow))

  def onFadeChanged(self,value):
    """Update all the slice compositing"""
    nodes = slicer.util.getNodes('vtkMRMLSliceCompositeNode*')
    for node in nodes.values():
      node.SetForegroundOpacity(value)

  def onZoom(self,zoomFactor):
    import CompareVolumes
    compareLogic = CompareVolumes.CompareVolumesLogic()
    compareLogic.zoom(zoomFactor)



class LandmarksWidget(pqWidget):
  """
  A "QWidget"-like class that manages a set of landmarks
  that are pairs of fiducials
  """

  def __init__(self,logic):
    super(LandmarksWidget,self).__init__()
    self.logic = logic
    self.volumeNodes = []
    self.selectedLandmark = None # a landmark name
    self.landmarkGroupBox = None # a QGroupBox
    self.buttons = {} # the current buttons in the group box
    self.pendingUpdate = False # update on new scene nodes
    self.updatingFiducials = False # don't update while update in process
    self.observerTags = [] # for monitoring fiducial changes
    self.movingView = None # layoutName of slice node where fiducial is being moved

    self.widget = qt.QWidget()
    self.layout = qt.QFormLayout(self.widget)
    self.landmarkArrayHolder = qt.QWidget()
    self.landmarkArrayHolder.setLayout(qt.QVBoxLayout())
    self.layout.addRow(self.landmarkArrayHolder)
    self.updateLandmarkArray()

  def setVolumeNodes(self,volumeNodes):
    """Set up the widget to reflect the currently selected
    volume nodes.  This triggers an update of the landmarks"""
    self.volumeNodes = volumeNodes
    self.updateLandmarkArray()

  def updateLandmarkArray(self):
    """Rebuild the list of buttons based on current landmarks"""
    # reset the widget
    if self.landmarkGroupBox:
      self.landmarkGroupBox.setParent(None)
    self.landmarkGroupBox = qt.QGroupBox("Landmarks")
    self.landmarkGroupBox.setLayout(qt.QFormLayout())
    # add the action buttons at the top
    actionButtons = qt.QHBoxLayout()
    self.addButton = qt.QPushButton("Add")
    self.addButton.connect('clicked()', self.addLandmark)
    actionButtons.addWidget(self.addButton)
    self.removeButton = qt.QPushButton("Remove")
    self.removeButton.connect('clicked()', self.removeLandmark)
    self.removeButton.enabled = False
    actionButtons.addWidget(self.removeButton)
    self.renameButton = qt.QPushButton("Rename")
    self.renameButton.connect('clicked()', self.renameLandmark)
    self.renameButton.enabled = False
    actionButtons.addWidget(self.renameButton)
    self.landmarkGroupBox.layout().addRow(actionButtons)

    # for now, hide these
    #self.addButton.hide()
    self.removeButton.hide()
    self.renameButton.hide()

    # make a button for each current landmark
    self.buttons = {}
    landmarks = self.logic.landmarksForVolumes(self.volumeNodes)
    keys = landmarks.keys()
    keys.sort()
    for landmarkName in keys:
      button = qt.QPushButton(landmarkName)
      button.connect('clicked()', lambda l=landmarkName: self.pickLandmark(l))
      self.landmarkGroupBox.layout().addRow( button )
      self.buttons[landmarkName] = button
    self.landmarkArrayHolder.layout().addWidget(self.landmarkGroupBox)

    # observe manipulation of the landmarks
    self.addLandmarkObservers()

  def addLandmarkObservers(self):
    """Add observers to all fiducialLists in scene
    so we will know when new markups are added
    """
    self.removeLandmarkObservers()
    for fiducialList in slicer.util.getNodes('vtkMRMLMarkupsFiducialNode*').values():
      tag = fiducialList.AddObserver(
              fiducialList.PointModifiedEvent, lambda caller,event: self.onFiducialMoved(caller))
      self.observerTags.append( (fiducialList,tag) )
      tag = fiducialList.AddObserver(
              fiducialList.MarkupAddedEvent, self.requestNodeAddedUpdate)
      self.observerTags.append( (fiducialList,tag) )
      tag = fiducialList.AddObserver(
              fiducialList.MarkupRemovedEvent, self.requestNodeAddedUpdate)
      self.observerTags.append( (fiducialList,tag) )

  def onFiducialMoved(self,fiducialList):
    """Callback when fiducialList's point has been changed.
    Check the Markups.State attribute to see if it is being
    actively moved and if so, skip the picked method."""
    self.movingView = fiducialList.GetAttribute('Markups.MovingInSliceView')
    movingIndexAttribute = fiducialList.GetAttribute('Markups.MovingMarkupIndex')
    if self.movingView and movingIndexAttribute:
      movingIndex = int(movingIndexAttribute)
      landmarkName = fiducialList.GetNthMarkupLabel(movingIndex)
      self.pickLandmark(landmarkName,clearMovingView=False)
      self.emit("landmarkMoved(landmarkName)", (landmarkName,))

  def removeLandmarkObservers(self):
    """Remove any existing observers"""
    for obj,tag in self.observerTags:
      obj.RemoveObserver(tag)
    self.observerTags = []

  def pickLandmark(self,landmarkName,clearMovingView=True):
    """Hightlight the named landmark button and emit
    a 'signal'"""
    for key in self.buttons.keys():
      self.buttons[key].text = key
    try:
      self.buttons[landmarkName].text = '*' + landmarkName
    except KeyError:
      pass
    self.selectedLandmark = landmarkName
    self.renameButton.enabled = True
    self.removeButton.enabled = True
    if clearMovingView:
      self.movingView = None
    self.emit("landmarkPicked(landmarkName)", (landmarkName,))

  def addLandmark(self):
    """Enable markup place mode so fiducial can be added.
    When the node is added it will be incorporated into the
    registration system as a landmark.
    """
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()

    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    interactionNode = applicationLogic.GetInteractionNode()
    interactionNode.SwitchToSinglePlaceMode()

  def removeLandmark(self):
    self.logic.removeLandmarkForVolumes(self.selectedLandmark, self.volumeNodes)
    self.selectedLandmark = None
    self.updateLandmarkArray()

  def renameLandmark(self):
    landmarks = self.logic.landmarksForVolumes(self.volumeNodes)
    if landmarks.has_key(self.selectedLandmark):
      newName = qt.QInputDialog.getText(
          slicer.util.mainWindow(), "Rename Landmark",
          "New name for landmark '%s'?" % self.selectedLandmark)
      if newName != "":
        for fiducialList,index in landmarks[self.selectedLandmark]:
          fiducialList.SetNthFiducialLabel(newName)
        self.selectedLandmark = newName
        self.updateLandmarkArray()
        self.pickLandmark(newName)

  def requestNodeAddedUpdate(self,caller,event):
    """Start a SingleShot timer that will check the fiducials
    in the scene and turn them into landmarks if needed"""
    if not self.pendingUpdate:
      qt.QTimer.singleShot(0, self.wrappedNodeAddedUpdate)
      self.pendingUpdate = True

  def wrappedNodeAddedUpdate(self):
    try:
      self.nodeAddedUpdate()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Node Added", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")

  def nodeAddedUpdate(self):
    """Perform the update of any new fiducials.
    First collect from any fiducial lists not associated with one of our
    lists (like when the process first gets started) and then check for
    new fiducials added to one of our lists.
    End result should be one fiducial per list with identical names and
    correctly assigned associated node ids.
    Most recently created new fiducial is picked as active landmark.
    """
    if self.updatingFiducials:
      return
    self.updatingFiducials = True
    addedAssociatedLandmark = self.logic.collectAssociatedFiducials(self.volumeNodes)
    addedLandmark = self.logic.landmarksFromFiducials(self.volumeNodes)
    if not addedLandmark:
      addedLandmark = addedAssociatedLandmark
    if addedLandmark:
      self.pickLandmark(addedLandmark)
    self.addLandmarkObservers()
    self.updateLandmarkArray()
    self.pendingUpdate = False
    self.updatingFiducials = False

#
# LandmarkRegistrationLogic
#

class LandmarkRegistrationLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget

  The representation of Landmarks is in terms of matching FiducialLists
  with one list per VolumeNode.

  volume1 <-- associated node -- FiducialList1
                                 - anatomy 1
                                 - anatomy 2
                                 ...
  volume2 <-- associated node -- FiducialList2
                                 - anatomy 1
                                 - anatomy 2
                                 ...

  The Fiducial List is only made visible in the viewer that
  has the associated node in the bg.

  Set of identically named fiducials in lists associated with the
  current moving and fixed volumes define a 'landmark'.

  Note that it is the name, not the index, of the anatomy that defines
  membership in a landmark.  Use a pair (fiducialListNodes,index) to
  identify a fiducial.
  """
  def __init__(self):
    self.linearMode = 'Rigid'
    self.hiddenFiducialVolumes = ()

  def addFiducial(self,name,position=(0,0,0),associatedNode=None):
    """Add an instance of a fiducial to the scene for a given
    volume node.  Creates a new list if needed.
    If list already has a fiducial with the given name, then
    set the position to the passed value.
    """

    markupsLogic = slicer.modules.markups.logic()
    originalActiveListID = markupsLogic.GetActiveListID() # TODO: naming convention?
    slicer.mrmlScene.StartState(slicer.mrmlScene.BatchProcessState)

    # make the fiducial list if required
    listName = associatedNode.GetName() + "-landmarks"
    fiducialList = slicer.util.getNode(listName)
    if not fiducialList:
      fiducialListNodeID = markupsLogic.AddNewFiducialNode(listName,slicer.mrmlScene)
      fiducialList = slicer.util.getNode(fiducialListNodeID)
      if associatedNode:
        fiducialList.SetAttribute("AssociatedNodeID", associatedNode.GetID())
      displayNode = fiducialList.GetDisplayNode()
      # TODO: pick appropriate defaults
      # 135,135,84
      displayNode.SetTextScale(6.)
      displayNode.SetGlyphScale(6.)
      displayNode.SetGlyphTypeFromString('StarBurst2D')
      displayNode.SetColor((1,1,0))
      #displayNode.GetAnnotationTextDisplayNode().SetColor((1,1,0))
      displayNode.SetVisibility(True)

    # make this active so that the fids will be added to it
    markupsLogic.SetActiveListID(fiducialList)

    foundLandmarkFiducial = False
    fiducialSize = fiducialList.GetNumberOfFiducials()
    for fiducialIndex in range(fiducialSize):
      if fiducialList.GetNthFiducialLabel(fiducialIndex) == name:
        fiducialList.SetNthFiducialPosition(fiducialIndex, *position)
        foundLandmarkFiducial = True
        break

    if not foundLandmarkFiducial:
      fiducialList.AddFiducial(*position)
      fiducialIndex = fiducialList.GetNumberOfFiducials()-1

    fiducialList.SetNthFiducialLabel(fiducialIndex, name)
    fiducialList.SetNthFiducialSelected(fiducialIndex, False)
    fiducialList.SetNthMarkupLocked(fiducialIndex, False)

    originalActiveList = slicer.util.getNode(originalActiveListID)
    if originalActiveList:
      markupsLogic.SetActiveListID(originalActiveList)
    slicer.mrmlScene.EndState(slicer.mrmlScene.BatchProcessState)


  def addLandmark(self,volumeNodes=[], position=(0,0,0)):
    """Add a new landmark by adding correspondingly named
    fiducials to all the current volume nodes.
    Find a unique name for the landmark and place it at the origin.
    """
    landmarks = self.landmarksForVolumes(volumeNodes)
    index = 0
    while True:
      landmarkName = 'L-%d' % index
      if not landmarkName in landmarks.keys():
        break
      index += 1
    for volumeNode in volumeNodes:
      fiducial = self.addFiducial(landmarkName, position=position,associatedNode=volumeNode)
    return landmarkName

  def removeLandmarkForVolumes(self,landmark,volumeNodes):
    """Remove the fiducial nodes from all the volumes.
    """
    slicer.mrmlScene.StartState(slicer.mrmlScene.BatchProcessState)
    landmarks = self.landmarksForVolumes(volumeNodes)
    if landmarks.has_key(landmark):
      for fiducialList,fiducialIndex in landmarks[landmark]:
        fiducialList.RemoveMarkup(fiducialIndex)
    slicer.mrmlScene.EndState(slicer.mrmlScene.BatchProcessState)

  def volumeFiducialList(self,volumeNode):
    """return fiducial list node that is
    list associated with the given volume node"""
    listName = volumeNode.GetName() + "-landmarks"
    return slicer.util.getNode(listName)

  def landmarksForVolumes(self,volumeNodes):
    """Return a dictionary of keyed by
    landmark name containing pairs (fiducialListNodes,index)
    Only fiducials that exist for all volumes are returned."""
    landmarksByName = {}
    for volumeNode in volumeNodes:
      listForVolume = self.volumeFiducialList(volumeNode)
      if listForVolume:
        fiducialSize = listForVolume.GetNumberOfMarkups()
        for fiducialIndex in range(fiducialSize):
          fiducialName = listForVolume.GetNthFiducialLabel(fiducialIndex)
          if landmarksByName.has_key(fiducialName):
            landmarksByName[fiducialName].append((listForVolume,fiducialIndex))
          else:
            landmarksByName[fiducialName] = [(listForVolume,fiducialIndex),]
    for fiducialName in landmarksByName.keys():
      if len(landmarksByName[fiducialName]) != len(volumeNodes):
        landmarksByName.__delitem__(fiducialName)
    return landmarksByName

  def ensureFiducialInListForVolume(self,volumeNode,landmarkName,landmarkPosition):
    """Make sure the fiducial list associated with the given
    volume node contains a fiducial named landmarkName and that it
    is associated with volumeNode.  If it does not have one, add one
    and put it at landmarkPosition."""
    fiducialList = self.volumeFiducialList(volumeNode)
    fiducialSize = fiducialList.GetNumberOfMarkups()
    for fiducialIndex in range(fiducialSize):
      if fiducialList.GetNthFiducialLabel(fiducialIndex) == landmarkName:
        fiducialList.SetNthMarkupAssociatedNodeID(fiducialIndex, volumeNode.GetID())
        return None
    # if we got here, then there is no fiducial with this name so add one
    fiducialList.AddFiducial(*landmarkPosition)
    fiducialIndex = fiducialList.GetNumberOfFiducials()-1
    fiducialList.SetNthFiducialLabel(fiducialIndex, landmarkName)
    fiducialList.SetNthFiducialSelected(fiducialIndex, False)
    fiducialList.SetNthMarkupLocked(fiducialIndex, False)
    return landmarkName

  def collectAssociatedFiducials(self,volumeNodes):
    """Look at each fiducial list in scene and find any fiducials associated
    with one of our volumes but not in in one of our lists.
    Add the fiducial as a landmark and delete it from the other list.
    Return the name of the last added landmark if it exists.
    """
    addedLandmark = None
    volumeNodeIDs = []
    for volumeNode in volumeNodes:
      volumeNodeIDs.append(volumeNode.GetID())
    landmarksByName = self.landmarksForVolumes(volumeNodes)
    fiducialListsInScene = slicer.util.getNodes('vtkMRMLMarkupsFiducialNode*')
    landmarkFiducialLists = []
    for landmarkName in landmarksByName.keys():
      for fiducialList,index in landmarksByName[landmarkName]:
        if fiducialList not in landmarkFiducialLists:
          landmarkFiducialLists.append(fiducialList)
    listIndexToRemove = [] # remove back to front after identifying them
    for fiducialList in fiducialListsInScene.values():
      if fiducialList not in landmarkFiducialLists:
        # this is not one of our fiducial lists, so look for fiducials
        # associated with one of our volumes
        fiducialSize = fiducialList.GetNumberOfMarkups()
        for fiducialIndex in range(fiducialSize):
          associated = fiducialList.GetNthMarkupAssociatedNodeID(fiducialIndex)
          if fiducialList.GetNthMarkupAssociatedNodeID(fiducialIndex) in volumeNodeIDs:
            # found one, so add it as a landmark
            landmarkPosition = fiducialList.GetMarkupPointVector(fiducialIndex,0)
            addedLandmark = self.addLandmark(volumeNodes,landmarkPosition)
            listIndexToRemove.insert(0,(fiducialList,fiducialIndex))
    for fiducialList,fiducialIndex in listIndexToRemove:
      fiducialList.RemoveMarkup(fiducialIndex)
    return addedLandmark

  def landmarksFromFiducials(self,volumeNodes):
    """Look through all fiducials in the scene and make sure they
    are in a fiducial list that is associated with the same
    volume node.  If they are in the wrong list fix the node id, and make a new
    duplicate fiducial in the correct list.
    This can be used when responding to new fiducials added to the scene.
    Returns the most recently added landmark (or None).
    """
    addedLandmark = None
    for volumeNode in volumeNodes:
      fiducialList = self.volumeFiducialList(volumeNode)
      if not fiducialList:
        print("no fiducialList for volume %s" % volumeNode.GetName())
        continue
      fiducialSize = fiducialList.GetNumberOfMarkups()
      for fiducialIndex in range(fiducialSize):
        fiducialAssociatedVolumeID = fiducialList.GetNthMarkupAssociatedNodeID(fiducialIndex)
        landmarkName = fiducialList.GetNthFiducialLabel(fiducialIndex)
        landmarkPosition = fiducialList.GetMarkupPointVector(fiducialIndex,0)
        if fiducialAssociatedVolumeID != volumeNode.GetID():
          # fiducial was placed on a viewer associated with the non-active list, so change it
          fiducialList.SetNthMarkupAssociatedNodeID(fiducialIndex,volumeNode.GetID())
        # now make sure all other lists have a corresponding fiducial (same name)
        for otherVolumeNode in volumeNodes:
          if otherVolumeNode != volumeNode:
            addedFiducial = self.ensureFiducialInListForVolume(otherVolumeNode,landmarkName,landmarkPosition)
            if addedFiducial:
              addedLandmark = addedFiducial
    return addedLandmark

  def enableLinearRegistration(self,fixed,moving,landmarks,transform,transformed):
    self.performLinearRegistration(fixed,moving,landmarks,transform,transformed)
    # TODO: set up observers on fixed and moving fiducial
    pass

  def performLinearRegistration(self,fixed,moving,landmarks,transform,transformed):
    """Perform the linear transform using the vtkLandmarkTransform class"""

    if transformed.GetTransformNodeID() != transform.GetID():
      transformed.SetAndObserveTransformNodeID(transform.GetID())

    # try to use user selection, but fall back if not enough points are available
    landmarkTransform = vtk.vtkLandmarkTransform()
    if self.linearMode == 'Rigid':
      landmarkTransform.SetModeToRigidBody()
    if self.linearMode == 'Similarity':
      landmarkTransform.SetModeToSimilarity()
    if self.linearMode == 'Affine':
      landmarkTransform.SetModeToAffine()
    if len(landmarks.values()) < 3:
      landmarkTransform.SetModeToRigidBody()

    points = {}
    point = [0,]*3
    for volumeNode in (fixed,moving):
      points[volumeNode] = vtk.vtkPoints()
    for fiducials in landmarks.values():
      for volumeNode,fid in zip((fixed,moving),fiducials):
        fiducialList,index = fid
        fiducialList.GetNthFiducialPosition(index,point)
        points[volumeNode].InsertNextPoint(point)
    landmarkTransform.SetSourceLandmarks(points[moving])
    landmarkTransform.SetTargetLandmarks(points[fixed])
    landmarkTransform.Update()
    transform.SetAndObserveMatrixTransformToParent(landmarkTransform.GetMatrix())

  def disableLinearRegistration(self):
    print("disableLinearRegistration")
    pass

  def resliceThroughTransform(self, sourceNode, transform, referenceNode, targetNode):
    """
    Fills the targetNode's vtkImageData with the source after
    applying the transform.  Uses spacing from referenceNode. Ignores any vtkMRMLTransforms.
    sourceNode, referenceNode, targetNode: vtkMRMLScalarVolumeNodes
    transform: vtkAbstractTransform
    """

    # get the transform from RAS back to source pixel space
    sourceRASToIJK = vtk.vtkMatrix4x4()
    sourceNode.GetRASToIJKMatrix(sourceRASToIJK)

    # get the transform from target image space to RAS
    referenceIJKToRAS = vtk.vtkMatrix4x4()
    targetNode.GetIJKToRASMatrix(referenceIJKToRAS)

    # this is the ijkToRAS concatenated with the passed in (abstract)transform
    self.resliceTransform = vtk.vtkGeneralTransform()
    self.resliceTransform.Concatenate(sourceRASToIJK)
    self.resliceTransform.Concatenate(transform)
    self.resliceTransform.Concatenate(referenceIJKToRAS)

    # use the matrix to extract the volume and convert it to an array
    self.reslice = vtk.vtkImageReslice()
    self.reslice.SetInterpolationModeToLinear()
    self.reslice.InterpolateOn()
    self.reslice.SetResliceTransform(self.resliceTransform)
    self.reslice.SetInput( sourceNode.GetImageData() )

    dimensions = referenceNode.GetImageData().GetDimensions()
    self.reslice.SetOutputExtent(0, dimensions[0]-1, 0, dimensions[1]-1, 0, dimensions[2]-1)
    self.reslice.SetOutputOrigin((0,0,0))
    self.reslice.SetOutputSpacing((1,1,1))

    self.reslice.UpdateWholeExtent()
    targetNode.SetAndObserveImageData(self.reslice.GetOutput())

  def performThinPlateRegistration(self,fixed,moving,landmarks,transformed):
    """Perform the thin plate transform using the vtkThinPlateSplineTransform class"""

    print('performing thin plate registration')
    transformed.SetAndObserveTransformNodeID(None)

    self.thinPlateTransform = vtk.vtkThinPlateSplineTransform()
    self.thinPlateTransform.SetBasisToR() # for 3D transform
    points = {}
    point = [0,]*3
    for volumeNode in (fixed,moving):
      points[volumeNode] = vtk.vtkPoints()
    for fiducialName in landmarks.keys():
      for volumeNode,fid in zip((fixed,moving),landmarks[fiducialName]):
        fid.GetFiducialCoordinates(point)
        points[volumeNode].InsertNextPoint(point)
    # since this is a resample transform, source is the fixed (resampling target) space
    # and moving is the target space
    self.thinPlateTransform.SetSourceLandmarks(points[fixed])
    self.thinPlateTransform.SetTargetLandmarks(points[moving])
    self.thinPlateTransform.Update()
    self.resliceThroughTransform(moving,self.thinPlateTransform, fixed, transformed)

  def run(self,inputVolume,outputVolume):
    """
    Run the actual algorithm
    """
    return True


class LandmarkRegistrationTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self,scenario=None):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    if scenario == "Basic":
      self.test_LandmarkRegistration1()
    elif scenario == "Linear":
      self.test_LandmarkRegistration2()
    elif scenario == "Thin Plate":
      self.test_LandmarkRegistration3()
    else:
      self.test_LandmarkRegistration1()
      self.test_LandmarkRegistration2()
      self.test_LandmarkRegistration3()

  def test_LandmarkRegistration1(self):
    """
    This tests basic landmarking with two volumes
    """

    self.delayDisplay("Starting test_LandmarkRegistration1")
    #
    # first, get some data
    #
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    mrHead = sampleDataLogic.downloadMRHead()
    dtiBrain = sampleDataLogic.downloadDTIBrain()
    self.delayDisplay('Two data sets loaded')

    w = slicer.modules.LandmarkRegistrationWidget
    w.volumeSelectors["Fixed"].setCurrentNode(dtiBrain)
    w.volumeSelectors["Moving"].setCurrentNode(mrHead)

    logic = LandmarkRegistrationLogic()

    for name,point in (
      ('middle-of-right-eye', [35.115070343017578, 74.803565979003906, -21.032917022705078]),
      ('tip-of-nose', [0.50825262069702148, 128.85432434082031, -48.434154510498047]),
      ('right-ear', [80.0, -26.329217910766602, -15.292181015014648]),
      ):
      logic.addFiducial(name, position=point,associatedNode=mrHead)

    for name,point in (
      ('middle-of-right-eye', [28.432207107543945, 71.112533569335938, -41.938472747802734]),
      ('tip-of-nose', [0.9863210916519165, 94.6998291015625, -49.877540588378906]),
      ('right-ear', [79.28509521484375, -12.95069694519043, 5.3944296836853027]),
      ):
      logic.addFiducial(name, position=point,associatedNode=dtiBrain)

    w.onVolumeNodeSelect()
    w.onLayout()
    w.onLandmarkPicked('tip-of-nose')

    self.delayDisplay('test_LandmarkRegistration1 passed!')

  def test_LandmarkRegistration2(self):
    """
    This tests basic linear registration with two
    volumes (pre- post-surgery)
    """

    self.delayDisplay("Starting test_LandmarkRegistration2")
    #
    # first, get some data
    #
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    pre,post = sampleDataLogic.downloadDentalSurgery()
    self.delayDisplay('Two data sets loaded')

    w = slicer.modules.LandmarkRegistrationWidget
    w.volumeSelectors["Fixed"].setCurrentNode(pre)
    w.volumeSelectors["Moving"].setCurrentNode(post)

    # initiate linear registration
    w.onRegistrationType("Linear")
    w.linearRegistrationActive.checked = True

    w.onLayout(layoutMode="Axi/Sag/Cor")

    self.delayDisplay('test_LandmarkRegistration2 passed!')

  def test_LandmarkRegistration3(self):
    """Test the thin plate spline transform"""
    self.test_LandmarkRegistration2()

    self.delayDisplay('starting test_LandmarkRegistration3')
    w = slicer.modules.LandmarkRegistrationWidget
    pre = w.volumeSelectors["Fixed"].currentNode()
    post = w.volumeSelectors["Moving"].currentNode()

    for name,point in (
      ('L-0', [-91.81303405761719, -36.81013488769531, 76.78043365478516]),
      ('L-1', [-91.81303405761719, -41.065155029296875, 19.57413101196289]),
      ('L-2', [-89.75, -121.12535858154297, 33.5537223815918]),
      ('L-3', [-91.29727935791016, -148.6207275390625, 54.980953216552734]),
      ('L-4', [-89.75, -40.17485046386719, 153.87451171875]),
      ('L-5', [-144.15321350097656, -128.45083618164062, 69.85309600830078]),
      ('L-6', [-40.16628646850586, -128.70603942871094, 71.85968017578125]),):
        w.logic.addFiducial(name, position=point,associatedNode=post)

    for name,point in (
      ('L-0', [-89.75, -48.97413635253906, 70.87068939208984]),
      ('L-1', [-91.81303405761719, -47.7024040222168, 14.120864868164062]),
      ('L-2', [-89.75, -130.1315155029297, 31.712587356567383]),
      ('L-3', [-90.78448486328125, -160.6336212158203, 52.85344696044922]),
      ('L-4', [-85.08663940429688, -47.26158905029297, 143.84193420410156]),
      ('L-5', [-144.1186065673828, -138.91270446777344, 68.24700927734375]),
      ('L-6', [-40.27879333496094, -141.29898071289062, 67.36009216308594]),):
        w.logic.addFiducial(name, position=point,associatedNode=pre)


    w.landmarksWidget.pickLandmark('L-4')
    w.linearRegistrationActive.checked = False
    w.onRegistrationType("Thin Plate")
    w.onThinPlateApply()

    self.delayDisplay('test_LandmarkRegistration3 passed!')


