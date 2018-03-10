from PySide2 import QtCore, QtWidgets, QtGui
import shiboken2

import maya.cmds as mc
import maya.OpenMayaUI as omui
import math
import json
import os

def getMainWindow():
    """
    Returns the main maya window as the appropriate QObject to use as a parent.
    """

    ptr = omui.MQtUtil.mainWindow()
    qObj = shiboken2.wrapInstance(long(ptr), QtCore.QObject)
    metaObj = qObj.metaObject()
    cls = metaObj.className()
    superCls = metaObj.superClass().className()
    if hasattr(QtWidgets, cls):
        base = getattr(QtWidgets, cls)
    elif hasattr(QtWidgets, superCls):
        base = getattr(QtWidgets, superCls)
    else:
        base = QtWidgets.QWidget
    mainWin = shiboken2.wrapInstance(long(ptr), base)

    return mainWin

"""
    Desc:
        Class to create a 3-point light rig

    Parameters:
        Needs keylight, filllight, rimLigth, and light rig object settings
        at the time of initialization
"""
class LightRig():

    def __init__(self, keyLight, fillLight, rimLight, rigSettings):
        self.keyLight = keyLight
        self.fillLight = fillLight
        self.rimLight = rimLight
        self.settings = rigSettings

    """
    Desc:
        The is the main function which actually creates
        3-point light rig
    Parameters:
        NONE
    Returns:
        NONE
    """
    def createRig(self):
        # Create a Cube for test cases
        mc.polySphere(name='mySphere')
        objCenter = mc.objectCenter('mySphere', l=True)

        # Get the bounding box for the selected ojbject
        XYZ = mc.xform('mySphere', bb=True, q=True)
        rad = XYZ[3] / 2 * self.settings.radius
        strltPos = self.settings.lightPos
        lightP = 0.0

        if strltPos == "High":
            lightP = 5.0
        elif strltPos == "Low":
            lightP = -5.0
        else:
            lightP = 0.0

        # Create a circle to place three point lights
        mc.circle(n='curveLights', nr=(0, 1, 0), c=(0, 0, 0), sections=9, radius=rad)

        # Create lights in three positions on the curve
        loc = mc.pointOnCurve('curveLights', pr=0.0, p=True)
        #_item = mc.spotLight(name='FillLight', coneAngle=45)
        _item = self.createLight(self.fillLight, "FillLight")
        mc.move(loc[0], loc[1]+lightP, loc[2], _item, ls=True)

        loc = mc.pointOnCurve('curveLights', pr=3.0, p=True)
        #_item = mc.spotLight(name='KeyLight', coneAngle=45)
        _item = self.createLight(self.keyLight, "KeyLight")
        mc.move(loc[0], loc[1]+lightP, loc[2], _item, ls=True)

        loc = mc.pointOnCurve('curveLights', pr=6.0, p=True)
        #_item = mc.spotLight(name='RimLight', coneAngle=45)
        _item = self.createLight(self.rimLight, "RimLight")
        mc.move(loc[0], loc[1]+lightP, loc[2], _item, ls=True)

        # Create space locator and aimConstraints
        mc.spaceLocator(n='fillLocator', p=(objCenter[0], objCenter[1], objCenter[2]))
        mc.aimConstraint('fillLocator', 'FillLight', aimVector=(0.0, 0.0, -1.0))
        mc.parent('fillLocator', 'curveLights', relative=True)

        mc.spaceLocator(n='keyLocator', p=(objCenter[0], objCenter[1], objCenter[2]))
        mc.aimConstraint('keyLocator', 'KeyLight', aimVector=(0.0, 0.0, -1.0))
        mc.parent('keyLocator', 'curveLights', relative=True)

        mc.spaceLocator(n='rimLocator', p=(objCenter[0], objCenter[1], objCenter[2]))
        mc.aimConstraint('rimLocator', 'RimLight', aimVector=(0.0, 0.0, -1.0))
        mc.parent('rimLocator', 'curveLights', relative=True)

        # Create lights main locator
        mc.spaceLocator(n='lightsMainLocator', p=(objCenter[0], objCenter[1], objCenter[2]))
        mc.parent('FillLight', 'lightsMainLocator', relative=True)
        mc.parent('KeyLight', 'lightsMainLocator', relative=True)
        mc.parent('RimLight', 'lightsMainLocator', relative=True)

        # Create Main Group for the entire light rig
        mc.group('curveLights', 'lightsMainLocator', n='LightRigGroup')


    """
    Desc:
        Method to create light
    Parameters:
        Light settings objects
    Returns:
        light object
    """
    def createLight(self, lightObj, name):
        print "Intensity is: "
        print(lightObj.intensity)
        if lightObj.lightType == "Directional":
            light = mc.directionalLight(name=name, rgb=lightObj.color, intensity=lightObj.intensity,
                                 rs=lightObj.castShadows)
        elif lightObj.lightType == "Point":
            light = mc.pointLight(name=name, rgb=lightObj.color, intensity=lightObj.intensity,
                                 rs=lightObj.castShadows)
        else:
            light = mc.spotLight(name=name, coneAngle=45, rgb=lightObj.color, intensity=lightObj.intensity,
                                 rs=lightObj.castShadows)

        return light


"""
    Desc:
        Class to create light panel with all UI elements
"""
class LightPanel(object):

    def __init__(self):
        self.lightType = "Spot"
        self.intensity = 3.0
        self.bgcolor = "#ffffff"
        self.color = [1.0, 1.0, 1.0]
        self.castShadows = False

    """
    Desc:
        Method to create light panel UI
    Parameters:
        name: name of the light panel
    Returns:
        light panel groupbox
    """
    def createUI(self, name):
        grpBox = QtWidgets.QGroupBox(name)
        fbox = QtWidgets.QFormLayout()

        self.name = name

        lblType = QtWidgets.QLabel("Type")
        self.cboxType = QtWidgets.QComboBox()
        self.cboxType.addItem("Spot")
        self.cboxType.addItem("Directional")
        self.cboxType.addItem("Point")
        self.cboxType.currentIndexChanged.connect(lambda:self.selectionChanged())
        fbox.addRow(lblType, self.cboxType)

        lblInt = QtWidgets.QLabel("Intensity")
        self.txtIntensity = QtWidgets.QLineEdit()
        intValidator = QtGui.QDoubleValidator(1, 100, 2)
        self.txtIntensity.setValidator(intValidator)
        self.txtIntensity.textChanged.connect(lambda:self.intensityChanged())
        fbox.addRow(lblInt, self.txtIntensity)

        lblClr = QtWidgets.QLabel("Color")
        self.clrBtn = QtWidgets.QPushButton()
        self.clrBtn.width = 64
        self.clrBtn.height = 64
        self.clrBtn.setStyleSheet("background-color: %s" % self.bgcolor)
        self.clrBtn.clicked.connect(self.colorClicked)
        fbox.addRow(lblClr, self.clrBtn)

        lblCast = QtWidgets.QLabel("Cast Shadows")
        self.rdBtn = QtWidgets.QCheckBox()
        self.rdBtn.setChecked(self.castShadows)
        self.rdBtn.toggled.connect(lambda:self.shadowsToggled())
        fbox.addRow(lblCast, self.rdBtn)

        grpBox.setLayout(fbox)
        grpBox.setFixedWidth(250)

        return grpBox

    """
    Desc:
        Event method, raised when text changed
    Parameters:
        NONE
    Returns:
        NONE
    """
    def intensityChanged(self):
        try:
            self.intensity = float(self.txtIntensity.text())
        except ValueError:
            self.intensity = 0.0

    """
    Desc:
        Event method raised when castShadows checkbox status is changed
    Parameters:
        NON
    Returns:
        NON
    """
    def shadowsToggled(self):
        self.castShadows = self.rdBtn.isChecked()

    """
    Desc:
        Event method, raised when combobox selection is changed
    Parameters:
        NONE
    Returns:
        NONE
    """
    def selectionChanged(self):
        self.lightType = self.cboxType.currentText()

    """
    Desc:
        Event method, raised when color button is clicked to pick a new color
    Parameters:
        NONE
    Returns:
        NONE
    """
    @QtCore.Slot()
    def colorClicked(self):
        col = QtWidgets.QColorDialog.getColor()
        colorName = col.name()
        colors = col.getRgb()
        nval = math.sqrt(colors[0]*colors[0] + colors[1]*colors[1] + colors[2]*colors[2])
        if nval > 0:
            self.color = [float(colors[0]/nval), float(colors[1]/nval), float(colors[2]/nval)]
            print self.color
        #self.color = [float(colors[0]), float(colors[1]), float(colors[2])]
        self.clrBtn.setStyleSheet("background-color: %s" % colorName)

    """
    Desc:
        Method to set default values in UI controls when button is clicked
    Parameters:
        NONE
    Returns:
        NONE
    """
    def reloadDefaults(self, type=None, shadows=False, intensity="10.0", color=None):
        color = color or [1.0, 1.0, 1.0]
        type = type or "Spot"
        print "Color Value:", color

        index = self.cboxType.findText(type, QtCore.Qt.MatchFixedString)
        if index > 0:
            self.cboxType.setCurrentIndex(index)

        self.txtIntensity.setText(str(intensity))

        qtColor = QtGui.QColor.fromRgbF(*color)
        colorName = qtColor.name()
        self.clrBtn.setStyleSheet("background-color: %s" % colorName)
        self.color = color
        self.rdBtn.setChecked(shadows)

    def toJSON(self):
        data = {
            'name': self.name,
            'lightType': self.lightType,
            'intensity': self.intensity,
            'bgcolor': self.bgcolor,
            'color': self.color ,
            'castshadows': self.castShadows
        }
        return data

"""
    Desc:
        Class to create Lightrig UI panel
"""
class LightRigPanel(object):

    def __init__(self):
        self.lightPos = "Center"
        self.radius = 5.0

    """
    Desc:
        Method to create light rig panel UI
    Parameters:
        name: name of the light rig group box
    Returns:
        light rig panel groupbox
    """
    def createUI(self, name):
        grpBox = QtWidgets.QGroupBox(name)
        fbox = QtWidgets.QFormLayout()

        self.name = name

        lblPos = QtWidgets.QLabel("Light Position")
        self.cboxPos = QtWidgets.QComboBox()
        self.cboxPos.addItem("Center")
        self.cboxPos.addItem("Low")
        self.cboxPos.addItem("High")
        self.cboxPos.currentIndexChanged.connect(lambda: self.selectionChanged())
        fbox.addRow(lblPos, self.cboxPos)

        lblRad = QtWidgets.QLabel("Radius")
        self.txtRad = QtWidgets.QLineEdit()
        intValidator = QtGui.QDoubleValidator(1, 100, 2)
        self.txtRad.setValidator(intValidator)
        self.txtRad.textChanged.connect(lambda: self.radiusChanged())
        self.txtRad.setFixedWidth(50)
        fbox.addRow(lblRad, self.txtRad)

        grpBox.setLayout(fbox)

        return grpBox


    """
    Desc:
        Event method, raised when radius text field is changed
    Parameters:
        NONE
    Returns:
        NONE
    """
    def radiusChanged(self):
        try:
            self.radius = float(self.txtRad.text())
        except ValueError:
            self.radius = 5.0

    """
    Desc:
        Event method, raised when comboxbox selection is changed
    Parameters:
        NONE
    Returns:
        NONE
    """
    def selectionChanged(self):
        self.lightPos = self.cboxPos.currentText()

    """
    Desc:
        Method to set default values in UI controls when button is clicked
    Parameters:
        NONE
    Returns:
        NONE
    """
    def reloadDefaults(self, radius="10.0", pos=None):
        pos = pos or "Center"
        self.txtRad.setText(str(radius))

        index = self.cboxPos.findText(pos, QtCore.Qt.MatchFixedString)
        if index > 0:
            self.cboxPos.setCurrentIndex(index)

    def toJSON(self):
        data = {
            'name': self.name,
            'lightPos': self.lightPos,
            'radius': self.radius
        }
        return data

"""
    Desc:
        Main class to create LightRig UI tool and invoke all
        its functionality to create a 3-point light rig
"""
class LightRigTool(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        parent = parent or getMainWindow()
        super(LightRigTool, self).__init__(parent)

        # Main Widget
        widget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QVBoxLayout(widget)

        # Grid layout to place radio buttons
        self.grid = QtWidgets.QGridLayout()

        self.keyLight = LightPanel()
        self.fillLight = LightPanel()
        self.rimLight = LightPanel()
        self.lightRig = LightRigPanel()

        self.grid.addWidget(self.keyLight.createUI("Key Light"), 1, 1)
        self.grid.addWidget(self.lightRig.createUI("Light Rig"), 1, 2)
        self.grid.addWidget(self.fillLight.createUI("Fill Light"), 2, 1)
        self.grid.addWidget(self.createButtonsPanel(), 2, 2)
        self.grid.addWidget(self.rimLight.createUI("Rim/Back Light"), 3, 1)
        self.grid.setSpacing(15)
        self.mainLayout.addLayout(self.grid)
        self.setCentralWidget(widget)
        self.show()
        self.raise_()

    """
    Desc:
        Method to create buttons panel for creating light rig, restore defaults
    Parameters:
        NONE
    Returns:
        groupbox
    """
    def createButtonsPanel(self):
        grpBox = QtWidgets.QGroupBox()
        vbox = QtWidgets.QVBoxLayout()

        lbl = QtWidgets.QLabel("NOTE: Please select a source object before you create a 3-point light setup")
        vbox.addWidget(lbl)

        hbox1 = QtWidgets.QHBoxLayout()
        verticalSpacer1 = QtWidgets.QSpacerItem(340, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        hbox1.addItem(verticalSpacer1)
        btnCreate = QtWidgets.QPushButton("Create 3-Point Setup")
        btnCreate.clicked.connect(lambda: self.createClicked())
        hbox1.addWidget(btnCreate)
        vbox.addItem(hbox1)

        hbox2 = QtWidgets.QHBoxLayout()
        verticalSpacer2 = QtWidgets.QSpacerItem(340, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        hbox2.addItem(verticalSpacer2)
        btnRestore = QtWidgets.QPushButton("Restore Defaults")
        btnRestore.clicked.connect(lambda: self.restoreClicked())
        hbox2.addWidget(btnRestore)
        vbox.addItem(hbox2)

        hbox = QtWidgets.QHBoxLayout()
        btnSavePreset = QtWidgets.QPushButton("Save As Preset")
        btnSavePreset.clicked.connect(lambda : self.saveClicked())

        btnLoadPreset = QtWidgets.QPushButton("Load Preset")
        btnLoadPreset.clicked.connect(lambda: self.loadClicked())

        hbox.addWidget(btnSavePreset)
        hbox.addWidget(btnLoadPreset)
        hbox.setSpacing(15)
        hbox.addStretch()

        vbox.addItem(hbox)

        grpBox.setLayout(vbox)

        return grpBox

    """
    Desc:
        Method to actually create a 3-point light rig
    Parameters:
        NONE
    Returns:
        NONE
    """
    def createClicked(self):
        print "Create Clicked"
        mainRig = LightRig(self.keyLight, self.fillLight, self.rimLight, self.lightRig)
        mainRig.createRig()

    """
    Desc:
        Method to set default values in UI controls when button is clicked
    Parameters:
        NONE
    Returns:
        NONE
    """
    def restoreClicked(self):
        self.keyLight.reloadDefaults()
        self.fillLight.reloadDefaults()
        self.rimLight.reloadDefaults()
        self.lightRig.reloadDefaults()


    def saveClicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                            "JSON Files (*.json)", options=options)
        if fileName:
            print(fileName)
            uidata = {
                'KeyLight': self.keyLight.toJSON(),
                'FillLight': self.fillLight.toJSON(),
                'RimLight': self.rimLight.toJSON(),
                'LightRig': self.lightRig.toJSON()
            }
            data = json.dumps(uidata, indent=4)
            with open(fileName, 'w') as outfile:
                json.dump(data, outfile)

    def loadClicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "JSON Files (*.json)", options=options)
        if fileName:
            print(fileName)
            with open(fileName) as data_file:
                data_loaded = json.load(data_file)
                self.parseJSON(data_loaded)

    def parseJSON(self, data_loaded):
        data = json.loads(data_loaded)
        self.keyLight.reloadDefaults(type=data["KeyLight"]["lightType"]
                                     ,shadows=data["KeyLight"]["castshadows"]
                                     ,intensity=data["KeyLight"]["intensity"]
                                     ,color=data["KeyLight"]["color"])

        self.fillLight.reloadDefaults(type=data["FillLight"]["lightType"]
                                     , shadows=data["FillLight"]["castshadows"]
                                     , intensity=data["FillLight"]["intensity"]
                                     , color=data["FillLight"]["color"])

        self.rimLight.reloadDefaults(type=data["RimLight"]["lightType"]
                                     , shadows=data["RimLight"]["castshadows"]
                                     , intensity=data["RimLight"]["intensity"]
                                     , color=data["RimLight"]["color"])

        self.lightRig.reloadDefaults(radius=data["LightRig"]["radius"]
                                     ,pos=data["LightRig"]["lightPos"])


"""
    Main program invocation happens here
"""
if __name__ == '__main__':
    print "Loading Tool"
    win = LightRigTool(getMainWindow())


