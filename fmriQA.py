#!/usr/bin/env python


import subprocess
import os

def wrapEPIdata(workingDir):

    subprocess.Popen('dicom2bxh --xcede *.IMA ../WRAPPED.bxh', cwd=workingDir, shell=True)

    for zslice in xrange(3, 30, 20):
        command = ['fmriqa_phantomqa.pl', '--zselect', str(zslice), '../WRAPPED.bxh',
                   workingDir + 'QA_z' + str(zslice)]
        command = ' '.join(command)
        subprocess.call(command, cwd=workingDir, shell=True)

def sanitizePath(pathDir):
    pathDir = pathDir.split('/')
    pathDir = os.path.sep.join(pathDir)
    pathDir = pathDir.split('\\')
    return os.path.sep.join(pathDir)

def createPath(stringList):
    return os.path.sep.join(stringList)

def main():
    x = sanitizePath('/media/sf_MAGAZYN\Data/QA/20160302')
    print x
    print "ajaja"


if __name__ == "__main__":
    main()