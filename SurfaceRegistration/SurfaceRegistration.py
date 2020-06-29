import os
from collections import defaultdict

from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time
import numpy
import json


#
# SurfaceRegistration
#

class SurfaceRegistration(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Surface Registration"
        self.parent.categories = ["Registration.CMF Registration"]
        self.parent.dependencies = []
        self.parent.contributors = ["Jean-Baptiste VIMORT (University of Michigan)", "Vinicius Boen(Univ of Michigan)"]
        self.parent.helpText = """
        This module organizes a fixed and moving model.
    """
        self.parent.acknowledgementText = """
    This work was supported by the National Institute of Dental
    & Craniofacial Research and the National Institute of Biomedical
    Imaging and Bioengineering under Award Number R01DE024450.
    The content is solely the responsibility of the authors and does
    not necessarily represent the official views of the National
    Institutes of Health.
    """


#
# SurfaceRegistrationWidget
#

class SurfaceRegistrationWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        print("-------Surface Registration Widget SetUp--------")
        ScriptedLoadableModuleWidget.setup(self)
        # ------------------------------------------------------------------------------------
        #                                   Global Variables
        # ------------------------------------------------------------------------------------
        self.logic = SurfaceRegistrationLogic(self)
        # -------------------------------------------------------------------------------------
        # Interaction with 3D Scene
        self.interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        #  -----------------------------------------------------------------------------------
        #                        Surface Registration UI setup
        #  -----------------------------------------------------------------------------------
        loader = qt.QUiLoader()
        moduleName = 'SurfaceRegistration'
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' %moduleName)

        qfile = qt.QFile(path)
        qfile.open(qt.QFile.ReadOnly)
        widget = loader.load(qfile, self.parent)
        self.layout = self.parent.layout()
        self.widget = widget
        self.layout.addWidget(widget)

        self.SceneCollapsibleButton = self.logic.get("SceneCollapsibleButton") # this atribute is usefull for Longitudinal quantification extension
        treeView = self.logic.get("treeView")
        treeView.setMRMLScene(slicer.app.mrmlScene())
        treeView.sceneModel().setHorizontalHeaderLabels(["Models"])
        treeView.sortFilterProxyModel().nodeTypes = ['vtkMRMLModelNode','vtkMRMLMarkupsFiducialNode']
        treeView.header().setVisible(False)

        self.registrationCollapsibleButton = self.logic.get("registrationCollapsibleButton")
        self.fiducialRegistration = self.logic.get("fiducialRegistration")
        self.surfaceRegistration = self.logic.get("surfaceRegistration")
        self.ROIRegistration = self.logic.get("ROIRegistration")
        self.InputCollapsibleButton = self.logic.get("InputCollapsibleButton")
        self.inputFixedModelSelector = self.logic.get("inputFixedModelSelector")
        self.inputFixedModelSelector.setMRMLScene(slicer.mrmlScene)
        self.inputMovingModelSelector = self.logic.get("inputMovingModelSelector")
        self.inputMovingModelSelector.setMRMLScene(slicer.mrmlScene)
        self.inputFixedLandmarksSelector = self.logic.get("inputFixedLandmarksSelector")
        self.inputFixedLandmarksSelector.setMRMLScene(slicer.mrmlScene)
        self.inputFixedLandmarksSelector.setEnabled(False) # The "enable" property seems to not be imported from the .ui
        self.inputMovingLandmarksSelector = self.logic.get("inputMovingLandmarksSelector")
        self.inputMovingLandmarksSelector.setMRMLScene(slicer.mrmlScene)
        self.inputMovingLandmarksSelector.setEnabled(False) # The "enable" property seems to not be imported from the .ui
        self.loadFixedLandmarksOnSurfacCheckBox = self.logic.get("loadFixedLandmarksOnSurfacCheckBox")
        self.loadMovingLandmarksOnSurfacCheckBox = self.logic.get("loadMovingLandmarksOnSurfacCheckBox")
        self.LandmarksBox = self.logic.get("LandmarksBox")
        self.landmarksModificationCollapsibleButton = self.logic.get("landmarksModificationCollapsibleButton")
        self.ModelLabel = self.logic.get("ModelLabel")
        self.fixedModel = self.logic.get("fixedModel")
        self.movingModel = self.logic.get("movingModel")
        self.addLandmarksButton = self.logic.get("addLandmarksButton")
        self.landmarkComboBox = self.logic.get("landmarkComboBox")
        self.landmarksScaleWidget = self.logic.get("landmarksScaleWidget")
        self.surfaceDeplacementCheckBox = self.logic.get("surfaceDeplacementCheckBox")
        self.radiusDefinitionWidget = self.logic.get("radiusDefinitionWidget")
        self.cleanerButton = self.logic.get("cleanerButton")
        self.roiGroupBox = self.logic.get("roiGroupBox")
        self.outputCollapsibleButton = self.logic.get("outputCollapsibleButton")
        self.outputTransformLayout = self.logic.get("outputTransformLayout")
        self.outputModelLayout = self.logic.get("outputModelLayout")
        self.outputModelSelector = self.logic.get("outputModelSelector")
        self.outputModelSelector.setMRMLScene(slicer.mrmlScene)
        self.outputTransformSelector = self.logic.get("outputTransformSelector")
        self.outputTransformSelector.setMRMLScene(slicer.mrmlScene)
        self.registrationAdvancedParametersCollapsibleButton = self.logic.get("registrationAdvancedParametersCollapsibleButton")
        self.fiducialAdvancedBox = self.logic.get("fiducialAdvancedBox")
        self.fiducialTransformTypeButtonsTranslation = self.logic.get("fiducialTransformTypeButtonsTranslation")
        self.fiducialTransformTypeButtonsRigid = self.logic.get("fiducialTransformTypeButtonsRigid")
        self.fiducialTransformTypeButtonsSimilarity = self.logic.get("fiducialTransformTypeButtonsSimilarity")
        self.surfaceAdvancedBox = self.logic.get("surfaceAdvancedBox")
        self.landmarkTransformTypeBox = self.logic.get("landmarkTransformTypeBox")
        self.landmarkTransformTypeButtonsRigidBody = self.logic.get("landmarkTransformTypeButtonsRigidBody")
        self.landmarkTransformTypeButtonsSimilarity = self.logic.get("landmarkTransformTypeButtonsSimilarity")
        self.landmarkTransformTypeButtonsAffine = self.logic.get("landmarkTransformTypeButtonsAffine")
        self.meanDistanceTypeBox = self.logic.get("meanDistanceTypeBox")
        self.meanDistanceTypeButtonsRootMeanSquare = self.logic.get("meanDistanceTypeButtonsRootMeanSquare")
        self.meanDistanceTypeButtonsAbsoluteValue = self.logic.get("meanDistanceTypeButtonsAbsoluteValue")
        self.startMatchingCentroids = self.logic.get("startMatchingCentroids")
        self.checkMeanDistance = self.logic.get("checkMeanDistance")
        self.numberOfIterations = self.logic.get("numberOfIterations")
        self.numberOfLandmarks = self.logic.get("numberOfLandmarks")
        self.maxDistance = self.logic.get("maxDistance")
        self.computeButton = self.logic.get("computeButton")
        self.undoButton = self.logic.get("undoButton")
        self.applyButton = self.logic.get("applyButton")

        # ------------------------------------------------------------------------------------
        #                                   CONNECTIONS
        # ------------------------------------------------------------------------------------

        # interactive menu
        self.fiducialRegistration.connect('clicked()', self.onFiducialRegistration)
        self.surfaceRegistration.connect('clicked()', self.onSurfaceRegistration)
        self.ROIRegistration.connect('clicked()', self.onROIRegistration)
        # Registration
        self.computeButton.connect('clicked()', self.onComputeButton)
        self.undoButton.connect('clicked()', self.onUndoButton)
        self.applyButton.connect('clicked()', self.onApply)
        # input modification
        self.inputFixedModelSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onFixedModelChanged)
        self.inputMovingModelSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onMovingModelChanged)
        self.inputFixedLandmarksSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onFixedLandmarksChanged)
        self.inputMovingLandmarksSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onMovingLandmarksCganged)
        # Select of landmarks
        self.addLandmarksButton.connect('clicked()', self.onAddButton)
        self.landmarksScaleWidget.connect('valueChanged(double)', self.onLandmarksScaleChanged)
        self.surfaceDeplacementCheckBox.connect('stateChanged(int)', self.onSurfaceDeplacementStateChanged)
        self.fixedModel.connect('clicked()', self.onFixedModelRadio)
        self.movingModel.connect('clicked()', self.onMovingModelRadio)
        # Select ROI
        self.cleanerButton.connect('clicked()', self.onCleanButton)
        self.landmarkComboBox.connect('currentIndexChanged(QString)', self.onLandmarkComboBoxChanged)
        self.radiusDefinitionWidget.connect('valueChanged(double)', self.onRadiusValueChanged)
        # output modification
        self.outputModelSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onOutputModelChanged)
        # advanced options
        self.landmarkTransformTypeButtonsRigidBody.connect("clicked()", lambda:self.onLandmarkTrandformType("RigidBody"))
        self.landmarkTransformTypeButtonsSimilarity.connect("clicked()", lambda:self.onLandmarkTrandformType("Similarity"))
        self.landmarkTransformTypeButtonsAffine.connect("clicked()", lambda:self.onLandmarkTrandformType("Affine"))
        self.meanDistanceTypeButtonsRootMeanSquare.connect("clicked()",lambda:self.onMeanDistanceType("Root Mean Square"))
        self.meanDistanceTypeButtonsAbsoluteValue.connect("clicked()",lambda:self.onMeanDistanceType("Absolute Value"))
        self.startMatchingCentroids.connect("toggled(bool)", self.onMatchCentroidsLinearActive)
        self.checkMeanDistance.connect("toggled(bool)", self.onCheckMeanDistanceActive)
        self.numberOfIterations.connect('valueChanged(double)', self.numberOfIterationsValueChanged)
        self.numberOfLandmarks.connect('valueChanged(double)', self.numberOfLandmarksValueChanged)
        self.maxDistance.connect('valueChanged(double)', self.maxDistanceValueChanged)

        self.sceneCloseTag = slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.onCloseScene)

        # ------------------------------------------------------------------------------------
        #                                   INITIALISATION
        # ------------------------------------------------------------------------------------

        self.numberOfIterationsValueChanged = 2000
        self.maxDistanceValueChanged = 0.001
        self.numberOfLandmarksValueChanged = 200
        self.checkMeanDistanceActive = False
        self.matchCentroidsLinearActive = False
        self.onMeanDistanceType("Absolute Value")
        self.onLandmarkTrandformType("RigidBody")
        self.onSurfaceRegistration()
        self.UpdateInterface()

    def enter(self):
        fixedModel = self.inputFixedModelSelector.currentNode()
        movingModel = self.inputMovingModelSelector.currentNode()
        fixedFidlist = self.inputFixedLandmarksSelector.currentNode()
        movingFidlist = self.inputMovingLandmarksSelector.currentNode()

        if fixedFidlist:
            if fixedFidlist.GetAttribute("connectedModelID") != fixedModel.GetID():
                self.inputFixedModelSelector.setCurrentNode(None)
                self.inputFixedLandmarksSelector.setCurrentNode(None)
                self.landmarkComboBox.clear()
        if movingFidlist:
            if movingFidlist.GetAttribute("connectedModelID") != movingModel.GetID():
                self.inputMovingModelSelector.setCurrentNode(None)
                self.inputMovingLandmarksSelector.setCurrentNode(None)
                self.landmarkComboBox.clear()
        self.UpdateInterface()

        # Checking the names of the fiducials
        list = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
        end = list.GetNumberOfItems()
        for i in range(0,end):
            fidList = list.GetItemAsObject(i)
            landmarkDescription = self.logic.decodeJSON(fidList.GetAttribute("landmarkDescription"))
            if landmarkDescription:
                for n in range(fidList.GetNumberOfMarkups()):
                    markupID = fidList.GetNthMarkupID(n)
                    markupLabel = fidList.GetNthMarkupLabel(n)
                    landmarkDescription[markupID]["landmarkLabel"] = markupLabel
                fidList.SetAttribute("landmarkDescription",self.logic.encodeJSON(landmarkDescription))

    def onCloseScene(self, obj, event):

        list = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
        end = list.GetNumberOfItems()
        for i in range(0,end):
            model = list.GetItemAsObject(i)
            hardenModel = slicer.mrmlScene.GetNodesByName(model.GetName()).GetItemAsObject(0)
            slicer.mrmlScene.RemoveNode(hardenModel)
        self.logic.selectedModel = None
        self.logic.fixedModel = None
        self.logic.movingModel = None
        self.logic.selectedFidList = None
        self.logic.fixedFidList = None
        self.logic.movingFidList = None
        self.inputFixedModelSelector.setCurrentNode(None)
        self.inputMovingModelSelector.setCurrentNode(None)
        self.inputFixedLandmarksSelector.setCurrentNode(None)
        self.inputMovingLandmarksSelector.setCurrentNode(None)
        self.outputModelSelector.setCurrentNode(None)
        self.outputTransformSelector.setCurrentNode(None)
        self.landmarkComboBox.clear()

    # ------------------------------------------------------------------------------------
    #                                   Update interface
    #                          (third view, ROI landmark and value)
    # ------------------------------------------------------------------------------------

    def UpdateInterface(self):
        if not self.logic.selectedModel:
            return
        activeInput = self.logic.selectedModel
        if not self.logic.selectedFidList:
            return
        fidList = self.logic.selectedFidList
        selectedFidReflID = self.logic.findIDFromLabel(fidList, self.landmarkComboBox.currentText)

        displayFiducialNode = self.logic.selectedFidList.GetMarkupsDisplayNode()
        self.landmarksScaleWidget.value = displayFiducialNode.GetGlyphScale()

        if activeInput:
            # Update values on widgets.
            landmarkDescription = self.logic.decodeJSON(fidList.GetAttribute("landmarkDescription"))
            if landmarkDescription and selectedFidReflID:
                activeDictLandmarkValue = landmarkDescription[selectedFidReflID]
                self.radiusDefinitionWidget.value = activeDictLandmarkValue["ROIradius"]
                if activeDictLandmarkValue["projection"]["isProjected"]:
                    self.surfaceDeplacementCheckBox.setChecked(True)
                else:
                    self.surfaceDeplacementCheckBox.setChecked(False)
            else:
                self.radiusDefinitionWidget.value = 0.0
            self.logic.UpdateThreeDView(self.landmarkComboBox.currentText)


    # ------------------------------------------------------------------------------------
    #                                   ALGORITHM
    # ------------------------------------------------------------------------------------

    def onFiducialRegistration(self):
        self.landmarksModificationCollapsibleButton.checked = False
        self.registrationAdvancedParametersCollapsibleButton.checked = False
        self.landmarksModificationCollapsibleButton.show()
        self.LandmarksBox.show()
        self.roiGroupBox.hide()
        self.fiducialAdvancedBox.show()
        self.surfaceAdvancedBox.hide()

    def onSurfaceRegistration(self):
        self.landmarksModificationCollapsibleButton.checked = False
        self.registrationAdvancedParametersCollapsibleButton.checked = False
        self.landmarksModificationCollapsibleButton.hide()
        self.LandmarksBox.hide()
        self.roiGroupBox.hide()
        self.fiducialAdvancedBox.hide()
        self.surfaceAdvancedBox.show()
        self.startMatchingCentroids.checked = False

    def onROIRegistration(self):
        self.landmarksModificationCollapsibleButton.checked = False
        self.registrationAdvancedParametersCollapsibleButton.checked = False
        self.landmarksModificationCollapsibleButton.show()
        self.LandmarksBox.show()
        self.roiGroupBox.show()
        self.fiducialAdvancedBox.hide()
        self.surfaceAdvancedBox.show()
        self.startMatchingCentroids.checked = True

    # Registration
    def onComputeButton(self):
        if not self.outputTransformSelector.currentNode():
            self.logic.warningMessage("Please select an output transform")
            return
        if not (self.inputMovingModelSelector.currentNode() and self.inputFixedModelSelector.currentNode()):
            self.logic.warningMessage("Please select both model")
            return
        outputTrans = self.outputTransformSelector.currentNode()
        movingModel = self.inputMovingModelSelector.currentNode()
        if outputTrans == movingModel.GetParentTransformNode():
            self.logic.warningMessage(
                "The transform selected as the output transform is also the parent transform of the"
                "moving model! Please select an other transform!")
            return
        # apply the good transform
        if self.fiducialRegistration.isChecked():
            exept = self.applyFiducialRegistration(outputTrans)
            if not exept:
                return
        elif self.surfaceRegistration.isChecked():
            self.applySurfaceRegistration(outputTrans)
        elif self.ROIRegistration.isChecked():
            self.applyROIRegistration(outputTrans)
        # Update interface and 3D scene
        self.outputTransformSelector.setCurrentNode(None)
        movingModel = self.inputMovingModelSelector.currentNode()
        self.logic.displayResult(movingModel, outputTrans)
        self.undoButton.enabled = True
        self.fixedModel.setChecked(True)
        self.onFixedModelRadio()

    def applyFiducialRegistration(self, outputTrans):
        if not (self.inputMovingLandmarksSelector.currentNode() and self.inputFixedLandmarksSelector.currentNode()):
            self.logic.warningMessage("Please select both fiducial lists")
            return False
        fixedLandmarks = self.logic.fixedFidList
        movingLandmarks = self.logic.movingFidList
        saveTransform = outputTrans.GetID()
        if self.fiducialTransformTypeButtonsRigid.isChecked():
            tranformType = "Rigid"
        elif self.fiducialTransformTypeButtonsTranslation.isChecked():
            tranformType = "Translation"
        else:
            tranformType = "Similarity"
        if fixedLandmarks.GetNumberOfFiducials() != movingLandmarks.GetNumberOfFiducials():
            self.logic.warningMessage("Both models must have the same numbers of landmarks")
            return False
        if fixedLandmarks.GetNumberOfFiducials() < 3:
            self.logic.warningMessage("Landmarks lists must have at least 3 landarks")
            return False
        print("------fiducial registration--------")
        self.logic.runFiducialRegistration(fixedLandmarks, movingLandmarks,
                                           saveTransform, tranformType)
        return True

    def applySurfaceRegistration(self, outputTrans):
        print("-------surface registration--------")
        fixedModel = self.logic.fixedModel
        movingModel = self.logic.movingModel
        fixedHarden = slicer.app.mrmlScene().GetNodeByID(fixedModel.GetAttribute("hardenModelID"))
        movingHarden = slicer.app.mrmlScene().GetNodeByID(movingModel.GetAttribute("hardenModelID"))
        fixed = fixedHarden.GetPolyData()
        moving = movingHarden.GetPolyData()
        meanDistanceType = self.meanDistanceType
        landmarkTransformType = self.LandmarkTransformType
        numberOfLandmarks = self.numberOfLandmarksValueChanged
        maxDistance = self.maxDistanceValueChanged
        numberOfIterations = self.numberOfIterationsValueChanged
        matchCentroids = self.matchCentroidsLinearActive
        checkMeanDistance = self.checkMeanDistanceActive
        self.logic.runICP(fixed, moving, outputTrans,
                          meanDistanceType, landmarkTransformType,
                          numberOfLandmarks, maxDistance, numberOfIterations,
                          matchCentroids, checkMeanDistance)

    def applyROIRegistration(self, outputTrans):
        print("-------ROI Registration---------")
        fixedROIPolydata = self.logic.getROIPolydata(self.inputFixedLandmarksSelector.currentNode())
        movingROIPolydata = self.logic.getROIPolydata(self.inputMovingLandmarksSelector.currentNode())
        meanDistanceType = self.meanDistanceType
        landmarkTransformType = self.LandmarkTransformType
        numberOfLandmarks = self.numberOfLandmarksValueChanged
        maxDistance = self.maxDistanceValueChanged
        numberOfIterations = self.numberOfIterationsValueChanged
        matchCentroids = self.matchCentroidsLinearActive
        checkMeanDistance = self.checkMeanDistanceActive
        self.logic.runICP(fixedROIPolydata, movingROIPolydata, outputTrans,
                          meanDistanceType, landmarkTransformType,
                          numberOfLandmarks, maxDistance, numberOfIterations,
                          matchCentroids, checkMeanDistance)

    def onUndoButton(self):
        print("---------undo-------------")
        movingModel = self.inputMovingModelSelector.currentNode()
        self.logic.undoDisplay(movingModel)
        self.undoButton.enabled = False
        self.fixedModel.setChecked(True)
        self.onFixedModelRadio()

    def onApply(self):
        print("---------apply-------------")
        if self.outputModelSelector.currentNode() and self.inputMovingModelSelector.currentNode():
            output = self.outputModelSelector.currentNode()
            input = self.inputMovingModelSelector.currentNode()
            self.logic.applyTransforms(output, input)

    # Call on Fixed Model changes
    def onFixedModelChanged(self):
        print("-------Fixed Model Change--------")
        if self.logic.fixedModel:
            fixedModel = self.logic.fixedModel
            try:
                fixedModel.RemoveObserver(self.logic.decodeJSON(self.logic.fixedModel.GetAttribute("modelModifieTagEvent")))
            except:
                pass
        self.logic.fixedModel = self.inputFixedModelSelector.currentNode()
        self.logic.ModelChanged(self.inputFixedModelSelector, self.inputFixedLandmarksSelector)
        self.inputFixedLandmarksSelector.setCurrentNode(None)
        self.fixedModel.setChecked(True)
        self.onFixedModelRadio()

    # Call on Moving Model changes
    def onMovingModelChanged(self):
        print("---------Moving Model Change----------")
        if self.logic.movingModel:
            movingModel = self.logic.movingModel
            try:
                movingModel.RemoveObserver(self.logic.decodeJSON(self.logic.movingModel.GetAttribute("modelModifieTagEvent")))
            except:
                pass
        self.logic.movingModel = self.inputMovingModelSelector.currentNode()
        self.logic.ModelChanged(self.inputMovingModelSelector, self.inputMovingLandmarksSelector)
        self.inputMovingLandmarksSelector.setCurrentNode(None)
        self.movingModel.setChecked(True)
        self.onMovingModelRadio()

    def onFixedLandmarksChanged(self):
        if self.inputFixedModelSelector.currentNode():
            self.logic.fixedFidList = self.inputFixedLandmarksSelector.currentNode()
            self.logic.selectedFidList = self.inputFixedLandmarksSelector.currentNode()
            self.logic.selectedModel = self.inputFixedModelSelector.currentNode()
            if self.inputFixedLandmarksSelector.currentNode():
                onSurface = self.loadFixedLandmarksOnSurfacCheckBox.isChecked()
                self.logic.connectLandmarks(self.inputFixedModelSelector,
                                      self.inputFixedLandmarksSelector,
                                      onSurface)
            else:
                self.landmarkComboBox.clear()
            self.fixedModel.setChecked(True)
            self.onFixedModelRadio()

    def onMovingLandmarksCganged(self):
        if self.inputMovingModelSelector.currentNode():
            self.logic.movingFidList = self.inputMovingLandmarksSelector.currentNode()
            self.logic.selectedFidList = self.inputMovingLandmarksSelector.currentNode()
            self.logic.selectedModel = self.inputMovingModelSelector.currentNode()
            if self.inputMovingLandmarksSelector.currentNode():
                onSurface = self.loadMovingLandmarksOnSurfacCheckBox.isChecked()
                self.logic.connectLandmarks(self.inputMovingModelSelector,
                                      self.inputMovingLandmarksSelector,
                                      onSurface)
            else:
                self.landmarkComboBox.clear()
            self.movingModel.setChecked(True)
            self.onMovingModelRadio()


    def onFixedModelRadio(self):
        print("Model Radio change")
        self.logic.selectedFidList = self.logic.fixedFidList
        self.logic.selectedModel = self. logic.fixedModel
        self.logic.displayModels(self.inputFixedModelSelector, self.inputMovingModelSelector, self.outputModelSelector)
        self.logic.updateLandmarkComboBox(self.inputFixedLandmarksSelector.currentNode())
        self.UpdateInterface()

    def onMovingModelRadio(self):
        print("Model Radio change")
        self.logic.selectedFidList = self.logic.movingFidList
        self.logic.selectedModel = self. logic.movingModel
        self.logic.displayModels(self.inputMovingModelSelector, self.inputFixedModelSelector, self.outputModelSelector)
        self.logic.updateLandmarkComboBox(self.inputMovingLandmarksSelector.currentNode())
        self.UpdateInterface()

    # When the Button is activated (enable the adding of landmarks in the third view)
    def onAddButton(self):
        # Add fiducial on the scene.
        # If no input model selected, the addition of fiducial shouldn't be possible.
        selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
        selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        if self.logic.selectedModel:
            if self.logic.selectedFidList:
                selectionNode.SetActivePlaceNodeID(self.logic.selectedFidList.GetID())
                self.interactionNode.SetCurrentInteractionMode(1)
            else:
                self.logic.warningMessage("Please select a fiducial list")
        else:
            self.logic.warningMessage("Please select a model")

    def onLandmarksScaleChanged(self):
        if not self.logic.selectedFidList:
            self.logic.warningMessage("Please select a fiducial list")
            return
        print("------------Landmark scaled change-----------")
        displayFiducialNode = self.logic.selectedFidList.GetMarkupsDisplayNode()
        disabledModify = displayFiducialNode.StartModify()
        displayFiducialNode.SetGlyphScale(self.landmarksScaleWidget.value)
        displayFiducialNode.SetTextScale(self.landmarksScaleWidget.value)
        displayFiducialNode.EndModify(disabledModify)

    # this function is called when checkbox "on surface" changes of state
    def onSurfaceDeplacementStateChanged(self):
        activeInput = self.logic.selectedModel
        if not activeInput:
            return
        fidList = self.logic.selectedFidList
        if not fidList:
            return
        selectedFidReflID = self.logic.findIDFromLabel(fidList, self.landmarkComboBox.currentText)
        isOnSurface = self.surfaceDeplacementCheckBox.isChecked()
        landmarkDescription = self.logic.decodeJSON(fidList.GetAttribute("landmarkDescription"))
        if isOnSurface:
            hardenModel = slicer.app.mrmlScene().GetNodeByID(fidList.GetAttribute("hardenModelID"))
            landmarkDescription[selectedFidReflID]["projection"]["isProjected"] = True
            landmarkDescription[selectedFidReflID]["projection"]["closestPointIndex"] =\
                self.logic.projectOnSurface(hardenModel, fidList, selectedFidReflID)
        else:
            landmarkDescription[selectedFidReflID]["projection"]["isProjected"] = False
            landmarkDescription[selectedFidReflID]["projection"]["closestPointIndex"] = None
            landmarkDescription[selectedFidReflID]["ROIradius"] = 0
        fidList.SetAttribute("landmarkDescription",self.logic.encodeJSON(landmarkDescription))

    def onLandmarkComboBoxChanged(self):
        print("-------- ComboBox change --------")
        self.UpdateInterface()

    def onRadiusValueChanged(self):
        print("--------- ROI radius modification ----------")
        fidList = self.logic.selectedFidList
        if not fidList:
            return
        selectedFidReflID = self.logic.findIDFromLabel(fidList, self.landmarkComboBox.currentText)
        if selectedFidReflID:
            landmarkDescription = self.logic.decodeJSON(fidList.GetAttribute("landmarkDescription"))
            activeLandmarkState = landmarkDescription[selectedFidReflID]
            activeLandmarkState["ROIradius"] = self.radiusDefinitionWidget.value
            if not activeLandmarkState["projection"]["isProjected"]:
                self.surfaceDeplacementCheckBox.setChecked(True)
                hardenModel = slicer.app.mrmlScene().GetNodeByID(fidList.GetAttribute("hardenModelID"))
                landmarkDescription[selectedFidReflID]["projection"]["isProjected"] = True
                landmarkDescription[selectedFidReflID]["projection"]["closestPointIndex"] =\
                    self.logic.projectOnSurface(hardenModel, fidList, selectedFidReflID)
            fidList.SetAttribute("landmarkDescription",self.logic.encodeJSON(landmarkDescription))
            self.logic.findROI(fidList)

    def onCleanButton(self):
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(" /!\ WARNING /!\ ")
        messageBox.setIcon(messageBox.Warning)
        messageBox.setText("Your model is about to be modified")
        messageBox.setInformativeText("Do you want to continue?")
        messageBox.setStandardButtons(messageBox.No | messageBox.Yes)
        choice = messageBox.exec_()
        if choice == messageBox.Yes:
            selectedLandmark = self.landmarkComboBox.currentText
            self.logic.cleanMesh(selectedLandmark)
            self.onRadiusValueChanged()
        else:
            messageBox.setText(" Region not modified")
            messageBox.setStandardButtons(messageBox.Ok)
            messageBox.setInformativeText("")
            messageBox.exec_()

    def onOutputModelChanged(self):
        if self.outputModelSelector.currentNode():
            self.applyButton.enabled = True
        else:
            self.applyButton.enabled = False
        if self.fixedModel.isChecked():
            self.onFixedModelRadio()
        if self.movingModel.isChecked():
            self.onMovingModelRadio()

    # Surface registration parameters
    def numberOfIterationsValueChanged(self, newValue):
        self.numberOfIterationsValueChanged = int(newValue)

    def maxDistanceValueChanged(self, newValue1):
        self.maxDistanceValueChanged = newValue1

    def numberOfLandmarksValueChanged(self, newValue2):
        self.numberOfLandmarksValueChanged = int(newValue2)

    def onLandmarkTrandformType(self, landmarkTransformType):
        """Pick which landmark transform"""
        self.LandmarkTransformType = landmarkTransformType

    def onMeanDistanceType(self, meanDistanceType):
        """Pick which distance mode"""
        self.meanDistanceType = meanDistanceType

    def onMatchCentroidsLinearActive(self, matchCentroidsLinearActive):
        """initialize the transform by translating the input surface so
        that its centroid coincides the centroid of the target surface."""
        self.matchCentroidsLinearActive = matchCentroidsLinearActive

    def onCheckMeanDistanceActive(self, checkMeanDistanceActive):
        """ force checking distance between every two iterations (slower but more accurate)"""
        self.checkMeanDistanceActive = checkMeanDistanceActive

class SurfaceRegistrationLogic():

    def __init__(self, interface):

        self.selectedModel = None
        self.fixedModel = None
        self.movingModel = None
        self.selectedFidList = None
        self.fixedFidList = None
        self.movingFidList = None
        self.interface = interface

    def get(self, objectName):
        return self.findWidget(self.interface.widget, objectName)

    def findWidget(self, widget, objectName):
        if widget.objectName == objectName:
            return widget
        else:
            for w in widget.children():
                resulting_widget = self.findWidget(w, objectName)
                if resulting_widget:
                    return resulting_widget
            return None

    def UpdateThreeDView(self, landmarkLabel):
        # Update the 3D view on Slicer
        if not self.selectedFidList:
            return
        if not self.selectedModel:
            return
        active = self.selectedFidList
        #deactivate all landmarks
        list = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
        end = list.GetNumberOfItems()
        selectedFidReflID = self.findIDFromLabel(active,landmarkLabel)
        for i in range(0,end):
            fidList = list.GetItemAsObject(i)
            landmarkDescription = self.decodeJSON(fidList.GetAttribute("landmarkDescription"))
            for key in landmarkDescription.keys():
                markupsIndex = fidList.GetNthControlPointIndexByID(key)
                if key != selectedFidReflID:
                    fidList.SetNthMarkupLocked(markupsIndex, True)
                else:
                    fidList.SetNthMarkupLocked(markupsIndex, False)
        displayNode = self.selectedModel.GetModelDisplayNode()
        displayNode.SetScalarVisibility(False)
        if selectedFidReflID != False:
            displayNode.SetScalarVisibility(True)

    def getROIPolydata(self, inputFidList):
        hardenInputModel = slicer.app.mrmlScene().GetNodeByID(inputFidList.GetAttribute("hardenModelID"))
        hardenInputPolydata = hardenInputModel.GetPolyData()
        markupID = inputFidList.GetNthMarkupID(0)
        landmarkDescription = self.decodeJSON(inputFidList.GetAttribute("landmarkDescription"))
        activeLandmarkState = landmarkDescription[markupID]
        inputROIPointListID = self.findROI(inputFidList)
        nbOfPoints = inputROIPointListID.GetNumberOfIds()
        ids = vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        for i in range(0, nbOfPoints):
            ids.InsertNextValue(inputROIPointListID.GetId(i))
        selectionNode = vtk.vtkSelectionNode()
        selectionNode.SetFieldType(vtk.vtkSelectionNode.POINT)
        selectionNode.SetContentType(vtk.vtkSelectionNode.INDICES)
        selectionNode.SetSelectionList(ids)
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(), 1)
        selection = vtk.vtkSelection()
        selection.AddNode(selectionNode)
        extractSelection = vtk.vtkExtractSelection()
        extractSelection.SetInputData(0, hardenInputPolydata)
        extractSelection.SetInputData(1, selection)
        extractSelection.Update()
        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(extractSelection.GetOutput())
        geometryFilter.Update()
        inputROIPolydata = geometryFilter.GetOutput()
        return inputROIPolydata

    def runFiducialRegistration(self, fixedLandmarks, movingLandmarks,
                                saveTransform, tranformType):
        parameters = {}
        parameters["fixedLandmarks"] = fixedLandmarks
        parameters["movingLandmarks"] = movingLandmarks
        parameters["saveTransform"] = saveTransform
        parameters["transformType"] = tranformType
        fiducialRegistration = slicer.modules.fiducialregistration
        slicer.cli.run(fiducialRegistration, None, parameters, wait_for_completion=True)

    def runICP(self, fixed, moving, outputTrans, meanDistanceType,
               landmarkTransformType, numberOfLandmarks, maxDistance,
               numberOfIterations, matchCentroids, checkMeanDistance):
        """Run the actual algorithm"""
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(moving)
        icp.SetTarget(fixed)
        if landmarkTransformType == "RigidBody":
            icp.GetLandmarkTransform().SetModeToRigidBody()
        elif landmarkTransformType == "Similarity":
            icp.GetLandmarkTransform().SetModeToSimilarity()
        elif landmarkTransformType == "Affine":
            icp.GetLandmarkTransform().SetModeToAffine()
        if meanDistanceType == "Root Mean Square":
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
        return

    def createIntermediateHardenModel(self, model):
        hardenModel = slicer.mrmlScene.GetNodesByName("SurfaceRegistration_" + model.GetName() + "_hardenCopy_" + str(
            slicer.app.applicationPid())).GetItemAsObject(0)
        if hardenModel is None:
            hardenModel = slicer.vtkMRMLModelNode()
        hardenPolyData = vtk.vtkPolyData()
        hardenPolyData.DeepCopy(model.GetPolyData())
        hardenModel.SetAndObservePolyData(hardenPolyData)
        hardenModel.SetName(
            "SurfaceRegistration_" + model.GetName() + "_hardenCopy_" + str(slicer.app.applicationPid()))
        if model.GetParentTransformNode():
            hardenModel.SetAndObserveTransformNodeID(model.GetParentTransformNode().GetID())
        hardenModel.HideFromEditorsOn()
        slicer.mrmlScene.AddNode(hardenModel)
        logic = slicer.vtkSlicerTransformLogic()
        logic.hardenTransform(hardenModel)
        return hardenModel

    def displayResult(self, movingModel, outputTrans):
        parentTrans = movingModel.GetParentTransformNode()
        nextParentTrans = parentTrans
        while nextParentTrans:
            nextParentTrans = parentTrans.GetParentTransformNode()
            if nextParentTrans:
                parentTrans = nextParentTrans
        if parentTrans:
            parentTrans.SetAndObserveTransformNodeID(outputTrans.GetID())
        else:
            movingModel.SetAndObserveTransformNodeID(outputTrans.GetID())
        self.movingModel.SetAttribute("lastTransformID",outputTrans.GetID())
        if self.movingFidList:
            self.movingFidList.SetAttribute("lastTransformID",outputTrans.GetID())
            self.movingFidList.GetDisplayNode().SetSelectedColor(0, 0, 1)

    def undoDisplay(self, movingModel):
        if movingModel:
            lastTrans = slicer.app.mrmlScene().GetNodeByID(movingModel.GetAttribute("lastTransformID"))
            parentTrans = movingModel.GetParentTransformNode()
            if not parentTrans:
                print("There is no transform to undo.")
                return
            if lastTrans == parentTrans:
                movingModel.SetAndObserveTransformNodeID(None)
            else:
                if parentTrans:
                    while (parentTrans.GetParentTransformNode()) and \
                            (parentTrans.GetParentTransformNode() != lastTrans):
                        parentTrans = parentTrans.GetParentTransformNode()
                if parentTrans.GetParentTransformNode() == lastTrans:
                    parentTrans.SetAndObserveTransformNodeID(None)
            if self.movingFidList:
                self.movingFidList.GetDisplayNode().SetSelectedColor(1, 0.5, 0.5)
            self.movingModel.SetAttribute("lastTransformID",parentTrans.GetID())
            if self.movingFidList:
                self.movingFidList.SetAttribute("lastTransformID",parentTrans.GetID())

    def applyTransforms(self, outputModel, inputModel):
        inputHardenModel = slicer.app.mrmlScene().GetNodeByID(inputModel.GetAttribute("hardenModelID"))
        hardenPolyData = vtk.vtkPolyData()
        hardenPolyData.DeepCopy(inputHardenModel.GetPolyData())
        outputModel.SetAndObservePolyData(hardenPolyData)
        outputModel.SetAndObserveTransformNodeID(None)
        displayNode = outputModel.GetDisplayNode()
        if displayNode is None:
            modelDisplay = slicer.vtkMRMLModelDisplayNode()
            slicer.mrmlScene.AddNode(modelDisplay)
            outputModel.SetAndObserveDisplayNodeID(modelDisplay.GetID())
            modelDisplay.VisibilityOn()
            modelDisplay.SetColor(1, 0, 0)
        else:
            displayNode.SetColor(1, 0, 0)
            displayNode.VisibilityOn()

    def onModelModified(self, obj, event):
        #recompute the harden model
        hardenModel = self.createIntermediateHardenModel(obj)
        obj.SetAttribute("hardenModelID",hardenModel.GetID())
        # for each fiducial list
        list = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
        end = list.GetNumberOfItems()
        for i in range(0,end):
            # If landmarks are projected on the modified model
            fidList = list.GetItemAsObject(i)
            if fidList.GetAttribute("connectedModelID"):
                if fidList.GetAttribute("connectedModelID") == obj.GetID():
                    #replace the harden model with the new one
                    fidList.SetAttribute("hardenModelID",hardenModel.GetID())
                    #reproject the fiducials on the new model
                    landmarkDescription = self.decodeJSON(fidList.GetAttribute("landmarkDescription"))
                    for n in range(fidList.GetNumberOfMarkups()):
                        markupID = fidList.GetNthMarkupID(n)
                        if landmarkDescription[markupID]["projection"]["isProjected"] == True:
                            hardenModel = slicer.app.mrmlScene().GetNodeByID(fidList.GetAttribute("hardenModelID"))
                            markupsIndex = fidList.GetNthControlPointIndexByID(markupID)
                            self.replaceLandmark(hardenModel.GetPolyData(), fidList, markupsIndex,
                                                 landmarkDescription[markupID]["projection"]["closestPointIndex"])
                        self.updateMidPoint(fidList, markupID)
                        fidList.SetAttribute("landmarkDescription",self.encodeJSON(landmarkDescription))

    def ModelChanged(self, inputModelSelector, inputLandmarksSelector):
        inputModel = inputModelSelector.currentNode()
        # if a Model Node is present
        if inputModel:
            self.selectedModel = inputModel
            hardenModel = self.createIntermediateHardenModel(inputModel)
            inputModel.SetAttribute("hardenModelID",hardenModel.GetID())
            modelModifieTagEvent = inputModel.AddObserver(inputModel.TransformModifiedEvent, self.onModelModified)
            inputModel.SetAttribute("modelModifieTagEvent",self.encodeJSON({"modelModifieTagEvent":modelModifieTagEvent}))
            inputLandmarksSelector.setEnabled(True)
        # if no model is selected
        else:
            # Update the fiducial list selector
            inputLandmarksSelector.setCurrentNode(None)
            inputLandmarksSelector.setEnabled(False)

    def isUnderTransform(self, markups):
        if markups.GetParentTransformNode():
            messageBox = ctk.ctkMessageBox()
            messageBox.setWindowTitle(" /!\ WARNING /!\ ")
            messageBox.setIcon(messageBox.Warning)
            messageBox.setText("Your Markup Fiducial Node is currently modified by a transform,"
                               "if you choose to continue the program will apply the transform"
                               "before doing anything else!")
            messageBox.setInformativeText("Do you want to continue?")
            messageBox.setStandardButtons(messageBox.No | messageBox.Yes)
            choice = messageBox.exec_()
            if choice == messageBox.Yes:
                logic = slicer.vtkSlicerTransformLogic()
                logic.hardenTransform(markups)
                return False
            else:
                messageBox.setText(" Node not modified")
                messageBox.setStandardButtons(messageBox.Ok)
                messageBox.setInformativeText("")
                messageBox.exec_()
                return True
        else:
            return False

    def connectedModelChangement(self):
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(" /!\ WARNING /!\ ")
        messageBox.setIcon(messageBox.Warning)
        messageBox.setText("The Markup Fiducial Node selected is curently projected on an"
                           "other model, if you chose to continue the fiducials will be  "
                           "reprojected, and this could impact the functioning of other modules")
        messageBox.setInformativeText("Do you want to continue?")
        messageBox.setStandardButtons(messageBox.No | messageBox.Yes)
        choice = messageBox.exec_()
        if choice == messageBox.Yes:
            return True
        else:
            messageBox.setText(" Node not modified")
            messageBox.setStandardButtons(messageBox.Ok)
            messageBox.setInformativeText("")
            messageBox.exec_()
            return False

    def createNewDataStructure(self,landmarks, model, onSurface):
        landmarks.SetAttribute("connectedModelID",model.GetID())
        landmarks.SetAttribute("hardenModelID",model.GetAttribute("hardenModelID"))
        landmarkDescription = dict()
        for n in range(landmarks.GetNumberOfMarkups()):
            markupID = landmarks.GetNthMarkupID(n)
            landmarkDescription[markupID] = dict()
            landmarkLabel = landmarks.GetNthMarkupLabel(n)
            landmarkDescription[markupID]["landmarkLabel"] = landmarkLabel
            landmarkDescription[markupID]["ROIradius"] = 0
            landmarkDescription[markupID]["projection"] = dict()
            if onSurface:
                landmarkDescription[markupID]["projection"]["isProjected"] = True
                hardenModel = slicer.app.mrmlScene().GetNodeByID(landmarks.GetAttribute("hardenModelID"))
                landmarkDescription[markupID]["projection"]["closestPointIndex"] = \
                    self.projectOnSurface(hardenModel, landmarks, markupID)
            else:
                landmarkDescription[markupID]["projection"]["isProjected"] = False
                landmarkDescription[markupID]["projection"]["closestPointIndex"] = None
            landmarkDescription[markupID]["midPoint"] = dict()
            landmarkDescription[markupID]["midPoint"]["definedByThisMarkup"] = list()
            landmarkDescription[markupID]["midPoint"]["isMidPoint"] = False
            landmarkDescription[markupID]["midPoint"]["Point1"] = None
            landmarkDescription[markupID]["midPoint"]["Point2"] = None
        landmarks.SetAttribute("landmarkDescription",self.encodeJSON(landmarkDescription))
        planeDescription = dict()
        landmarks.SetAttribute("planeDescription",self.encodeJSON(planeDescription))
        landmarks.SetAttribute("isClean",self.encodeJSON({"isClean":False}))
        landmarks.SetAttribute("lastTransformID",None)
        landmarks.SetAttribute("arrayName",model.GetName() + "_ROI")

    def changementOfConnectedModel(self,landmarks, model, onSurface):
        landmarks.SetAttribute("connectedModelID",model.GetID())
        landmarks.SetAttribute("hardenModelID",model.GetAttribute("hardenModelID"))
        landmarkDescription = self.decodeJSON(landmarks.GetAttribute("landmarkDescription"))
        for n in range(landmarks.GetNumberOfMarkups()):
            markupID = landmarks.GetNthMarkupID(n)
            if onSurface:
                if landmarkDescription[markupID]["projection"]["isProjected"] == True:
                    hardenModel = slicer.app.mrmlScene().GetNodeByID(landmarks.GetAttribute("hardenModelID"))
                    landmarkDescription[markupID]["projection"]["closestPointIndex"] = \
                        self.projectOnSurface(hardenModel, landmarks, markupID)
            else:
                landmarkDescription[markupID]["projection"]["isProjected"] = False
                landmarkDescription[markupID]["projection"]["closestPointIndex"] = None
            landmarks.SetAttribute("landmarkDescription",self.encodeJSON(landmarkDescription))
        landmarks.SetAttribute("isClean",self.encodeJSON({"isClean":False}))

    def connectLandmarks(self, modelSelector, landmarkSelector, onSurface):
        model = modelSelector.currentNode()
        landmarks = landmarkSelector.currentNode()
        self.selectedFidList = landmarks
        self.selectedModel = model
        if not (model and landmarks):
            return

        if self.isUnderTransform(landmarks):
            landmarkSelector.setCurrentNode(None)
            return
        connectedModelID = landmarks.GetAttribute("connectedModelID")
        try:
            tag = self.decodeJSON(landmarks.GetAttribute("PointAddedEventTag"))
            landmarks.RemoveObserver(tag["PointAddedEventTag"])
            print("adding observers removed!")
        except:
            pass
        try:
            tag = self.decodeJSON(landmarks.GetAttribute("PointModifiedEventTag"))
            landmarks.RemoveObserver(tag["PointModifiedEventTag"])
            print("moving observers removed!")
        except:
            pass
        try:
            tag = self.decodeJSON(landmarks.GetAttribute("PointRemovedEventTag"))
            landmarks.RemoveObserver(tag["PointRemovedEventTag"])
            print("moving observers removed!")
        except:
            pass
        if connectedModelID:
            if connectedModelID != model.GetID():
                if self.connectedModelChangement():
                    self.changementOfConnectedModel(landmarks, model, onSurface)
                else:
                    landmarkSelector.setCurrentNode(None)
                    return
            else:
                landmarks.SetAttribute("hardenModelID",model.GetAttribute("hardenModelID"))
        # creation of the data structure
        else:
            self.createNewDataStructure(landmarks, model, onSurface)
        #update of the landmark Combo Box
        self.updateLandmarkComboBox(landmarks)
        #adding of listeners
        PointAddedEventTag = landmarks.AddObserver(landmarks.PointAddedEvent, self.onPointAddedEvent)
        landmarks.SetAttribute("PointAddedEventTag",self.encodeJSON({"PointAddedEventTag":PointAddedEventTag}))
        PointModifiedEventTag = landmarks.AddObserver(landmarks.PointModifiedEvent, self.onPointModifiedEvent)
        landmarks.SetAttribute("PointModifiedEventTag",self.encodeJSON({"PointModifiedEventTag":PointModifiedEventTag}))
        PointRemovedEventTag = landmarks.AddObserver(landmarks.PointRemovedEvent, self.onPointRemovedEvent)
        landmarks.SetAttribute("PointRemovedEventTag",self.encodeJSON({"PointRemovedEventTag":PointRemovedEventTag}))

    # Called when a landmark is added on a model
    def onPointAddedEvent(self, obj, event):
        print("------markup adding-------")
        landmarkDescription = self.decodeJSON(obj.GetAttribute("landmarkDescription"))
        numOfMarkups = obj.GetNumberOfMarkups()
        markupID = obj.GetNthMarkupID(numOfMarkups - 1)  # because everytime a new node is added, its index is the last one on the list
        landmarkDescription[markupID] = dict()
        landmarkLabel = obj.GetNthMarkupLabel(numOfMarkups - 1)
        landmarkDescription[markupID]["landmarkLabel"] = landmarkLabel
        landmarkDescription[markupID]["ROIradius"] = 0
        landmarkDescription[markupID]["projection"] = dict()
        landmarkDescription[markupID]["projection"]["isProjected"] = True
        # The landmark will be projected by onPointModifiedEvent
        landmarkDescription[markupID]["midPoint"] = dict()
        landmarkDescription[markupID]["midPoint"]["definedByThisMarkup"] = list()
        landmarkDescription[markupID]["midPoint"]["isMidPoint"] = False
        landmarkDescription[markupID]["midPoint"]["Point1"] = None
        landmarkDescription[markupID]["midPoint"]["Point2"] = None
        obj.SetAttribute("landmarkDescription",self.encodeJSON(landmarkDescription))
        self.interface.landmarkComboBox.addItem(landmarkLabel)
        self.interface.landmarkComboBox.setCurrentIndex(self.interface.landmarkComboBox.count - 1)
        self.interface.UpdateInterface()
        qt.QTimer.singleShot(0, lambda : self.onPointModifiedEvent(obj,None))

    def calculateMidPointCoord(self, fidList, landmark1ID, landmark2ID):
        """Set the midpoint when you know the the mrml nodes"""
        landmark1Index = fidList.GetNthControlPointIndexByID(landmark1ID)
        landmark2Index = fidList.GetNthControlPointIndexByID(landmark2ID)
        coord1 = [-1, -1, -1]
        coord2 = [-1, -1, -1]
        fidList.GetNthFiducialPosition(landmark1Index, coord1)
        fidList.GetNthFiducialPosition(landmark2Index, coord2)
        midCoord = [-1, -1, -1]
        midCoord[0] = (coord1[0] + coord2[0])/2
        midCoord[1] = (coord1[1] + coord2[1])/2
        midCoord[2] = (coord1[2] + coord2[2])/2
        return midCoord

    def updateMidPoint(self, fidList, landmarkID):
        landmarkDescription = self.decodeJSON(fidList.GetAttribute("landmarkDescription"))
        for midPointID in landmarkDescription[landmarkID]["midPoint"]["definedByThisMarkup"]:
            if landmarkDescription[midPointID]["midPoint"]["isMidPoint"]:
                landmark1ID = landmarkDescription[midPointID]["midPoint"]["Point1"]
                landmark2ID = landmarkDescription[midPointID]["midPoint"]["Point2"]
                coord = self.calculateMidPointCoord(fidList, landmark1ID, landmark2ID)
                index = fidList.GetNthControlPointIndexByID(midPointID)
                fidList.SetNthControlPointPositionFromArray(index, coord, fidList.PositionPreview)
                if landmarkDescription[midPointID]["projection"]["isProjected"]:
                    hardenModel = slicer.app.mrmlScene().GetNodeByID(fidList.GetAttribute("hardenModelID"))
                    landmarkDescription[midPointID]["projection"]["closestPointIndex"] = \
                        self.projectOnSurface(hardenModel, fidList, landmarkID)
                    fidList.SetAttribute("landmarkDescription",self.encodeJSON(landmarkDescription))
                self.updateMidPoint(fidList, midPointID)

    # Called when a landmarks is moved
    def onPointModifiedEvent(self, obj, event):
        print("----onPointModifiedEvent SR-----")
        landmarkDescription = self.decodeJSON(obj.GetAttribute("landmarkDescription"))
        if not landmarkDescription:
            return
        selectedLandmarkID = self.findIDFromLabel(obj, self.interface.landmarkComboBox.currentText)
        # remove observer to make sure, the callback function won't work..
        tag = self.decodeJSON(obj.GetAttribute("PointModifiedEventTag"))
        obj.RemoveObserver(tag["PointModifiedEventTag"])
        if selectedLandmarkID:
            activeLandmarkState = landmarkDescription[selectedLandmarkID]
            if activeLandmarkState["projection"]["isProjected"]:
                hardenModel = slicer.app.mrmlScene().GetNodeByID(obj.GetAttribute("hardenModelID"))
                activeLandmarkState["projection"]["closestPointIndex"] = \
                    self.projectOnSurface(hardenModel, obj, selectedLandmarkID)
                obj.SetAttribute("landmarkDescription",self.encodeJSON(landmarkDescription))
            self.updateMidPoint(obj,selectedLandmarkID)
            self.findROI(obj)
        time.sleep(0.08)
        # Add the observer again
        PointModifiedEventTag = obj.AddObserver(obj.PointModifiedEvent, self.onPointModifiedEvent)
        obj.SetAttribute("PointModifiedEventTag",self.encodeJSON({"PointModifiedEventTag":PointModifiedEventTag}))

    def onPointRemovedEvent(self, obj, event):
        print("------markup deleting-------")
        landmarkDescription = self.decodeJSON(obj.GetAttribute("landmarkDescription"))
        IDs = []
        for ID, value in landmarkDescription.items():
            isFound = False
            for n in range(obj.GetNumberOfMarkups()):
                markupID = obj.GetNthMarkupID(n)
                if ID == markupID:
                    isFound = True
            if not isFound:
                print(ID)
                IDs.append(ID)
        for ID in IDs:
            landmarkDescription.pop(ID,None)
        obj.SetAttribute("landmarkDescription",self.encodeJSON(landmarkDescription))
        self.updateLandmarkComboBox(obj)

    def updateLandmarkComboBox(self, fidList):
        if not fidList:
            return
        landmarkDescription = self.decodeJSON(fidList.GetAttribute("landmarkDescription"))
        self.interface.landmarkComboBox.blockSignals(True)
        self.interface.landmarkComboBox.clear()
        numOfFid = fidList.GetNumberOfMarkups()
        if numOfFid > 0:
            for i in range(0, numOfFid):
                ID = fidList.GetNthMarkupID(i)
                if not landmarkDescription[ID]["midPoint"]["isMidPoint"]:
                    landmarkLabel = fidList.GetNthMarkupLabel(i)
                    self.interface.landmarkComboBox.addItem(landmarkLabel)
        self.interface.landmarkComboBox.setCurrentIndex(self.interface.landmarkComboBox.count - 1)
        self.interface.landmarkComboBox.blockSignals(False)

    def findIDFromLabel(self, fidList, landmarkLabel):
        # find the ID of the markupsNode from the label of a landmark!
        landmarkDescription = self.decodeJSON(fidList.GetAttribute("landmarkDescription"))
        for ID, value in landmarkDescription.items():
            if value["landmarkLabel"] == landmarkLabel:
                return ID
        return None

    def getClosestPointIndex(self, fidNode, inputPolyData, landmarkID):
        landmarkCoord = numpy.zeros(3)
        landmarkCoord[1] = 42
        fidNode.GetNthFiducialPosition(landmarkID, landmarkCoord)
        pointLocator = vtk.vtkPointLocator()
        pointLocator.SetDataSet(inputPolyData)
        pointLocator.AutomaticOn()
        pointLocator.BuildLocator()
        indexClosestPoint = pointLocator.FindClosestPoint(landmarkCoord)
        return indexClosestPoint

    def replaceLandmark(self, inputModelPolyData, fidNode, landmarkID, indexClosestPoint):
        landmarkCoord = [-1, -1, -1]
        fidNode.GetNthFiducialPosition(landmarkID, landmarkCoord)
        inputModelPolyData.GetPoints().GetPoint(indexClosestPoint, landmarkCoord)
        fidNode.SetNthControlPointPositionFromArray(landmarkID, landmarkCoord, fidNode.PositionPreview)

    def projectOnSurface(self, modelOnProject, fidNode, selectedFidReflID):
        if selectedFidReflID:
            markupsIndex = fidNode.GetNthControlPointIndexByID(selectedFidReflID)
            indexClosestPoint = self.getClosestPointIndex(fidNode, modelOnProject.GetPolyData(), markupsIndex)
            self.replaceLandmark(modelOnProject.GetPolyData(), fidNode, markupsIndex, indexClosestPoint)
            return indexClosestPoint

    def hideAllModels(self):
        numNodes = slicer.mrmlScene.GetNumberOfNodesByClass("vtkMRMLModelNode")
        for i in range(3, numNodes):
            elements = slicer.mrmlScene.GetNthNodeByClass(i, "vtkMRMLModelNode")
            disp = elements.GetDisplayNode()
            if disp:
                disp.VisibilityOff()

    def hideAllFidLists(self):
        numNodes = slicer.mrmlScene.GetNumberOfNodesByClass("vtkMRMLMarkupsFiducialNode")
        for i in range(0, numNodes):
            elements = slicer.mrmlScene.GetNthNodeByClass(i, "vtkMRMLMarkupsFiducialNode")
            disp = elements.GetDisplayNode()
            if disp:
                disp.VisibilityOff()

    def displayModels(self, selectedModelSelector, unselectedModelSelector, outputModelSelector):
        self.hideAllModels()
        self.hideAllFidLists()
        if unselectedModelSelector.currentNode():
            disp = unselectedModelSelector.currentNode().GetDisplayNode()
            if disp:
                disp.SetOpacity(0.5)
                disp.VisibilityOn()
        if selectedModelSelector.currentNode():
            disp = selectedModelSelector.currentNode().GetDisplayNode()
            if disp:
                disp.SetOpacity(1)
                disp.VisibilityOn()
        if outputModelSelector.currentNode():
            disp = outputModelSelector.currentNode().GetDisplayNode()
            if disp:
                disp.VisibilityOn()
        if self.fixedFidList:
            disp = self.fixedFidList.GetDisplayNode()
            if disp:
                disp.VisibilityOn()
        if self.movingFidList:
            disp = self.movingFidList.GetDisplayNode()
            if disp:
                disp.VisibilityOn()


    def defineNeighbor(self, connectedVerticesList, inputModelNodePolyData, indexClosestPoint, distance):
        self.GetConnectedVertices(connectedVerticesList, inputModelNodePolyData, indexClosestPoint)
        if distance > 1:
            for dist in range(1, int(distance)):
                for i in range(0, connectedVerticesList.GetNumberOfIds()):
                    self.GetConnectedVertices(connectedVerticesList, inputModelNodePolyData,
                                              connectedVerticesList.GetId(i))
        return connectedVerticesList

    def GetConnectedVertices(self, connectedVerticesIDList, polyData, pointID):
        # Return IDs of all the vertices that compose the first neighbor.
        cellList = vtk.vtkIdList()
        connectedVerticesIDList.InsertUniqueId(pointID)
        # Get cells that vertex 'pointID' belongs to
        polyData.GetPointCells(pointID, cellList)
        numberOfIds = cellList.GetNumberOfIds()
        for i in range(0, numberOfIds):
            # Get points which compose all cells
            pointIdList = vtk.vtkIdList()
            polyData.GetCellPoints(cellList.GetId(i), pointIdList)
            for j in range(0, pointIdList.GetNumberOfIds()):
                connectedVerticesIDList.InsertUniqueId(pointIdList.GetId(j))
        return connectedVerticesIDList

    def addArrayFromIdList(self, connectedIdList, inputModelNode, arrayName):
        if not inputModelNode:
            return
        inputModelNodePolydata = inputModelNode.GetPolyData()
        pointData = inputModelNodePolydata.GetPointData()
        numberofIds = connectedIdList.GetNumberOfIds()
        hasArrayInt = pointData.HasArray(arrayName)
        if hasArrayInt == 1:  # ROI Array found
            pointData.RemoveArray(arrayName)
        arrayToAdd = vtk.vtkDoubleArray()
        arrayToAdd.SetName(arrayName)
        for i in range(0, inputModelNodePolydata.GetNumberOfPoints()):
            arrayToAdd.InsertNextValue(0.0)
        for i in range(0, numberofIds):
            arrayToAdd.SetValue(connectedIdList.GetId(i), 1.0)
        lut = vtk.vtkLookupTable()
        tableSize = 2
        lut.SetNumberOfTableValues(tableSize)
        lut.Build()
        displayNode = inputModelNode.GetDisplayNode()
        if displayNode:
            rgb = displayNode.GetColor()
            lut.SetTableValue(0, rgb[0], rgb[1], rgb[2], 1)
        else:
            lut.SetTableValue(0, 0.0, 0.0, 1.0, 1)
        lut.SetTableValue(1, 1.0, 0.0, 0.0, 1)
        arrayToAdd.SetLookupTable(lut)
        pointData.AddArray(arrayToAdd)
        inputModelNodePolydata.Modified()
        return True

    def displayROI(self, inputModelNode, scalarName):
        PolyData = inputModelNode.GetPolyData()
        PolyData.Modified()
        displayNode = inputModelNode.GetModelDisplayNode()
        displayNode.SetScalarVisibility(False)
        disabledModify = displayNode.StartModify()
        displayNode.SetActiveScalarName(scalarName)
        displayNode.SetScalarVisibility(True)
        displayNode.EndModify(disabledModify)

    def getCellPoints(self, polyData, cellIdx):
        points = vtk.vtkIdList()
        polyData.GetCellPoints(cellIdx, points)
        for i in range(points.GetNumberOfIds()):
            yield points.GetId(i)

    def getPointCells(self, polyData, pointIdx):
        cells = vtk.vtkIdList()
        polyData.GetPointCells(pointIdx, cells)
        for i in range(cells.GetNumberOfIds()):
            yield cells.GetId(i)

    def findROI(self, fidList):
        hardenModel = slicer.app.mrmlScene().GetNodeByID(fidList.GetAttribute("hardenModelID"))
        connectedModel = slicer.app.mrmlScene().GetNodeByID(fidList.GetAttribute("connectedModelID"))
        landmarkDescription = self.decodeJSON(fidList.GetAttribute("landmarkDescription"))
        arrayName = fidList.GetAttribute("arrayName")

        # Each ROI radius is a "weight" in the graph of points. Do a breadth-first
        # traversal, subtracting one from the weight at each layer. Continue until
        # weight is 0.

        # Starting weights (the ROI radius at each fiducial)
        weights = defaultdict(set)
        for key, state in landmarkDescription.items():
            weight = int(state['ROIradius'])
            idx = state['projection']['closestPointIndex']
            weights[weight].add(idx)

        poly = hardenModel.GetPolyData()

        # To keep from backtracking
        allPoints = set()
        allCells = set()

        # Breadth-first traversal of points. Note we process in "rings" around
        # each fiducial to be sure we don't backtrack or process any cells/points
        # multiple times
        for weight in range(max(weights), 0, -1):
            points = weights.pop(weight)

            # Find the ring of cells that neighbor the current set of points
            cellsToAdd = set()
            for point in points:
                cellsToAdd.update(self.getPointCells(poly, point))
            cellsToAdd -= allCells  # Exclude already-seen cells
            allCells.update(cellsToAdd)

            # Find the ring of points that neighbor the current set of cells
            pointsToAdd = set()
            for cell in cellsToAdd:
                pointsToAdd.update(self.getCellPoints(poly, cell))
            pointsToAdd -= allPoints # Exclude already-seen points
            allPoints.update(pointsToAdd)

            # All the points we found should be traversed next with lesser weight.
            # If a markup with smaller ROI exists, it will still be included or
            # overtaken here.
            weights[weight - 1].update(pointsToAdd)

        # Copy that set of all points into a vtkIdList.
        pointIds = vtk.vtkIdList()
        for point in allPoints:
            pointIds.InsertNextId(point)

        self.addArrayFromIdList(pointIds, connectedModel, arrayName)
        self.displayROI(connectedModel, arrayName)
        return pointIds

    def cleanerAndTriangleFilter(self, inputModel):
        cleanerPolydata = vtk.vtkCleanPolyData()
        cleanerPolydata.SetInputData(inputModel.GetPolyData())
        cleanerPolydata.Update()
        triangleFilter = vtk.vtkTriangleFilter()
        triangleFilter.SetInputData(cleanerPolydata.GetOutput())
        triangleFilter.Update()
        inputModel.SetAndObservePolyData(triangleFilter.GetOutput())

    def cleanMesh(self, selectedLandmark):
        activeInput = self.selectedModel
        fidList = self.selectedFidList
        hardenModel = slicer.app.mrmlScene().GetNodeByID(activeInput.GetAttribute("hardenModelID"))
        if activeInput:
            # Clean the mesh with vtkCleanPolyData cleaner and vtkTriangleFilter:
            self.cleanerAndTriangleFilter(activeInput)
            self.cleanerAndTriangleFilter(hardenModel)
            # Define the new ROI:
            selectedLandmarkID = self.findIDFromLabel(fidList, selectedLandmark)
            if selectedLandmarkID:
                landmarkDescription = self.decodeJSON(fidList.GetAttribute("landmarkDescription"))
                landmarkDescription[selectedLandmarkID]["projection"]["closestPointIndex"] =\
                    self.projectOnSurface(hardenModel, fidList, selectedLandmarkID)
                fidList.SetAttribute("landmarkDescription",self.encodeJSON(landmarkDescription))
            fidList.SetAttribute("isClean",self.encodeJSON({"isClean":True}))
            activeInput.SetAttribute("isClean",self.encodeJSON({"isClean":True}))

    def warningMessage(self, message):
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(" /!\ WARNING /!\ ")
        messageBox.setIcon(messageBox.Warning)
        messageBox.setText(message)
        messageBox.setStandardButtons(messageBox.Ok)
        messageBox.exec_()

    def encodeJSON(self, input):
        encodedString = json.dumps(input)
        encodedString = encodedString.replace('\"', '\'')
        return encodedString

    def decodeJSON(self, input):
        if input:
            input = input.replace('\'','\"')
            return json.loads(input)
        return None

class SurfaceRegistrationTest(ScriptedLoadableModuleTest):
    def setUp(self):

        slicer.mrmlScene.Clear(0)

    def downloaddata(self):
        import urllib.request
        downloads = (
            ('http://slicer.kitware.com/midas3/download?items=213632', '01.vtk', slicer.util.loadModel),
            ('http://slicer.kitware.com/midas3/download?items=213633', '02.vtk', slicer.util.loadModel),
            ('http://slicer.kitware.com/midas3/download?items=227775', 'surfaceTransform.h5',
                slicer.util.loadTransform),
            ('http://slicer.kitware.com/midas3/download?items=225957', 'FiducialTransform.h5',
             slicer.util.loadTransform),
            ('http://slicer.kitware.com/midas3/download?items=225961', 'ROItransform.h5',
             slicer.util.loadTransform),
        )
        for url, name, loader in downloads:
            filePath = slicer.app.temporaryPath + '/' + name
            if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
                logging.info('Requesting download %s from %s...\n' % (name, url))
                urllib.request.urlretrieve(url, filePath)
            if loader:
                logging.info('Loading %s...' % (name,))
                loader(filePath)

        layoutManager = slicer.app.layoutManager()
        threeDWidget = layoutManager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        threeDView.resetFocalPoint()

    def runTest(self):

        self.delayDisplay("Clear the scene")
        self.setUp()

        self.delayDisplay("Starting the tests")

        # unitests
        self.delayDisplay(' Test createIntermediateHardenModel Function ')
        self.assertTrue(self.testCreateIntermediateHardenModel())

        self.delayDisplay(' Test getClosestPointIndex Function ')
        self.assertTrue(self.testGetClosestPointIndexFunction())

        self.delayDisplay(' Test replaceLandmark Function ')
        self.assertTrue(self.testReplaceLandmarkFunction())

        self.delayDisplay(' Test DefineNeighbors Function ')
        self.assertTrue(self.testDefineNeighborsFunction())

        self.delayDisplay(' Test addArrayFromIdList Function ')
        self.assertTrue(self.testAddArrayFromIdListFunction())

        # self.delayDisplay(' Test testGetROIPolydata Function ')
        # self.assertTrue(self.testGetROIPolydata())

        self.delayDisplay(' Test runFiducialRegistration Function ')
        self.assertTrue(self.testRunFiducialRegistration())

        self.delayDisplay(' Test ICP Function ')
        self.assertTrue(self.testRunICP())

        # globaltests
        self.setUp()
        self.delayDisplay("Download and load datas")
        self.downloaddata()

        self.assertTrue(self.testLandmarkRegistration())

        slicer.modules.SurfaceRegistrationWidget.undoButton.click()

        self.assertTrue(self.testSurfaceRegistration())

        slicer.modules.SurfaceRegistrationWidget.undoButton.click()

        self.assertTrue(self.testROIRegistration())

        self.delayDisplay('All tests passed!')

    # ---------------------------------------------
    #              uni tests
    # ---------------------------------------------

    def testCreateIntermediateHardenModel(self):
        logic = SurfaceRegistrationLogic(slicer.modules.SurfaceRegistrationWidget)
        sphereModel = self.defineSphere()
        slicer.mrmlScene.AddNode(sphereModel)
        transform = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(transform)
        transform.SetName("test")
        hardenPoint = list()
        #test 1
        matrix = vtk.vtkMatrix4x4()
        matrix.SetElement(0,3,20)
        transform.ApplyTransformMatrix(matrix)
        sphereModel.SetAndObserveTransformNodeID(transform.GetID())
        harden = logic.createIntermediateHardenModel(sphereModel)
        a = harden.GetPolyData().GetPoint(5)
        hardenPoint.append(a)
        #test 2
        matrix = vtk.vtkMatrix4x4()
        matrix.SetElement(0,0,0.77)
        matrix.SetElement(0,2,0.64)
        matrix.SetElement(1,0,-0.32)
        matrix.SetElement(1,1,0.87)
        matrix.SetElement(1,2,0.38)
        matrix.SetElement(2,0,-0.56)
        matrix.SetElement(2,1,-0.50)
        matrix.SetElement(2,2,-0.66)
        transform.ApplyTransformMatrix(matrix)
        sphereModel.SetAndObserveTransformNodeID(transform.GetID())
        harden = logic.createIntermediateHardenModel(sphereModel)
        a = harden.GetPolyData().GetPoint(5)
        hardenPoint.append(a)
        #test 3
        matrix.SetElement(0,3,20)
        transform.ApplyTransformMatrix(matrix)
        sphereModel.SetAndObserveTransformNodeID(transform.GetID())
        harden = logic.createIntermediateHardenModel(sphereModel)
        a = harden.GetPolyData().GetPoint(5)
        hardenPoint.append(a)
        # reference
        point = list()
        point.append([117.49279022216797, 0.0, -22.252094268798828])
        point.append([76.22811126708984, -46.053489685058594, -51.109580993652344])
        point.append([45.985511779785156, -83.88117218017578, 14.071327209472656])
        for i in range(0, 3):
            if hardenPoint[i][0] != point[i][0]\
                    or hardenPoint[i][1] != point[i][1]\
                    or hardenPoint[i][2] != point[i][2]:
                print("test", i, "CreateIntermediateHardenModel: failed")
                return False
            else:
                print("test", i, "CreateIntermediateHardenModel: succeed")

        return True

    def testGetClosestPointIndexFunction(self):
        sphereModel = self.defineSphere()
        slicer.mrmlScene.AddNode(sphereModel)
        closestPointIndexList = list()
        polyData = sphereModel.GetPolyData()
        logic = SurfaceRegistrationLogic(slicer.modules.SurfaceRegistrationWidget)
        markupsLogic = self.defineMarkupsLogic()
        closestPointIndexList.append(
            logic.getClosestPointIndex(slicer.mrmlScene.GetNodeByID(markupsLogic.GetActiveListID()),
                                       polyData,
                                       0))
        closestPointIndexList.append(
            logic.getClosestPointIndex(slicer.mrmlScene.GetNodeByID(markupsLogic.GetActiveListID()),
                                       polyData,
                                       1))
        closestPointIndexList.append(
            logic.getClosestPointIndex(slicer.mrmlScene.GetNodeByID(markupsLogic.GetActiveListID()),
                                       polyData,
                                       2))

        closestPointIndexListResult = [9, 35, 1]

        for i in range(0, 3):
            if closestPointIndexList[i] != closestPointIndexListResult[i]:
                print("test ", i, " GetClosestPointIndex: failed")
                return False
            else:
                print("test ", i, " GetClosestPointIndex: succeed")
        return True

    def testReplaceLandmarkFunction(self):
        logic = SurfaceRegistrationLogic(slicer.modules.SurfaceRegistrationWidget)
        sphereModel = self.defineSphere()
        polyData = sphereModel.GetPolyData()
        markupsLogic = self.defineMarkupsLogic()
        listCoordinates = list()
        listCoordinates.append([55.28383255004883, 55.28383255004883, 62.34897994995117])
        listCoordinates.append([-68.93781280517578, -68.93781280517578, -22.252094268798828])
        listCoordinates.append([0.0, 0.0, -100.0])
        closestPointIndexList = [9, 35, 1]
        coord = [-1, -1, -1]
        for i in range(0, slicer.mrmlScene.GetNodeByID(markupsLogic.GetActiveListID()).GetNumberOfFiducials()):
            logic.replaceLandmark(polyData, slicer.mrmlScene.GetNodeByID(markupsLogic.GetActiveListID()),
                                  i,
                                  closestPointIndexList[i])
            slicer.mrmlScene.GetNodeByID(markupsLogic.GetActiveListID()).GetNthFiducialPosition(i, coord)
            if coord != listCoordinates[i]:
                print("test ",i ," ReplaceLandmark: failed")
                return False
            else:
                print("test ",i ," ReplaceLandmark: succeed")
        return True

    def testDefineNeighborsFunction(self):
        logic = SurfaceRegistrationLogic(slicer.modules.SurfaceRegistrationWidget)
        sphereModel = self.defineSphere()
        polyData = sphereModel.GetPolyData()
        closestPointIndexList = [9, 35, 1]
        connectedVerticesReferenceList = list()
        connectedVerticesReferenceList.append([9, 2, 3, 8, 10, 15, 16])
        connectedVerticesReferenceList.append(
            [35, 28, 29, 34, 36, 41, 42, 21, 22, 27, 23, 30, 33, 40, 37, 43, 47, 48, 49])
        connectedVerticesReferenceList.append(
            [1, 7, 13, 19, 25, 31, 37, 43, 49, 6, 48, 12, 18, 24, 30, 36, 42, 5, 47, 41, 11, 17, 23, 29, 35])
        connectedVerticesTestedList = list()

        for i in range(0, 3):
            inter = vtk.vtkIdList()
            logic.defineNeighbor(inter,
                                 polyData,
                                 closestPointIndexList[i],
                                 i + 1)
            connectedVerticesTestedList.append(inter)
            list1 = list()
            for j in range(0, connectedVerticesTestedList[i].GetNumberOfIds()):
                list1.append(int(connectedVerticesTestedList[i].GetId(j)))
            connectedVerticesTestedList[i] = list1
            if connectedVerticesTestedList[i] != connectedVerticesReferenceList[i]:
                print("test ",i ," AddArrayFromIdList: failed")
                return False
            else:
                print("test ",i ," AddArrayFromIdList: succeed")
        return True

    def testAddArrayFromIdListFunction(self):
        logic = SurfaceRegistrationLogic(slicer.modules.SurfaceRegistrationWidget)
        sphereModel = self.defineSphere()
        polyData = sphereModel.GetPolyData()
        closestPointIndexList = [9, 35, 1]
        for i in range(0, 3):
            inter = vtk.vtkIdList()
            logic.defineNeighbor(inter, polyData, closestPointIndexList[i], i + 1)
            logic.addArrayFromIdList(inter,
                                     sphereModel,
                                     'Test_' + str(i + 1))
            if polyData.GetPointData().HasArray('Test_' + str(i + 1)) != 1:
                print("test ",i ," AddArrayFromIdList: failed")
                return False
            else:
                print("test ",i ," AddArrayFromIdList: succeed")
        return True

    def testGetROIPolydata(self):
        logic = SurfaceRegistrationLogic(slicer.modules.SurfaceRegistrationWidget)
        sphereModel = self.defineSphere()
        harden = slicer.mrmlScene.AddNode(sphereModel)
        logic.updateDictModel(sphereModel)
        closestPointIndexList = [9, 35, 1]
        XPosition = list()
        YPosition = list()
        ZPosition = list()
        XPosition.append([0.0, 43.38837432861328, 78.18315124511719, 97.49279022216797, 30.680213928222656, 55.28383255004883, 68.93781280517578, 68.93781280517578, 2.6567715668640796e-15, 4.7873370442571075e-15, 5.969711605878806e-15, 5.969711605878806e-15, -55.28383255004883, -68.93781280517578, -68.93781280517578, 30.680213928222656, 55.28383255004883])
        YPosition.append([0.0, 0.0, 0.0, 0.0, 30.680213928222656, 55.28383255004883, 68.93781280517578, 68.93781280517578, 43.38837432861328, 78.18315124511719, 97.49279022216797, 97.49279022216797, 55.28383255004883, 68.93781280517578, 68.93781280517578, -30.680213928222656, -55.28383255004883])
        ZPosition.append([100.0, 90.09688568115234, 62.34897994995117, 22.252094268798828, 90.09688568115234, 62.34897994995117, 22.252094268798828, -22.252094268798828, 90.09688568115234, 62.34897994995117, 22.252094268798828, -22.252094268798828, 62.34897994995117, 22.252094268798828, -22.252094268798828, 90.09688568115234, 62.34897994995117])
        XPosition.append([0.0, 97.49279022216797, 78.18315124511719, 43.38837432861328, 2.6567715668640796e-15, 4.7873370442571075e-15, 5.969711605878806e-15, 5.969711605878806e-15, -30.680213928222656, -55.28383255004883, -68.93781280517578, -68.93781280517578, -55.28383255004883, -43.38837432861328, -78.18315124511719, -97.49279022216797, -97.49279022216797, -78.18315124511719, -43.38837432861328, -30.680213928222656, -55.28383255004883, -68.93781280517578, -68.93781280517578, -55.28383255004883, -30.680213928222656, -1.4362011132771323e-14, -1.7909134394119945e-14, -1.7909134394119945e-14, -1.4362011132771323e-14, -7.970314912350476e-15, 68.93781280517578, 68.93781280517578, 55.28383255004883, 30.680213928222656])
        YPosition.append([0.0, 0.0, 0.0, 0.0, 43.38837432861328, 78.18315124511719, 97.49279022216797, 97.49279022216797, 30.680213928222656, 55.28383255004883, 68.93781280517578, 68.93781280517578, 55.28383255004883, 5.313543133728159e-15, 9.574674088514215e-15, 1.1939423211757613e-14, 1.1939423211757613e-14, 9.574674088514215e-15, 5.313543133728159e-15, -30.680213928222656, -55.28383255004883, -68.93781280517578, -68.93781280517578, -55.28383255004883, -30.680213928222656, -78.18315124511719, -97.49279022216797, -97.49279022216797, -78.18315124511719, -43.38837432861328, -68.93781280517578, -68.93781280517578, -55.28383255004883, -30.680213928222656])
        ZPosition.append([-100.0, -22.252094268798828, -62.34897994995117, -90.09688568115234, 90.09688568115234, 62.34897994995117, 22.252094268798828, -22.252094268798828, 90.09688568115234, 62.34897994995117, 22.252094268798828, -22.252094268798828, -62.34897994995117, 90.09688568115234, 62.34897994995117, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 90.09688568115234, 62.34897994995117, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 62.34897994995117, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234])
        XPosition.append([0.0, 97.49279022216797, 97.49279022216797, 78.18315124511719, 43.38837432861328, 68.93781280517578, 68.93781280517578, 55.28383255004883, 30.680213928222656, 5.969711605878806e-15, 5.969711605878806e-15, 4.7873370442571075e-15, 2.6567715668640796e-15, -68.93781280517578, -68.93781280517578, -55.28383255004883, -30.680213928222656, -97.49279022216797, -97.49279022216797, -78.18315124511719, -43.38837432861328, -68.93781280517578, -68.93781280517578, -55.28383255004883, -30.680213928222656, -1.7909134394119945e-14, -1.7909134394119945e-14, -1.4362011132771323e-14, -7.970314912350476e-15, 68.93781280517578, 68.93781280517578, 55.28383255004883, 30.680213928222656])
        YPosition.append([0.0, 0.0, 0.0, 0.0, 0.0, 68.93781280517578, 68.93781280517578, 55.28383255004883, 30.680213928222656, 97.49279022216797, 97.49279022216797, 78.18315124511719, 43.38837432861328, 68.93781280517578, 68.93781280517578, 55.28383255004883, 30.680213928222656, 1.1939423211757613e-14, 1.1939423211757613e-14, 9.574674088514215e-15, 5.313543133728159e-15, -68.93781280517578, -68.93781280517578, -55.28383255004883, -30.680213928222656, -97.49279022216797, -97.49279022216797, -78.18315124511719, -43.38837432861328, -68.93781280517578, -68.93781280517578, -55.28383255004883, -30.680213928222656])
        ZPosition.append([-100.0, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234, 22.252094268798828, -22.252094268798828, -62.34897994995117, -90.09688568115234])
        for i in range(0, 3):
            inter = vtk.vtkIdList()
            logic.defineNeighbor(inter,
                                 harden.GetPolyData(),
                                 closestPointIndexList[i],
                                 i + 1)
            logic.dictionaryInput[sphereModel.GetID()].ROIPointListID = inter
            ROIPolydata = logic.getROIPolydata(sphereModel)
            for j in range (0,ROIPolydata.GetNumberOfPoints()):
                if ROIPolydata.GetPoint(j)[0] != XPosition[i][j] \
                        or ROIPolydata.GetPoint(j)[1] != YPosition[i][j] \
                        or ROIPolydata.GetPoint(j)[2] != ZPosition[i][j]:
                    print("test ",i ," GetROIPolydata: failed")
                    return False
            print("test ",i ," GetROIPolydata: succeed")
        return True

    def testRunFiducialRegistration(self):
        logic = SurfaceRegistrationLogic(slicer.modules.SurfaceRegistrationWidget)
        referenceMarkupsFiducial = slicer.vtkMRMLMarkupsFiducialNode()
        referenceMarkupsFiducial.SetName("RF")
        slicer.mrmlScene.AddNode(referenceMarkupsFiducial)
        referenceMarkupsFiducial.AddFiducial(0.0, 0.0, 0.0)
        referenceMarkupsFiducial.AddFiducial(0.0, 10.0, 0.0)
        referenceMarkupsFiducial.AddFiducial(0.0, -10.0, 0.0)

        Fiducial1 = slicer.vtkMRMLMarkupsFiducialNode()
        Fiducial1.SetName("F1")
        slicer.mrmlScene.AddNode(Fiducial1)
        Fiducial1.AddFiducial(10.0, 0.0, 0.0)
        Fiducial1.AddFiducial(10.0, 10.0, 0.0)
        Fiducial1.AddFiducial(10.0, -10.0, 0.0)

        Fiducial2 = slicer.vtkMRMLMarkupsFiducialNode()
        Fiducial2.SetName("F2")
        slicer.mrmlScene.AddNode(Fiducial2)
        Fiducial2.AddFiducial(0.0, 0.0, 0.0)
        Fiducial2.AddFiducial(0.0, -10.0, 10.0)
        Fiducial2.AddFiducial(0.0, 10.0, -10.0)

        outTransform = slicer.vtkMRMLLinearTransformNode()
        outTransform.SetName("testTransform")
        slicer.mrmlScene.AddNode(outTransform)
        outMatrix = list()
        logic.runFiducialRegistration(referenceMarkupsFiducial,referenceMarkupsFiducial,outTransform,"Rigid")
        self.matrixToList(outTransform.GetMatrixTransformFromParent(),outMatrix)
        logic.runFiducialRegistration(referenceMarkupsFiducial,Fiducial1,outTransform,"Rigid")
        self.matrixToList(outTransform.GetMatrixTransformFromParent(),outMatrix)
        logic.runFiducialRegistration(referenceMarkupsFiducial,Fiducial2,outTransform,"Rigid")
        self.matrixToList(outTransform.GetMatrixTransformFromParent(),outMatrix)

        controlMatrix = list()
        controlMatrix.append([1.0, -0.0, 0.0, -0.0, -0.0, 1.0, -0.0, 0.0, 0.0, -0.0, 1.0, -0.0, -0.0, 0.0, -0.0, 1.0])
        controlMatrix.append([1.0, -0.0, 0.0, 10.0, -0.0, 1.0, -0.0, 0.0, 0.0, -0.0, 1.0, -0.0, -0.0, 0.0, -0.0, 1.0])
        controlMatrix.append([-1.0000000000000004, -0.0, 0.0, -0.0, -0.0, -0.7071067811865479, 0.7071067811865477, 0.0, 0.0, 0.7071067811865477, 0.7071067811865475, -0.0, -0.0, 0.0, -0.0, 1.0])

        for i in range(0, 3):
            for j in range (0,16):
                if outMatrix[i][j] - controlMatrix[i][j] > 1e-5:
                    print("test ",i ," RunFiducialRegistration: failed")
                    return False
            print("test ",i ," RunFiducialRegistration: succeed")
        return True

    def testRunICP(self):
        logic = SurfaceRegistrationLogic(slicer.modules.SurfaceRegistrationWidget)
        fixedModel = self.defineSphere()
        transform = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(transform)
        transform.SetName("test")
        outTransform = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(outTransform)
        outTransform.SetName("test")
        outMatrix = list()
        #test 1
        sphereModel = self.defineSphere([50,50,50])
        logic.runICP(fixedModel.GetPolyData(),sphereModel.GetPolyData(),outTransform,"Absolute Value","RigidBody",
                     200,0.01,200,False,False)
        self.matrixToList(outTransform.GetMatrixTransformFromParent(),outMatrix)
        #test 2
        sphereModel = self.defineSphere([-500,50,390])
        logic.runICP(fixedModel.GetPolyData(),sphereModel.GetPolyData(),outTransform,"Absolute Value","Similarity",
                     1000,0.01,200,True,False)
        self.matrixToList(outTransform.GetMatrixTransformFromParent(),outMatrix)
        #test 3
        sphereModel = self.defineSphere([590,450,550])
        logic.runICP(fixedModel.GetPolyData(),sphereModel.GetPolyData(),outTransform,"Root Mean Square","RigidBody",
                     200,0.0001,500,True,True)
        self.matrixToList(outTransform.GetMatrixTransformFromParent(),outMatrix)

        controlMatrix = list()
        controlMatrix.append([0.9999999999999923, -4.279253171898915e-08, 1.1110679174853347e-07, 50.00000851831867, 4.2792541798255874e-08, 0.9999999999999948, -9.065735075747138e-08, 49.999998934011444, -1.1110678783316003e-07, 9.065735562782809e-08, 0.9999999999999888, 50.00000667708221, -0.0, -0.0, -0.0, 1.0])
        controlMatrix.append([1.000004009517861, -1.9237628046700715e-08, 7.542521002557797e-15, -500.000014730678, 1.9237628046700715e-08, 1.000004009517861, 3.487673804108392e-15, 50.00000052625974, -7.542521069652104e-15, -3.487673659008763e-15, 1.0000040095178613, 390.000000000001, 0.0, 0.0, -0.0, 1.0])
        controlMatrix.append([1.0, -2.0899226190521931e-10, 1.3553095062753832e-09, 590.000002010415, 2.0899226247775542e-10, 1.0, -4.224393595596447e-10, 450.00000204856195, -1.3553095061870965e-09, 4.224393598428939e-10, 1.0, 549.9999986267089, -0.0, -0.0, -0.0, 1.0])
        for i in range(0, 3):
            for j in range (0,16):
                if outMatrix[i][j] != controlMatrix[i][j]:
                    print("test ",i ," RunICP: failed")
                    return False
            print("test ",i ," RunICP: succeed")
        return True

    # ------------------------------------------------------------
    #                          global tests
    # ------------------------------------------------------------

    def testLandmarkRegistration(self):

        self.delayDisplay("Starting Landmark Registration Test")

        surfaceRegistration = slicer.modules.SurfaceRegistrationWidget

        surfaceRegistration.fiducialRegistration.setChecked(True)

        surfaceRegistration.inputFixedModelSelector.setCurrentNode(
            slicer.mrmlScene.GetNodesByName("02").GetItemAsObject(0))
        surfaceRegistration.inputMovingModelSelector.setCurrentNode(
            slicer.mrmlScene.GetNodesByName("01").GetItemAsObject(0))

        movingMarkupsFiducial = slicer.vtkMRMLMarkupsFiducialNode()
        movingMarkupsFiducial.SetName("moving MarkupsFiducial")
        slicer.mrmlScene.AddNode(movingMarkupsFiducial)
        surfaceRegistration.inputMovingLandmarksSelector.setCurrentNode(movingMarkupsFiducial)

        movingMarkupsFiducial.AddFiducial(8.08220491, -98.03022892, 93.12060543)
        surfaceRegistration.logic.onPointModifiedEvent(movingMarkupsFiducial,None)
        movingMarkupsFiducial.AddFiducial(-64.97482242, -26.20270453, 40.0195569)
        surfaceRegistration.logic.onPointModifiedEvent(movingMarkupsFiducial,None)
        movingMarkupsFiducial.AddFiducial(-81.14900734, -108.26332837, 121.16330592)
        surfaceRegistration.logic.onPointModifiedEvent(movingMarkupsFiducial,None)

        fixedMarkupsFiducial = slicer.vtkMRMLMarkupsFiducialNode()
        fixedMarkupsFiducial.SetName("fixed MarkupsFiducial")
        slicer.mrmlScene.AddNode(fixedMarkupsFiducial)
        surfaceRegistration.inputFixedLandmarksSelector.setCurrentNode(fixedMarkupsFiducial)

        fixedMarkupsFiducial.AddFiducial(-39.70435272, -97.08191652, 91.88711809)
        surfaceRegistration.logic.onPointModifiedEvent(movingMarkupsFiducial,None)
        fixedMarkupsFiducial.AddFiducial(-96.02709079, -18.26063616, 21.47774342)
        surfaceRegistration.logic.onPointModifiedEvent(movingMarkupsFiducial,None)
        fixedMarkupsFiducial.AddFiducial(-127.93278815, -106.45001448, 92.35628815)
        surfaceRegistration.logic.onPointModifiedEvent(movingMarkupsFiducial,None)

        outTransform = slicer.vtkMRMLLinearTransformNode()
        outTransform.SetName("outputFiducialTransform")
        slicer.mrmlScene.AddNode(outTransform)
        surfaceRegistration.outputTransformSelector.setCurrentNode(outTransform)

        surfaceRegistration.computeButton.click()
        checkTransform = slicer.mrmlScene.GetNodesByName("FiducialTransform").GetItemAsObject(0)
        checkMatrix = checkTransform.GetMatrixTransformFromParent()
        print(checkMatrix)
        outMatrix = outTransform.GetMatrixTransformFromParent()
        print(outMatrix)

        surfaceRegistration.inputMovingLandmarksSelector.setCurrentNode(None)
        surfaceRegistration.inputFixedLandmarksSelector.setCurrentNode(None)
        slicer.mrmlScene.RemoveNode(movingMarkupsFiducial)
        slicer.mrmlScene.RemoveNode(fixedMarkupsFiducial)

        return self.areMatrixEquals(checkMatrix, outMatrix)

    def testSurfaceRegistration(self):

        self.delayDisplay("Starting Surface Registration Test")

        surfaceRegistration = slicer.modules.SurfaceRegistrationWidget

        surfaceRegistration.surfaceRegistration.setChecked(True)

        surfaceRegistration.inputFixedModelSelector.setCurrentNode(
            slicer.mrmlScene.GetNodesByName("02").GetItemAsObject(0))
        surfaceRegistration.inputMovingModelSelector.setCurrentNode(
            slicer.mrmlScene.GetNodesByName("01").GetItemAsObject(0))

        outTransform = slicer.vtkMRMLLinearTransformNode()
        outTransform.SetName("outputSurfaceTransform")
        slicer.mrmlScene.AddNode(outTransform)
        surfaceRegistration.outputTransformSelector.setCurrentNode(outTransform)

        surfaceRegistration.numberOfIterationsValueChanged = 200
        surfaceRegistration.maxDistanceValueChanged = 0.01

        surfaceRegistration.computeButton.click()

        checkTransform = slicer.mrmlScene.GetNodesByName("surfaceTransform").GetItemAsObject(0)
        checkMatrix = checkTransform.GetMatrixTransformFromParent()

        outMatrix = outTransform.GetMatrixTransformFromParent()

        print(checkMatrix)
        print(outMatrix)

        return self.areMatrixEquals(checkMatrix, outMatrix)

    def testROIRegistration(self):

        self.delayDisplay("Starting ROI Registration Test")

        surfaceRegistration = slicer.modules.SurfaceRegistrationWidget

        surfaceRegistration.ROIRegistration.setChecked(True)

        surfaceRegistration.inputFixedModelSelector.setCurrentNode(
            slicer.mrmlScene.GetNodesByName("02").GetItemAsObject(0))
        surfaceRegistration.inputMovingModelSelector.setCurrentNode(
            slicer.mrmlScene.GetNodesByName("01").GetItemAsObject(0))

        # equivalent to fixed radio selection
        surfaceRegistration.onFixedModelRadio()
        fixedMarkupsFiducial = slicer.vtkMRMLMarkupsFiducialNode()
        fixedMarkupsFiducial.SetName("fixed MarkupsFiducial")
        slicer.mrmlScene.AddNode(fixedMarkupsFiducial)
        surfaceRegistration.inputFixedLandmarksSelector.setCurrentNode(fixedMarkupsFiducial)
        fixedMarkupsFiducial.AddFiducial(-127.93278815, -106.45001448, 92.35628815)
        surfaceRegistration.logic.onPointModifiedEvent(fixedMarkupsFiducial,None)
        # equivalent to clean button
        selectedLandmark = surfaceRegistration.landmarkComboBox.currentText
        surfaceRegistration.logic.cleanMesh(selectedLandmark)
        surfaceRegistration.onRadiusValueChanged()
        # changement of radius
        surfaceRegistration.radiusDefinitionWidget.value = 40

        # equivalent to moving radio selection
        surfaceRegistration.onMovingModelRadio()
        movingMarkupsFiducial = slicer.vtkMRMLMarkupsFiducialNode()
        movingMarkupsFiducial.SetName("moving MarkupsFiducial")
        slicer.mrmlScene.AddNode(movingMarkupsFiducial)
        surfaceRegistration.inputMovingLandmarksSelector.setCurrentNode(movingMarkupsFiducial)
        movingMarkupsFiducial.AddFiducial(-81.14900734, -108.26332837, 121.16330592)
        surfaceRegistration.logic.onPointModifiedEvent(movingMarkupsFiducial,None)
        # equivalent to clean button
        selectedLandmark = surfaceRegistration.landmarkComboBox.currentText
        surfaceRegistration.logic.cleanMesh(selectedLandmark)
        surfaceRegistration.onRadiusValueChanged()
        # changement of radius
        surfaceRegistration.radiusDefinitionWidget.value = 35

        surfaceRegistration.numberOfIterationsValueChanged = 200
        surfaceRegistration.maxDistanceValueChanged = 0.01

        outTransform = slicer.vtkMRMLLinearTransformNode()
        outTransform.SetName("outputROITransform")
        slicer.mrmlScene.AddNode(outTransform)
        surfaceRegistration.outputTransformSelector.setCurrentNode(outTransform)

        surfaceRegistration.computeButton.click()
        checkTransform = slicer.mrmlScene.GetNodesByName("ROItransform").GetItemAsObject(0)
        checkMatrix = checkTransform.GetMatrixTransformFromParent()
        print(checkMatrix)
        outMatrix = outTransform.GetMatrixTransformFromParent()
        print(outMatrix)

        return self.areMatrixEquals(checkMatrix, outMatrix)

    # ------------------------------------------------------------
    #                       util functions
    # ------------------------------------------------------------
    def defineSphere(self, center = [0,0,0]):
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetRadius(100.0)
        sphereSource.SetCenter(center)
        sphereSource.Update()
        model = slicer.vtkMRMLModelNode()
        model.SetAndObservePolyData(sphereSource.GetOutput())
        modelDisplay = slicer.vtkMRMLModelDisplayNode()
        slicer.mrmlScene.AddNode(modelDisplay)
        model.SetAndObserveDisplayNodeID(modelDisplay.GetID())
        modelDisplay.SetInputPolyDataConnection(sphereSource.GetOutputPort())
        modelDisplay.VisibilityOff()
        return model

    def defineMarkupsLogic(self):
        slicer.mrmlScene.Clear(0)
        markupsLogic = slicer.modules.markups.logic()
        markupsLogic.AddFiducial(58.602, 41.692, 62.569)
        markupsLogic.AddFiducial(-59.713, -67.347, -19.529)
        markupsLogic.AddFiducial(-10.573, -3.036, -93.381)
        return markupsLogic

    def areMatrixEquals(self, a, b):

        for i in range(0, 4):
            for j in range(0, 4):
                if not ((a.GetElement(i, j) >= b.GetElement(i, j) - 1.0)
                        and (a.GetElement(i, j) <= b.GetElement(i, j) + 1.0)):
                    print(a.GetElement(i, j))
                    print(b.GetElement(i, j))
                    return False
        return True

    def matrixToList(self,matrix,liste):
        a = list()
        for i in range(0, 4):
            for j in range(0, 4):
                a.append(matrix.GetElement(i, j))
        liste.append(a)
