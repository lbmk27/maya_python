import nuke
import json
import os
import sys


def readJSON(filePath):
    """
    Reads the main JSON file to fetch renderLayers and passes for each layer
    :param filePath:
    :return: None
    """
    returnedData = {}
    try:
        with open(filePath) as dataFile:
            data = json.load(dataFile)
            returnedData = data

        output = parseJSON(returnedData)
        return output

    except:
        print 'Error loading file at path ' + filePath + ":" + sys.exc_info()[0]


def parseJSON(data):
    """
    Parses JSON for nodes with just collections and collections with aovCollection
    :param data:
    :return: collection of layerPasses dictionary
    """
    renderLayers = {}
    layerList = []
    nodes = data["renderSetup"]["renderLayers"]
    for node in nodes:
        currentNode = node["renderSetupLayer"]

        layer = {}
        layerPasses = {}
        layerPasses["name"] = currentNode["name"]
        layerPasses["renderedIn"] = ("rs_%s" % currentNode["name"])
        layerPasses["passes"] = []
        for collection in currentNode["collections"]:
            if 'collection' in collection:
                if readCollectionNode(collection) is not None:
                    layerPasses["passes"].append(readCollectionNode(collection))

            if 'aovCollection' in collection:
                if readAOVCollectionNode(collection) is not None:
                    layerPasses["passes"].append(readAOVCollectionNode(collection))

        layer["layer"] = layerPasses
        layerList.append(layer)

    renderLayers = layerList

    return renderLayers


def readCollectionNode(collectionNode):
    """
    If the collection passes has no aovNodeCollection then its just a beauty pass
    :param collectionNode:
    :return:
    """
    pass


def readAOVCollectionNode(aovNode):
    """
    Function to return arnold node names, which is used to extract passes for that layer
    :param aovNode:
    :return: passes dictionary with pass name and the arnold node name used
    """
    passDetails = {}
    aovChildren = aovNode["aovCollection"]["children"]
    passName = ''
    for child in aovChildren:
        if child["aovChildCollection"]["selector"]["arnoldAOVChildSelector"]:
            passDetails["passName"] = child["aovChildCollection"]["selector"]["arnoldAOVChildSelector"][
                "arnoldAOVNodeName"]
            passDetails["renderedIn"] = child["aovChildCollection"]["name"]

    return passDetails


def createReadNode(folderPath, nodeName):
    """
    Method to create Read nodes for every render pass
    :param folderPath: location to folder where the sequence of images are stored
    :param nodeName: name of the node
    :return: NONE
    """
    try:
        for seq in nuke.getFileNameList(folderPath):
            readNode = nuke.createNode('Read')
            readNode.knob('name').setValue(nodeName)
        readNode.knob('file').fromUserText(folderPath + '\\' + seq)
    except:
        print 'Error concatenating string ' + sys.exc_info()[0]


def createNukeNodesFromPasses(layers, dirPath):
    """
    Method to extract pass names and create nuke nodes
    :param layers: layers dictionary which contains all layers and passes
    :param dirPath: location to the folder where .JSON file and render passes are kept
    :return: NONE
    """
    for layer in layers:
        layerFolder = layer["layer"]["renderedIn"]
        try:
            if len(layer["layer"]["passes"]) > 0:
                for currentPass in layer["layer"]["passes"]:
                    passFolder = currentPass["renderedIn"]
                    folderLoc = os.path.abspath(os.path.join(dirPath, layerFolder, passFolder))
                    createReadNode(folderLoc, 'shadowRead')
                    createShadowNodeTree()
            else:
                folderLoc = os.path.abspath(os.path.join(dirPath, layerFolder, "beauty"))
                createReadNode(folderLoc, 'beautyRead')
                createBeautyNodeTree()
        except:
            print 'Error parsing JSON string from ' + layer + ":" + sys.exc_info()[0]


def createBeautyNodeTree():
    """
    This method creates all the necessary nodes needed for a beauty pass.
    This is basically like a preset which is followed in every similar scenario
    :return:
    """
    node = nuke.toNode("beautyRead")
    node['selected'].setValue(True)
    nuke.createNode('EdgeBlur')
    bGrade = nuke.createNode('Grade')
    bGrade.knob('name').setValue('beautyGrade')


def createShadowNodeTree():
    """
    This method creates all the necessary nodes needed for a shadow pass.
    This is basically like a preset which is followed in every similar scenario
    :return:
    """
    node = nuke.toNode("shadowRead")
    node['selected'].setValue(True)
    nuke.createNode('Shuffle')
    nuke.createNode('Grade')
    nuke.createNode('Premult')
    blurNode = nuke.createNode('Blur')
    blurNode.knob('name').setValue('blurNode')

    node['selected'].setValue(False)

    bmNode = nuke.createNode('Blur')
    bmNode.knob('name').setValue('blurMaskGrade')

    nuke.nodes.Merge(name="finalMerge", inputs=[nuke.toNode("blurMaskGrade"), nuke.toNode("beautyGrade")])
    nuke.connectViewer(0, nuke.toNode("finalMerge"))


def generateNukeScript():
    """
    Main initialization of the program starts here.
    Pops up with a Open file dialog to browse the JSON file and then creates all the necessary nodes
    :return:
    """
    fileName = nuke.getFilename("Open JSON file", '*.json')
    if fileName:
        output = readJSON(fileName)

    dirPath = os.path.dirname(os.path.abspath(fileName))

    createNukeNodesFromPasses(output, dirPath)

