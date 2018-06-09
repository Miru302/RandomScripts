# by Ayan Azimkulov "Miru302"
import maya.cmds as cmds
import maya.mel as mel


# Global Vars
# blendShapeNodeName should be the blendshape node that gets the final inputs to drive face blendshapes.
blendShapeNodeName = "BSName"
suffixName = "_" + "MLLsubject"
rootName = "face" + suffixName

AdditionalBSNames = []


def GetCamera():
    cameras = cmds.ls(cameras=True, long=0)
    defaultCameras = [u'frontShape', u'perspShape', u'sideShape', u'topShape']

    for d in defaultCameras:
        cameras.remove(d)

    for d in cameras:
        if "RIG" in str(cmds.ls(d, long=1)):
            cameras.remove(d)
            continue

    if len(cameras) == 1:
        return cameras[0]
    elif len(cameras) == 0:
        print "No custom Camera found"
        return "perspShape"
    else:
        print "More than one custom cameras"
        return cameras[0]


def findBlendshapeNode():
    for each in cmds.ls(type="blendShape"):
        # check if QSJ2 bs node in the scene:
        for qsj2_bs_node_name in AdditionalBSNames:
            if qsj2_bs_node_name in each:
                return each

        # check if QSJ1 bs node in the scene:
        if blendShapeNodeName in each:
            if "proxy" not in each:
                return each


def getListBlendShapeNodes():
    cmds.ls(type="blendShape")


# get names of blendshape weights that have animCurveUU attached to it:
def getBlendShapesWeightNames(targetBlendShapeNode):
    weights = []
    l_connections = cmds.listConnections(targetBlendShapeNode, connections=1, destination=0, type="animCurveUU")
    if not l_connections:  # in FBX animations, weights are connected to TU animCurves
        l_connections = cmds.listConnections(targetBlendShapeNode, connections=1, destination=0, type="animCurveTU")
    for weight in l_connections:
        if "." in weight:
            weights.append(weight.split(".")[1])
    return weights


def createAndGetBones(weightNames):
    cmds.select(cl=1)
    joints = []
    joints.append(cmds.joint(name=rootName))
    joints.append(cmds.joint(name="camParam" + suffixName))  # a bone for Camera Parameters stream
    for num in range(len(weightNames)):
        cmds.select(rootName)
        joints.append(cmds.joint(name=weightNames[num] + suffixName))
    return joints


def connectBlendShapesToControlNodes(targetBlendShapeNode, controlNodes):
    for controlNode in controlNodes:
        if controlNode == rootName or controlNode == "camParam" + suffixName:
            continue
        sourceAttr = targetBlendShapeNode + "." + controlNode.rsplit(suffixName, 1)[0]
        targetAttr = controlNode + ".translateY"
        cmds.connectAttr(sourceAttr, targetAttr)


def linkCamera(currentCamera):
    cmds.connectAttr(currentCamera + ".focalLength", "camParam" + suffixName + ".translateY")


def skinCube():
    cmds.polyCube(n="faceBlendCube" + suffixName)
    cmds.select(rootName, add=True)
    cmds.skinCluster()


def linkMayaLiveLink(controlNodes):
    cmds.select(rootName)
    cmds.LiveLinkAddSubject("face")
    cmds.select("export_Hips")
    cmds.LiveLinkAddSubject("body")
    mel.eval("MayaLiveLinkUI")

# -------------------main------------------- #


def main():
    blendShapeNodeName = findBlendshapeNode()  # getting blendshape node for expressions
    if not blendShapeNodeName:
        return

    weightNames = getBlendShapesWeightNames(blendShapeNodeName)
    controlNodes = createAndGetBones(weightNames)
    connectBlendShapesToControlNodes(blendShapeNodeName, controlNodes)
    skinCube()
    currentCamera = GetCamera()  # getting custom camera, or if there is no any then default Perspective Camera
    linkCamera(currentCamera)
    linkMayaLiveLink(controlNodes)

    print "Done!"


if __name__ == '__main__':
    main()
