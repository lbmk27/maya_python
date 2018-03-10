##################################################################
#                   SETTING RELATIVE PATH - WORKING              #
##################################################################

filenames = cmds.ls(type="file")

for f in filenames:
    attrib = "%s.fileTextureName" %f
    oldpath = cmds.getAttr(attrib)
    #print oldpath
    sub_path = oldpath.split("sourceimages",1)[1] 
    #print sub_path
    new_path = "sourceimages" + sub_path
    print new_path
    cmds.setAttr(attrib, new_path, type="string")





## To set path for shotgun maya file

filenames = cmds.ls(type="file")

for f in filenames:
    attrib = "%s.fileTextureName" %f
    oldpath = cmds.getAttr(attrib)
    #print "old path:" + oldpath
    sub_path = oldpath.split("sourceimages", 1)[1] 
    #print "sub path: " + sub_path
    new_path = "R:/Hand-ins/MDDN541/TOM/MAYA/TEXTURES" + sub_path
    print "new path: " + new_path
    cmds.setAttr(attrib, new_path, type="string")