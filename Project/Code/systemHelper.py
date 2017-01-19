from __future__ import print_function
import os

def checkOverwrite(dir, conditionType, subjectNumber,  fileType = '.hdf5'):
    '''
    Checks whether a file is in the directory
    If it is in the directory it will ask for changing the subject number
    return the storage filepath
    '''
    # keep checking until file is not in the folder
    while True:
        if os.path.isfile(dir + conditionType + str(subjectNumber) + fileType):
            subjectNumber = raw_input('Please enter a new subject number ')
        else:
            file = dir  + conditionType + str(subjectNumber) + fileType
            break
    print('Storing data in: \n\t ', file)
    return file