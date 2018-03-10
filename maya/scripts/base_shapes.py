import maya.cmds as mc


def make_shape(type, name, divisions):
    """
    Creates shape based on argument passed

    Args:
        type: {cube, cone, cylinder, plane, torus, sphere}
        name: name of the object
        divisions: number of subdivisions we want to apply in x,y and z axis.
                   Same value will be taken in all axis.
    Return:
        None
    """

    if type == 'cube':
        mc.polyCube(n=name, sx=divisions, sy=divisions, sz=divisions)
    elif type == 'cone':
        mc.polyCone(n=name, sx=divisions, sy=divisions, sz=divisions)
    elif type == 'cylinder':
        mc.polyCylinder(n=name, sx=divisions, sy=divisions, sz=divisions)
    elif type == 'plane':
        mc.polyPlane(n=name, sx=divisions, sy=divisions)
    elif type == 'torus':
        mc.polyTorus(n=name, sx=divisions, sy=divisions)
    elif type == 'sphere':
        mc.polySphere(n=name, sx=divisions, sy=divisions)
    else:
        mc.polySphere()