##################################################################
#                COPYTING ENTIRE FOLDER WORKING CODE             #
##################################################################

import shutil
import errno
 
def copyDirectory(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)
            

srcpath = 'D:/test/ball'
# Test directory shouldn't exists
despath = 'D:/test/copy/test'

print("copying....")
copyDirectory(srcpath, despath)
print("Done copying")

