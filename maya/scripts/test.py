from PySide2 import QtCore, QtWidgets, QtGui
import shiboken2

import maya.cmds as mc
import maya.OpenMayaUI as omui

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

class LightPanel(object):

    def __init__(self):
        self.lightType = ""
        self.intensity = 10
        self.color = "#ffffff"
        self.castShadows = True

    def createUI(self, name):
        grpBox = QtWidgets.QGroupBox(name)
        fbox = QtWidgets.QFormLayout()

        lblType = QtWidgets.QLabel("Type")
        self.cboxType = QtWidgets.QComboBox()
        self.cboxType.addItem("Spot")
        self.cboxType.addItem("Directional")
        self.cboxType.addItem("Point")
        self.cboxType.currentIndexChanged.connect(lambda:self.selectionChanged())
        fbox.addRow(lblType, self.cboxType)

        lblInt = QtWidgets.QLabel("Intensity")
        self.txtIntensity = QtWidgets.QLineEdit()
        intValidator = QtGui.QIntValidator(1, 999)
        self.txtIntensity.setValidator(intValidator)
        self.txtIntensity.textChanged.connect(lambda:self.intensityChanged())
        fbox.addRow(lblInt, self.txtIntensity)

        lblClr = QtWidgets.QLabel("Color")
        self.clrBtn = QtWidgets.QPushButton()
        self.clrBtn.width = 64
        self.clrBtn.height = 64
        self.clrBtn.setStyleSheet("background-color: %s" % self.color)
        self.clrBtn.clicked.connect(lambda: self.colorClicked())
        fbox.addRow(lblClr, self.clrBtn)

        lblCast = QtWidgets.QLabel("Cast Shadows")
        self.rdBtn = QtWidgets.QCheckBox()
        self.rdBtn.setChecked(self.castShadows)
        self.rdBtn.toggled.connect(lambda:self.shadowsToggled())
        fbox.addRow(lblCast, self.rdBtn)

        grpBox.setLayout(fbox)
        grpBox.setFixedWidth(250)

        return grpBox

    def intensityChanged(self):
        self.intensity = self.txtIntensity.text()
        print self.intensity

    def shadowsToggled(self):
        self.castShadows = self.rdBtn.isChecked()
        print self.castShadows

    def selectionChanged(self):
        self.lightType = self.cboxType.currentText()
        print self.lightType

    def colorClicked(self):
        col = QtWidgets.QColorDialog.getColor()
        colorName = QtGui.QColor(col).name()
        print colorName
        self.clrBtn.setStyleSheet("background-color: %s" % colorName)


class LightRigPanel(object):

    def __init__(self):
        self.lightPos = ""
        self.radius = 5

    def createUI(self, name):
        grpBox = QtWidgets.QGroupBox(name)
        fbox = QtWidgets.QFormLayout()

        lblPos = QtWidgets.QLabel("Light Position")
        self.cboxPos = QtWidgets.QComboBox()
        self.cboxPos.addItem("Center")
        self.cboxPos.addItem("Low")
        self.cboxPos.addItem("High")
        self.cboxPos.currentIndexChanged.connect(lambda: self.selectionChanged())
        fbox.addRow(lblPos, self.cboxPos)

        lblRad = QtWidgets.QLabel("Radius")
        self.txtRad = QtWidgets.QLineEdit()
        intValidator = QtGui.QIntValidator(1, 999)
        self.txtRad.setValidator(intValidator)
        self.txtRad.textChanged.connect(lambda: self.radiusChanged())
        self.txtRad.setFixedWidth(50)
        fbox.addRow(lblRad, self.txtRad)

        grpBox.setLayout(fbox)

        return grpBox


    def radiusChanged(self):
        self.radius = self.txtRad.text()
        print self.radius

    def selectionChanged(self):
        self.lightPos = self.cboxPos.currentText()
        print self.lightPos

class LightRigTool(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        parent = parent or getMainWindow()
        super(LightRigTool, self).__init__(parent)

        # Main Widget
        widget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QVBoxLayout(widget)

        # Grid layout to place radio buttons
        self.grid = QtWidgets.QGridLayout()

        keyLight = LightPanel()
        fillLight = LightPanel()
        rimLight = LightPanel()
        lightRig = LightRigPanel()

        self.grid.addWidget(keyLight.createUI("Key Light"), 1, 1)
        self.grid.addWidget(lightRig.createUI("Light Rig"), 1, 2)
        self.grid.addWidget(fillLight.createUI("Fill Light"), 2, 1)
        self.grid.addWidget(CreateLRButtonsPanel(), 2, 2)
        self.grid.addWidget(rimLight.createUI("Rim/Back Light"), 3, 1)
        self.grid.setSpacing(15)
        self.mainLayout.addLayout(self.grid)
        self.setCentralWidget(widget)
        self.show()
        self.raise_()


def CreateLRButtonsPanel():
    grpBox = QtWidgets.QGroupBox()
    vbox = QtWidgets.QVBoxLayout()

    lbl = QtWidgets.QLabel("NOTE: Please select a source object before you create a 3-point light setup")
    vbox.addWidget(lbl)

    hbox1 = QtWidgets.QHBoxLayout()
    verticalSpacer1 = QtWidgets.QSpacerItem(340, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    hbox1.addItem(verticalSpacer1)
    btnCreate = QtWidgets.QPushButton("Create 3-Point Setup")
    btnCreate.clicked.connect(lambda : createClicked())
    hbox1.addWidget(btnCreate)
    vbox.addItem(hbox1)

    hbox2 = QtWidgets.QHBoxLayout()
    verticalSpacer2 = QtWidgets.QSpacerItem(340, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    hbox2.addItem(verticalSpacer2)
    btnRestore = QtWidgets.QPushButton("Restore Defaults")
    hbox2.addWidget(btnRestore)
    vbox.addItem(hbox2)

    hbox = QtWidgets.QHBoxLayout()
    btnSavePreset = QtWidgets.QPushButton("Save As Preset")
    btnLoadPreset = QtWidgets.QPushButton("Load Preset")
    hbox.addWidget(btnSavePreset)
    hbox.addWidget(btnLoadPreset)
    hbox.setSpacing(15)
    hbox.addStretch()

    vbox.addItem(hbox)

    grpBox.setLayout(vbox)

    return grpBox

def createClicked():
    print "Create Clicked"


"""
    Main program invocation happens here
"""
if __name__ == '__main__':
    print "Loading Tool"
    win = LightRigTool(getMainWindow())



import json
class LightPanel(object):
    def __init__(self):
        self.lightType = ""
        self.intensity = 3.0
        self.bgcolor = "#ffffff"
        self.color = [1.0, 1.0, 1.0]
        self.castShadows = False




obj = LightPanel()
print(obj.toJSON())

