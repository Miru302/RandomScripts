#by Ayan Azimkulov "Miru302"
import maya.cmds as cmds

# This is tool to create Joint for every blendshape weight in blendshape node inside Maya, 
# and link weight value to Y position of the joint,
# Primarily used to transfer Blendshape animations via MayaLiveLink into UnrealEngine

# Global Vars
# blendShapeNodeName should be the blendshape node that gets the final inputs to drive face blendshapes.
blendShapeNodeName = "head_HIblendshape"
suffixName = "_" + "MLLsubject"
rootName = "face"


def findBlendshapeNode():
    pass


def getListBlendShapeNodes():
    cmds.ls(type="blendShape")


# get names of blendshape weights that have animCurveUU attached to it:
def getBlendShapesWeightNames(targetBlendShapeNode):
    weights = []
    for weight in cmds.listConnections(targetBlendShapeNode, connections=1, destination=0, type="animCurveUU"):
        if "." in weight:
            weights.append(weight.split(".")[1])
    return weights


def createAndGetBones(weightNames):
    cmds.select(cl=1)
    joints = []
    joints.append(cmds.joint(name=rootName))
    for num in range(len(weightNames)):
        cmds.select(rootName)
        joints.append(cmds.joint(name=weightNames[num] + suffixName))
    return joints


def connectBlendShapesToControlNodes(targetBlendShapeNode, controlNodes):
    for controlNode in controlNodes:
        if controlNode == rootName:
            continue
        sourceAttr = targetBlendShapeNode + "." + controlNode.rsplit(suffixName, 1)[0]
        targetAttr = controlNode + ".translateY"
        cmds.connectAttr(sourceAttr, targetAttr)


def skinCube():
    cmds.polyCube(n="faceBlendCube" + suffixName)
    cmds.select(rootName, add=True)
    cmds.skinCluster()


# -------------------main------------------- #
def main():
    weightNames = getBlendShapesWeightNames(blendShapeNodeName)
    controlNodes = createAndGetBones(weightNames)
    connectBlendShapesToControlNodes(blendShapeNodeName, controlNodes)
    skinCube()


if __name__ == '__main__':
    main()
