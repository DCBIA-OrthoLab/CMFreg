import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# SurfaceRegistration
#

class SurfaceRegistration:
  def __init__(self, parent):
    parent.title = "Surface Registration"
    parent.categories = ["CMF Registration"]
    parent.dependencies = []
    parent.contributors = ["Vinicius Boen(Univ of Michigan)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This module organizes a fixed and moving model.
    """
    parent.acknowledgementText = """
    This work is part of the National Alliance for Medical Image
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
    slicer.selfTests['SurfaceRegistration'] = self.runTest

  def runTest(self):
    tester = SurfaceRegistrationTest()
    tester.runTest()

#
# qSurfaceRegistrationWidget
#
class SurfaceRegistrationWidget:
  """The module GUI widget"""
  def __init__(self, parent = None):
    self.logic = SurfaceRegistrationLogic()
    self.sliceNodesByViewName = {}
    self.sliceNodesByVolumeID = {}
    self.observerTags = []

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
    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "SurfaceRegistration Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    #
    # Input Surface Volume Collapsible Button
    #
    inputSurfaceCollapsibleButton = ctk.ctkCollapsibleButton()
    inputSurfaceCollapsibleButton.text = "Select Input Files"
    self.layout.addWidget(inputSurfaceCollapsibleButton)
    inputSurfaceFormLayout = qt.QFormLayout(inputSurfaceCollapsibleButton)
    
    #
    # Input Surface Volume Options
    #
    self.modelSelectors = {}
    self.viewNames = ("Fixed Surface Volume", "Moving Surface Volume")
    for viewName in self.viewNames:
      self.modelSelectors[viewName] = slicer.qMRMLNodeComboBox() 
      self.modelSelectors[viewName].nodeTypes = ( ("vtkMRMLModelNode"), "" ) 
      self.modelSelectors[viewName].selectNodeUponCreation = False
      self.modelSelectors[viewName].addEnabled = False
      self.modelSelectors[viewName].removeEnabled = True
      self.modelSelectors[viewName].noneEnabled = True
      self.modelSelectors[viewName].showHidden = False
      self.modelSelectors[viewName].showChildNodeTypes = True
      self.modelSelectors[viewName].setMRMLScene( slicer.mrmlScene )
      self.modelSelectors[viewName].setToolTip( "Pick the %s surface volume." % viewName.lower() )
      inputSurfaceFormLayout.addRow("%s" % viewName, self.modelSelectors[viewName])
	
    
    #
    # Input Registration Parameters Collapsible Button
    #
    inputRegistrationParametersCollapsibleButton = ctk.ctkCollapsibleButton()
    inputRegistrationParametersCollapsibleButton.text = "Surface Based Registration Options"
    self.layout.addWidget(inputRegistrationParametersCollapsibleButton)
    inputRegistrationParametersFormLayout = qt.QFormLayout(inputRegistrationParametersCollapsibleButton)
	
    #
    # Landmark Transform Mode TYPE SELECTION
    # - allows selection of the active registration type to display
    #
    self.landmarkTransformTypeBox = qt.QGroupBox("Landmark Transform Mode")
    self.landmarkTransformTypeBox.setLayout(qt.QFormLayout())
    self.landmarkTransformTypeButtons = {}
    self.landmarkTransformTypes = ("RigidBody", "Similarity", "Affine")
    for landmarkTransformType in self.landmarkTransformTypes:
      self.landmarkTransformTypeButtons[landmarkTransformType] = qt.QRadioButton()
      self.landmarkTransformTypeButtons[landmarkTransformType].text = landmarkTransformType
      self.landmarkTransformTypeButtons[landmarkTransformType].setToolTip("Pick the type of registration")
      self.landmarkTransformTypeButtons[landmarkTransformType].connect("clicked()",
                                      lambda t=landmarkTransformType: self.onLandmarkTrandformType(t))
      self.landmarkTransformTypeBox.layout().addWidget(self.landmarkTransformTypeButtons[landmarkTransformType])
    inputRegistrationParametersFormLayout.addWidget(self.landmarkTransformTypeBox)

    #
    # Mean Distance Mode TYPE SELECTION
    #
    self.meanDistanceTypeBox = qt.QGroupBox("Mean Distance Mode")
    self.meanDistanceTypeBox.setLayout(qt.QFormLayout())
    self.meanDistanceTypeButtons = {}
    self.meanDistanceTypes = ("RMS", "Absolute Value")
    inputRegistrationParametersFormLayout.addWidget(self.landmarkTransformTypeBox)
    for meanDistanceType in self.meanDistanceTypes:
      self.meanDistanceTypeButtons[meanDistanceType] = qt.QRadioButton()
      self.meanDistanceTypeButtons[meanDistanceType].text = meanDistanceType
      self.meanDistanceTypeButtons[meanDistanceType].setToolTip("Pick the type of registration")
      self.meanDistanceTypeButtons[meanDistanceType].connect("clicked()",
                                      lambda t=meanDistanceType: self.onMeanDistanceType(t))
      self.meanDistanceTypeBox.layout().addWidget(self.meanDistanceTypeButtons[meanDistanceType])
    inputRegistrationParametersFormLayout.addWidget(self.meanDistanceTypeBox)
    
    #
    # Start by Matching Centroids Options
    #
    self.startMatchingCentroids = qt.QCheckBox()
    self.startMatchingCentroids.checked = False
    self.startMatchingCentroids.connect("toggled(bool)", self.onMatchCentroidsLinearActive)
    inputRegistrationParametersFormLayout.addRow("Start by matching centroids ", self.startMatchingCentroids)
	
    #
    # Check Mean Distance Options
    #
    self.checkMeanDistance = qt.QCheckBox()
    self.checkMeanDistance.checked = False
    self.checkMeanDistance.connect("toggled(bool)", self.onCheckMeanDistanceActive)
    inputRegistrationParametersFormLayout.addRow("Check Mean Distance ", self.checkMeanDistance)	
	
    # Number of Iterations
    numberOfIterations = ctk.ctkSliderWidget()
    numberOfIterations.connect('valueChanged(double)', self.numberOfIterationsValueChanged)
    numberOfIterations.decimals = 0
    numberOfIterations.minimum = 2000
    numberOfIterations.maximum = 80000
    numberOfIterations.value = 2000
    inputRegistrationParametersFormLayout.addRow("Number of Iterations:", numberOfIterations)
    
    # Number of Landmarks
    numberOfLandmarks = ctk.ctkSliderWidget()
    numberOfLandmarks.connect('valueChanged(double)', self.numberOfLandmarksValueChanged)
    numberOfLandmarks.decimals = 0
    numberOfLandmarks.minimum = 0
    numberOfLandmarks.maximum = 10000
    numberOfLandmarks.value = 200
    inputRegistrationParametersFormLayout.addRow("Number of Landmarks:", numberOfLandmarks)
	
    # Maximum Distance
    maxDistance = ctk.ctkSliderWidget()
    maxDistance.connect('valueChanged(double)', self.maxDistanceValueChanged)
    maxDistance.decimals = 5
    maxDistance.minimum = 0.00001
    maxDistance.maximum = 1
    maxDistance.value = 0.00001
    inputRegistrationParametersFormLayout.addRow("Maximum Distance:", maxDistance)

    #
    # Output Surface Collapsible Button
    #
    outputSurfaceCollapsibleButton = ctk.ctkCollapsibleButton()
    outputSurfaceCollapsibleButton.text = "Output Registration Matrix"
    self.layout.addWidget(outputSurfaceCollapsibleButton)
    outputSurfaceFormLayout = qt.QFormLayout(outputSurfaceCollapsibleButton)	
	
    #
    # Output Surface Volume Options
    #
    self.modelOutputSurfaceSelectors = {}	
    self.modelOutputSurfaceSelectors["Output Surface Volume"] = slicer.qMRMLNodeComboBox() 
    self.modelOutputSurfaceSelectors["Output Surface Volume"].nodeTypes = ( ("vtkMRMLModelNode"), "" ) 	
    self.modelOutputSurfaceSelectors["Output Surface Volume"].addEnabled = True
    self.modelOutputSurfaceSelectors["Output Surface Volume"].selectNodeUponCreation = True
    self.modelOutputSurfaceSelectors["Output Surface Volume"].removeEnabled = True
    self.modelOutputSurfaceSelectors["Output Surface Volume"].noneEnabled = True
    self.modelOutputSurfaceSelectors["Output Surface Volume"].showHidden = False
    self.modelOutputSurfaceSelectors["Output Surface Volume"].showChildNodeTypes = True
    self.modelOutputSurfaceSelectors["Output Surface Volume"].setMRMLScene( slicer.mrmlScene )
    self.modelOutputSurfaceSelectors["Output Surface Volume"].setToolTip( "Pick the Output Surface Volume" )
    outputSurfaceFormLayout.addRow("Output Surface Volume", self.modelOutputSurfaceSelectors["Output Surface Volume"])
    
    #
    # Output Transform Options
    #
    self.volumeOutputTransformSelectors = {}
    self.volumeOutputTransformSelectors["Output Transform"] = slicer.qMRMLNodeComboBox()
    self.volumeOutputTransformSelectors["Output Transform"].nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.volumeOutputTransformSelectors["Output Transform"].selectNodeUponCreation = True
    self.volumeOutputTransformSelectors["Output Transform"].addEnabled = True
    self.volumeOutputTransformSelectors["Output Transform"].removeEnabled = True
    self.volumeOutputTransformSelectors["Output Transform"].noneEnabled = True
    self.volumeOutputTransformSelectors["Output Transform"].showHidden = False
    self.volumeOutputTransformSelectors["Output Transform"].showChildNodeTypes = True
    self.volumeOutputTransformSelectors["Output Transform"].setMRMLScene( slicer.mrmlScene )
    self.volumeOutputTransformSelectors["Output Transform"].setToolTip("Pick the Output Transform file")
    outputSurfaceFormLayout.addRow("Output Transform", self.volumeOutputTransformSelectors["Output Transform"])
	
	
    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Run Registration")
    self.applyButton.toolTip = "Run the registration algorithm."
    self.applyButton.enabled = True
    outputSurfaceFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)

    # Add vertical spacer
    self.layout.addStretch(1)

    self.checkMeanDistanceActive = False
    self.matchCentroidsLinearActive = False
	
  def numberOfIterationsValueChanged(self, newValue):
    self.numberOfIterationsValueChanged = int(newValue)


  def maxDistanceValueChanged(self, newValue1):
    self.maxDistanceValueChanged = newValue1


  def numberOfLandmarksValueChanged(self, newValue2):
    self.numberOfLandmarksValueChanged = int(newValue2)

  def cleanup(self):
    self.removeObservers()

  def addObservers(self):
    """Observe the mrml scene for changes that we wish to respond to.
    """
    tag = slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAddedEvent)
    self.observerTags.append( (slicer.mrmlScene, tag) )
	
  def removeObservers(self):
    """Remove observers and any other cleanup needed to
    disconnect from the scene"""
    for obj,tag in self.observerTags:
      obj.RemoveObserver(tag)
    self.observerTags = []	
	
  def onLandmarkTrandformType(self,landmarkTransformType):
    """Pick which landmark transform"""
    if landmarkTransformType == "RigidBody":
      self.LandmarkTransformType = "RigidBody"
    elif landmarkTransformType == "Similarity":
      self.LandmarkTransformType = "Similarity"
    elif landmarkTransformType == "Affine":
      self.LandmarkTransformType = "Affine"     
	
  def onMeanDistanceType(self,meanDistanceType):
    """Pick which distance mode"""
    if meanDistanceType == "RMS":
      self.meanDistanceType = "RMS"
    elif meanDistanceType == "Absolute Value":
      self.meanDistanceType = "Absolute Value"
  
  def onMatchCentroidsLinearActive(self,matchCentroidsLinearActive):
    """initialize the transform by translating the input surface so 
	that its centroid coincides the centroid of the target surface."""
    self.matchCentroidsLinearActive = matchCentroidsLinearActive

  def onCheckMeanDistanceActive(self,checkMeanDistanceActive):
    """ force checking distance between every two iterations (slower but more accurate)"""
    self.checkMeanDistanceActive = checkMeanDistanceActive

  def onApplyButton(self):
    """ Aply the Surface ICP Registration """
    self.applyButton.text = "Working..."
    self.applyButton.repaint()
    fixed = self.modelSelectors['Fixed Surface Volume'].currentNode()
    moving = self.modelSelectors['Moving Surface Volume'].currentNode()
    outputSurf = self.modelOutputSurfaceSelectors['Output Surface Volume'].currentNode()
    
    outputTrans = self.volumeOutputTransformSelectors["Output Transform"].currentNode()
	
    meanDistanceType = self.meanDistanceType
    landmarkTransformType = self.LandmarkTransformType
    numberOfLandmarks = self.numberOfLandmarksValueChanged
    maxDistance = self.maxDistanceValueChanged
    numberOfIterations = self.numberOfIterationsValueChanged
    matchCentroids = self.matchCentroidsLinearActive
    checkMeanDistance = self.checkMeanDistanceActive
	
    self.logic.run(fixed, moving, outputSurf, outputTrans, meanDistanceType, 
						landmarkTransformType, numberOfLandmarks, maxDistance, 
								numberOfIterations, matchCentroids, checkMeanDistance)

  def onReload(self,moduleName="SurfaceRegistration"):
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
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
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
		  
#
# SurfaceRegistrationLogic
#
class SurfaceRegistrationLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  
  def run(self, fixed, moving, outputSurf, outputTrans, meanDistanceType, 
						landmarkTransformType, numberOfLandmarks, maxDistance, 
								numberOfIterations, matchCentroids, checkMeanDistance):
    """Run the actual algorithm"""	
    inputPolyData = moving.GetPolyData() 
    
    icp = vtk.vtkIterativeClosestPointTransform()
	
    icp.SetSource(inputPolyData)
    icp.SetTarget(fixed.GetPolyData())

    if landmarkTransformType == "RigidBody":
      icp.GetLandmarkTransform().SetModeToRigidBody()
    elif landmarkTransformType == "Similarity":
      icp.GetLandmarkTransform().SetModeToSimilarity()
    elif landmarkTransformType == "Affine":    
      icp.GetLandmarkTransform().SetModeToAffine()
	  
    if meanDistanceType == "RMS":
      icp.SetMeanDistanceModeToRMS()
    elif meanDistanceType == "Absolute Value":
      icp.SetMeanDistanceModeToAbsoluteValue()
	  
    icp.SetMaximumNumberOfIterations(numberOfIterations)
    icp.SetMaximumMeanDistance(maxDistance)
    icp.SetMaximumNumberOfLandmarks(numberOfLandmarks)
    icp.SetCheckMeanDistance(int(checkMeanDistance))
    icp.SetStartByMatchingCentroids(int(matchCentroids))
    icp.Update()
	
    outputMatrix = vtk.vtkMatrix4x4()
    icp.GetMatrix(outputMatrix)
    outputTrans.SetAndObserveMatrixTransformToParent(outputMatrix)
    
    outputPolyData = vtk.vtkPolyData()
    outputPolyData.DeepCopy(inputPolyData)
    outputSurf.SetAndObservePolyData(outputPolyData)
    return
