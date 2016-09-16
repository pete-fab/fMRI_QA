#!/usr/bin/env python

import subprocess
import directory
import sys
import shutil

WRAP_NAME = 'WRAPPED.bxh'
ANALYSIS_FOLDER = 'ANALYSIS'
SLICE_ROOT = 'QA_z'


def wrapEPIdata(dataDir,outputDir):
    dataFolder = directory.getNameFromPath(dataDir)
    # The relative output path is used to get absolute paths in the output
    command = 'dicom2bxh --xcede *.IMA ..'+ directory.SEP + dataFolder + directory.SEP + WRAP_NAME
    p = subprocess.Popen(command, cwd=dataDir, shell=True)
    p.communicate()  # this causes the script to wait until dicom2bxh is finished
    primaryPath = directory.joinPath([dataDir, WRAP_NAME])
    outputPath = directory.joinPath([outputDir, WRAP_NAME])
    try:
        shutil.move(primaryPath, outputPath)
    except:
        print 'Error: moving ' + WRAP_NAME + ' to ' + outputPath + '!! Check what went wrong!!'
        sys.exit(1)


def fmriQaAnalysis(workingDir,sliceNumber):
    sliceFolder = directory.joinPath([workingDir, SLICE_ROOT])
    command = ['fmriqa_phantomqa.pl', '--zselect', str(sliceNumber), ' WRAPPED.bxh', sliceFolder + str(sliceNumber)]
    command = ' '.join(command)
    subprocess.call(command, cwd=workingDir, shell=True)


def analyzeSlices(workingDir,sliceList):
    for zslice in sliceList:
        fmriQaAnalysis(workingDir, zslice)

