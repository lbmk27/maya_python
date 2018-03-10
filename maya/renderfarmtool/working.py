##################################################################
#      CREATE PROJECT, WORKSPACE, IMPORT REFERENCES, SAVE        #
##################################################################

import maya.cmds as mc
import maya.mel as mel

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

        
# Set directory path
maya_dir = 'D:/test/ball'

# Create project structure
create_folder( maya_dir )

mel.eval('setProject \"' + maya_dir + '\"')

print("creating project and workspace....")
# Create folder structure
for file_rule in mc.workspace(query=True, fileRuleList=True):
    file_rule_dir = mc.workspace(fileRuleEntry=file_rule)
    maya_file_rule_dir = os.path.join( maya_dir, file_rule_dir)
    create_folder( maya_file_rule_dir )

# Import the references into maya file before saving
import_references()

# Save the file as .ma
mc.file( rename='shot_001.ma' )
mc.file( save=True, type='mayaAscii')

