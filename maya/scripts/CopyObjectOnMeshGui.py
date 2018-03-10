from PySide2 import QtCore, QtWidgets
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

"""
    Generic function to return normals from a mesh,
    not used at the moment in this program
"""
def getNormalsFromMesh(mesh):
    for normal in mc.polyInfo(mesh, fn=True):
        strNormals = normal.partition(": ")[2].split(' ')
        x, y, z = [float(x) for x in strNormals]
        yield (x, y, z)


# for n in getNormalsFromMesh('pSphereShape1'):
#     print n

"""
    Class to create ObjectCloner tool UI
    which allows the user to select an option
    from UI and attached it to the source object
"""
class ObjectCloner(QtWidgets.QMainWindow):
    """
    Constructor to create all associated UI elements
    when the class object is created
    """
    def __init__(self, parent=None):
        parent = parent or getMainWindow()
        super(ObjectCloner, self).__init__(parent)

        # Main Widget
        widget = QtWidgets.QWidget()
        self.mainlayout = QtWidgets.QVBoxLayout(widget)

        # Grid layout to place radio buttons
        self.grid = QtWidgets.QGridLayout()
        self.mainlayout.addLayout(self.grid)
        self.createRButtons()
        self.createAttachButton()
        self.setCentralWidget(widget)
        self.show()
        self.raise_()


    """
    Create Radio buttons

    Returns:
        NONE
    """
    def createRButtons(self):
        self.rbtSp = QtWidgets.QRadioButton("Sphere")
        self.rbtSp.setChecked(True)
        self.rbtCb = QtWidgets.QRadioButton("Cube")
        self.rbtCy = QtWidgets.QRadioButton("Cylinder")
        self.rbtCn = QtWidgets.QRadioButton("Cone")
        self.rbtPl = QtWidgets.QRadioButton("Plane")
        self.rbtTr = QtWidgets.QRadioButton("Torus")
        self.rbtPr = QtWidgets.QRadioButton("Prism")
        self.rbtPy = QtWidgets.QRadioButton("Pyramid")

        self.grid.addWidget(self.rbtSp, 1, 1)
        self.grid.addWidget(self.rbtCb, 1, 2)
        self.grid.addWidget(self.rbtCy, 1, 3)
        self.grid.addWidget(self.rbtCn, 1, 4)
        self.grid.addWidget(self.rbtPl, 2, 1)
        self.grid.addWidget(self.rbtTr, 2, 2)
        self.grid.addWidget(self.rbtPr, 2, 3)
        self.grid.addWidget(self.rbtPy, 2, 4)


    """
    Create Attach Button - this button clones the object on
    every vertex of selected source object

    Returns:
        NONE
    """
    def createAttachButton(self):
        hlayout = QtWidgets.QHBoxLayout()
        verticalSpacer = QtWidgets.QSpacerItem(340, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        hlayout.addItem(verticalSpacer)

        btn = QtWidgets.QPushButton('Attach Object')
        btn.clicked.connect(lambda:self.btn_clicked())
        hlayout.addWidget(btn)

        self.mainlayout.addLayout(hlayout)

    """
        Function to return which UI option is selected
        Parameters:
            NONE
        Returns:
            String of select option
    """
    def getSelectedOption(self):
        if self.rbtSp.isChecked() == True:
            return "Sphere"
        elif self.rbtCb.isChecked() == True:
            return "Cube"
        elif self.rbtCy.isChecked() == True:
            return "Cylinder"
        elif self.rbtCn.isChecked() == True:
            return "Cone"
        elif self.rbtPl.isChecked() == True:
            return "Plane"
        elif self.rbtTr.isChecked() == True:
            return "Torus"
        elif self.rbtPr.isChecked() == True:
            return "Prism"
        elif self.rbtPy.isChecked() == True:
            return "Pyramid"


    """
        Button click event handler - the main functionality of cloning an
        object happens here.
        We first get the every vertex of the selected source object and
        loop through them, and attach the selected option to each
        and every vertex

        Returns:
            NONE
    """
    def btn_clicked(self):
        # Get the selected object
        selObjs = mc.ls(sl=True)

        obj = self.getSelectedOption()

        divisions = 4
        radius=0.1
        width=0.1
        height=0.1
        depth=0.1

        grpName = obj + '_Grp'
        mc.group(em=True, name=grpName)
        # Fetch all the vertices for the selected object
        srcVrts = mc.ls('%s.vtx[:]' % selObjs[0], fl=True)

        # # loop through vertices in mesh vertices list
        for vtx in srcVrts:
            # get the position of the vertex in model space
            loc = mc.pointPosition(vtx, l=True)

            if obj == "Sphere":
                _item = mc.polySphere(sx=9, sy=9, r=radius)
                mc.group(_item[0], parent=grpName)
            elif obj == "Cube":
                _item = mc.polyCube(sx=1, sy=1, sz=1, w=width, h=height, d=depth)
                mc.group(_item[0], parent=grpName)
            elif obj == "Cylinder":
                _item = mc.polyCylinder(radius=radius, sx=9, sy=9, sz=9, h=height)
                mc.group(_item[0], parent=grpName)
            elif obj == "Cone":
                _item = mc.polyCone(sx=9, sy=9, sz=divisions, r=radius, h=height)
                mc.group(_item[0], parent=grpName)
            elif obj == "Plane":
                _item = mc.polyPlane(sx=1, sy=1, w=width, h=height)
                mc.group(_item[0], parent=grpName)
            elif obj == "Torus":
                _item = mc.polyTorus(r=radius, sr=0.125,sx=8, sy=8)
                mc.group(_item[0], parent=grpName)
            elif obj == "Prism":
                _item = mc.polyPrism(l=0.1, ns=3, w=0.1, sc=1, sh=1)
                mc.group(_item[0], parent=grpName)
            elif obj == "Pyramid":
                _item = mc.polyPyramid(sh=0.1, ns=4, sc=0, w=0.1)
                mc.group(_item[0], parent=grpName)

            # translate the created sphere to vertex location in space
            mc.setAttr('%s.translateX' % _item[0], loc[0])
            mc.setAttr('%s.translateY' % _item[0], loc[1])
            mc.setAttr('%s.translateZ' % _item[0], loc[2])

        print("Object attached!" + obj)

"""
    Main program invocation happens here
"""
if __name__ == '__main__':
    win = ObjectCloner(getMainWindow())