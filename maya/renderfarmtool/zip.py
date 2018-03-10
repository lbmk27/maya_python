##################################################################
#                       ZIP FILE WORKING CODE                    #
##################################################################

import os
import zipfile

# Output absolute filepath 
output_filename = 'D:/test/copy/test.zip'

# Path to Maya project folder
source_dir = 'D:/test/copy/test'

def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    #print relroot
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir):
            #print root
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename): # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)
                    

print("creating zip file ....")                    
make_zipfile(output_filename, source_dir)
print("done zipping")
