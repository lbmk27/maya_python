from PySide2 import QtCore, QtWidgets, QtGui
import shiboken2

import maya.cmds as mc
import maya.OpenMayaUI as omui
import maya.mel as mel
import os
import shutil
import errno
import zipfile


# Global variable
g_texturesPath = "R:/Hand-ins/MDDN541/TOM/MAYA/TEXTURES"


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


# Create folder function definition
def create_folder( directory ):
    if not os.path.exists( directory ):
        os.makedirs( directory )


# Import all references into current scene file
def import_references():
    refs = mc.ls(type='reference')

    for i in refs:
        rFile = mc.referenceQuery(i, f=True)
        mc.file(rFile, importReference=True)


def copyDirectory(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    #print relroot
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zip:
        for root, dirs, files in os.walk(source_dir):
            #print root
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename): # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)


"""
    Desc:
        Class to create settings UI panel
"""
class SettingsPanel(object):

    def __init__(self):
        self.txtPrj = "default"
        self.txtScene = "test"
        self.txtLoc = "D:/RenderFarm"


    """
    Desc:
        Method to create settings panel UI
    Parameters:
        name: name of the settings group box
    Returns:
        light settings panel groupbox
    """
    def createUI(self, name):
        grpBox = QtWidgets.QGroupBox(name)
        fbox = QtWidgets.QFormLayout()

        self.name = name

        lblLoc = QtWidgets.QLabel("Maya project path")
        self.txtLoc = QtWidgets.QLineEdit()
        self.txtLoc.setFixedWidth(250)
        fbox.addRow(lblLoc, self.txtLoc)

        lblPrj = QtWidgets.QLabel("Project Name")
        self.txtPrj = QtWidgets.QLineEdit()
        self.txtPrj.setFixedWidth(250)
        fbox.addRow(lblPrj, self.txtPrj)
        
        lblScene = QtWidgets.QLabel("Scene Name")
        self.txtScene = QtWidgets.QLineEdit()
        self.txtScene.setFixedWidth(250)
        fbox.addRow(lblScene, self.txtScene)

        grpBox.setLayout(fbox)

        return grpBox



"""
    Desc:
        Main class to create RenderFarmTool UI tool and invoke all
        its functionality to renderfarm ready file
"""
class RenderFarmTool(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        parent = parent or getMainWindow()
        super(RenderFarmTool, self).__init__(parent)

        # Main Widget
        widget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QVBoxLayout(widget)

        # Grid layout to place radio buttons
        self.grid = QtWidgets.QGridLayout()

        self.settingsPnl = SettingsPanel()

        self.grid.addWidget(self.settingsPnl.createUI("Run RenderFarm file preparation process"), 1, 1)
        self.grid.addWidget(self.createButtonsPanel(), 2, 1)
        self.grid.setSpacing(15)
        self.mainLayout.addLayout(self.grid)
        self.setCentralWidget(widget)
        self.show()
        self.raise_()


    """
    Desc:
        Method to create buttons panel for creating file
    Parameters:
        NONE
    Returns:
        groupbox
    """
    def createButtonsPanel(self):
        grpBox = QtWidgets.QGroupBox()
        vbox = QtWidgets.QVBoxLayout()

        lbl = QtWidgets.QLabel("NOTE: This will initiate the file preparation process and can't be stopped.")
        vbox.addWidget(lbl)

        hbox1 = QtWidgets.QHBoxLayout()
        verticalSpacer1 = QtWidgets.QSpacerItem(340, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        hbox1.addItem(verticalSpacer1)
        btnCreate = QtWidgets.QPushButton("Create RenderFarm file")
        btnCreate.clicked.connect(lambda: self.createClicked())
        hbox1.addWidget(btnCreate)
        vbox.addItem(hbox1)

        lblSTxt = QtWidgets.QLabel("Status:")
        vbox.addWidget(lblSTxt)

        self.lblStatus = QtWidgets.QLabel("...")
        vbox.addWidget(self.lblStatus)

        grpBox.setLayout(vbox)

        return grpBox


    """
    Desc:
        Method to run the file preparation process
    Parameters:
        NONE
    Returns:
        NONE
    """
    def createClicked(self):
        print("Initiating file preparation process ...")
        self.lblStatus.setText("Initiating file preparation process ...")

        # Set path to Maya project folder
        maya_dir = self.settingsPnl.txtLoc.text() + "/" + self.settingsPnl.txtPrj.text()

        # Create project structure
        create_folder(maya_dir)

        mel.eval('setProject \"' + maya_dir + '\"')

        self.lblStatus.setText("Creating project and workspace ...")
        print("Creating project and workspace ...")
        # Create folder structure
        for file_rule in mc.workspace(query=True, fileRuleList=True):
            file_rule_dir = mc.workspace(fileRuleEntry=file_rule)
            maya_file_rule_dir = os.path.join( maya_dir, file_rule_dir)
            print(maya_file_rule_dir)
            create_folder( maya_file_rule_dir )

        # Import the references into maya file before saving
        self.lblStatus.setText("Importing references ...")
        print("Importing references ...")
        import_references()

        #srcpath = 'D:/test/ball'
        # Test directory shouldn't exists
        destexpath = maya_dir + "/sourceimages"

        # Delete sourceimages folder and create new one
        shutil.rmtree(destexpath)

        self.lblStatus.setText("Copying textures ...")
        print("Copying textures ...")
        #copyDirectory(g_texturesPath, destexpath)

        self.lblStatus.setText("Setting relative path to textures ...")
        print("Setting relative path to textures ...")
        # Set to Relative path
        filenames = mc.ls(type="file")
        for f in filenames:
            attrib = "%s.fileTextureName" %f
            oldpath = mc.getAttr(attrib)
            #print oldpath
            sub_path = oldpath.split("sourceimages",1)[1] 
            #print sub_path
            new_path = "sourceimages" + sub_path
            print new_path
            mc.setAttr(attrib, new_path, type="string")


        self.lblStatus.setText("Saving scene file ...")
        print("Saving scene file ...")
        # Save the file as .ma
        file_name = self.settingsPnl.txtScene.text() + ".ma"
        mc.file( rename=file_name )
        mc.file( save=True, type='mayaAscii')

        # Output zip filepath 
        output_zipfname = maya_dir + ".zip"  #'D:/test/copy/test.zip'

        self.lblStatus.setText("Creating zip file ...") 
        print("Creating zip file ...") 
        make_zipfile(output_zipfname, maya_dir)

        self.lblStatus.setText("File ready for render farm.")
        print("File ready for render farm.")


"""
    Main program invocation happens here
"""
if __name__ == '__main__':
    print "Loading Tool"
    win = RenderFarmTool(getMainWindow())