import maya.cmds as mc

"""
The below script generates a sphere on every vertex
of the selected mesh.
It is mandatory to select a POLYGONAL mesh before executing
the below script

Args:
    NONE
Return:
    None
"""
    
# Get the selected object
selObjs = mc.ls(sl=True)

# Fetch all the vertices for the selected object
srcVrts = mc.ls('%s.vtx[:]' % selObjs[0], fl=True)

# loop through vertices in mesh vertices list
for vtx in srcVrts:
    # get the position of the vertex in model space
    loc = mc.pointPosition(vtx, l=True)
    # create a sphere with below flags
    sphr = mc.polySphere(sx=8, sy=8, r = 0.1)
    # translate the created sphere to vertex location in space
    mc.setAttr('%s.translateX' % sphr[0], loc[0])
    mc.setAttr('%s.translateY' % sphr[0], loc[1])
    mc.setAttr('%s.translateZ' % sphr[0], loc[2])
