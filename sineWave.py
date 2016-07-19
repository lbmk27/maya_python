import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math

kPluginNodeTypeName = "sineNode"
kPluginNodeId = OpenMaya.MTypeId(0X81048)

class sineNode(OpenMayaMPx.MPxNode):
    aInput = OpenMaya.MObject()
    aAmplitude = OpenMaya.MObject()
    aFrequency = OpenMaya.MObject()
    aOffset = OpenMaya.MObject()
    aOutput = OpenMaya.MObject()

    def __init__(self):
        #print("> sineNode.__init__")
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, block):
        #print("> compute")
        
        inputValue = block.inputValue(sineNode.aInput).asFloat()
        amplitude = block.inputValue(sineNode.aAmplitude).asFloat()
        frequency = block.inputValue(sineNode.aFrequency).asFloat()
        offset = block.inputValue(sineNode.aOffset).asFloat()
        outputData = block.outputValue(sineNode.aOutput)

        result = math.sin(inputValue * frequency) * amplitude + offset
        outputData.setFloat(result)
        
        block.setClean(plug)

        return OpenMaya.MStatus.kSuccess

def nodeCreator():
    #print("> nodeCreator")
    return OpenMayaMPx.asMPxPtr(sineNode())

def nodeInitializer():
    #print("> nodeInitializer")
    
    nAttr = OpenMaya.MFnNumericAttribute()
    sineNode.aInput = nAttr.create("input", "in", OpenMaya.MFnNumericData.kFloat, 1)
    nAttr.setSoftMin(-10)
    nAttr.setSoftMax(10)

    sineNode.aAmplitude = nAttr.create("amplitude", "amp", OpenMaya.MFnNumericData.kFloat, 1)
    nAttr.setSoftMin(-10)
    nAttr.setSoftMax(10)

    sineNode.aFrequency = nAttr.create("frequency", "freq", OpenMaya.MFnNumericData.kFloat, 1)
    nAttr.setSoftMin(0)
    nAttr.setSoftMax(5)

    sineNode.aOffset = nAttr.create("offset", "ofs", OpenMaya.MFnNumericData.kFloat, 0)
    nAttr.setSoftMin(-10)
    nAttr.setSoftMax(10)

    sineNode.aOutput = nAttr.create("output", "out", OpenMaya.MFnNumericData.kFloat)
    nAttr.setWritable(False)

    sineNode.addAttribute(sineNode.aInput)
    sineNode.addAttribute(sineNode.aAmplitude)
    sineNode.addAttribute(sineNode.aFrequency)
    sineNode.addAttribute(sineNode.aOffset)
    sineNode.addAttribute(sineNode.aOutput)

    sineNode.attributeAffects(sineNode.aInput, sineNode.aOutput)
    sineNode.attributeAffects(sineNode.aAmplitude, sineNode.aOutput)
    sineNode.attributeAffects(sineNode.aFrequency, sineNode.aOutput)
    sineNode.attributeAffects(sineNode.aOffset, sineNode.aOutput)

def initializePlugin(mobject):
    #print("> initializePlugin")
    fnPlugin = OpenMayaMPx.MFnPlugin(mobject)
    fn.Plugin.registerNode(kPluginNodeTypeName, kPluginNodeId, nodeCreator, 
                        nodeInitializer, OpenMayaMPx.MPxNode.kDependNode)

def uninitializePlugin(mobject):
    #print("> uninitializePlugin")
    fnPlugin = OpenMayaMPx.MFnPlugin(mobject)
    fn.Plugin.deregisterNode(kPluginNodeId)
