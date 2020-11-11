#!/usr/bin/env python

import subprocess
import directory
import sys
import shutil
import my_logger as l
import config

WRAP_NAME = 'WRAPPED.bxh'
ANALYSIS_FOLDER = 'ANALYSIS'
SLICE_ROOT = 'QA_z'

rl = l.RuntimeLogger()

def wrapEPIdata(dataDir,outputDir):
    dataFolder = directory.getNameFromPath(dataDir)
    rl.info(dataDir)
    # The relative output path is used to get absolute paths in the output
    command = 'dicom2bxh --xcede * ..'+ directory.SEP + dataFolder + directory.SEP + WRAP_NAME
    # command = 'dicom2bxh --xcede *.' + config.DATA_EXT + ' ..' + directory.SEP + dataFolder + directory.SEP + WRAP_NAME
    rl.info('To execute: '+command)
    p = subprocess.Popen(command, cwd=dataDir, shell=True)
    p.communicate()  # this causes the script to wait until dicom2bxh is finished
    rl.info('Done: ' + command)
    primaryPath = directory.joinPath([dataDir, WRAP_NAME])
    outputPath = directory.joinPath([outputDir, WRAP_NAME])
    try:
        shutil.move(primaryPath, outputPath)
    except:
        e_text = 'Error: moving ' + WRAP_NAME + ' to ' + outputPath + '!! Check what went wrong!!'
        print e_text
        rl.error(e_text)
        sys.exit(1)


def fmriQaAnalysis(workingDir,sliceNumber):
    sliceFolder = directory.joinPath([workingDir, SLICE_ROOT])
    command = ['fmriqa_phantomqa.pl', '--zselect', str(sliceNumber), ' WRAPPED.bxh', sliceFolder + str(sliceNumber)]
    command = ' '.join(command)
    rl.info('To execute: ' + command)
    subprocess.call(command, cwd=workingDir, shell=True)
    rl.info('Done: ' + command)


def analyzeSlices(workingDir,sliceList):
    rl.info('To execute bxh slice analysis on : ' + workingDir)
    rl.info('analyzing for slices: ' + str(sliceList))
    for zslice in sliceList:
        fmriQaAnalysis(workingDir, zslice)
    rl.info('Done bxh slice analysis on : ' + workingDir)

