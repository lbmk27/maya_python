import maya.cmds as mc

class LightRig():

    def __init__(self, keyLight, fillLight, rimLight, rigSettings):
        self.keyLight = keyLight
        self.fillLight = fillLight
        self.rimLight = rimLight
        self.settings = rigSettings

    def createRig(self):
        # Create a Cube for test cases
        mc.polySphere(name='mySphere')
        objCenter = mc.objectCenter('mySphere', l=True)

        # Get the bounding box for the selected ojbject
        rigScaleFactor = 15
        XYZ = mc.xform('a', bb=True, q=True)
        rad = XYZ[3] / 2 * rigScaleFactor

        # Create a circle to place three point lights
        mc.circle(n='curveLights', nr=(0, 1, 0), c=(0, 0, 0), sections=9, radius=rad)

        # Create lights in three positions on the curve
        loc = mc.pointOnCurve('curveLights', pr=0.0, p=True)
        #_item = mc.spotLight(name='FillLight', coneAngle=45)
        _item = self.createLight(self.fillLight, "FillLight")
        mc.move(loc[0], loc[1], loc[2], _item, ls=True)

        loc = mc.pointOnCurve('curveLights', pr=3.0, p=True)
        #_item = mc.spotLight(name='KeyLight', coneAngle=45)
        _item = self.createLight(self.keyLight, "KeyLight")
        mc.move(loc[0], loc[1], loc[2], _item, ls=True)

        loc = mc.pointOnCurve('curveLights', pr=6.0, p=True)
        #_item = mc.spotLight(name='RimLight', coneAngle=45)
        _item = self.createLight(self.rimLight, "RimLight")
        mc.move(loc[0], loc[1], loc[2], _item, ls=True)

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


    def createLight(self, lightObj, name):
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

