#!/usr/bin/env python

import subprocess
def wrapEPIdata(workingDir):

    subprocess.Popen('dicom2bxh --xcede *.IMA ../WRAPPED.bxh', cwd=workingDir, shell=True)

    for zslice in xrange(3, 30, 20):
        command = ['fmriqa_phantomqa.pl', '--zselect', str(zslice), '../WRAPPED.bxh',
                   workingDir + 'QA_z' + str(zslice)]
        command = ' '.join(command)
        subprocess.call(command, cwd=workingDir, shell=True)

