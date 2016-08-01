#!/usr/bin/env python


import bxh
import directory
import shutil
import qa2csv

def main():
    rootDir = directory.sanitizePath('/media/sf_MAGAZYN/Data/QA/QA_fMRI_data/')

    directory.decompress(rootDir)
    dateFolderPaths = directory.getChildrenPaths(rootDir)
    for dateFolderPath in dateFolderPaths:
        dataPaths = directory.getChildrenPaths(dateFolderPath)
        dataPaths = sanitizeDataFolders(dataPaths)
        analysisPath = directory.joinPath([dateFolderPath, bxh.ANALYSIS_FOLDER])
        directory.createPath(analysisPath)
        for dataPath in dataPaths:
            bxh.wrapEPIdata(dataPath, analysisPath)
            bxh.analyzeSlices(analysisPath)
            qa2csv.localSummary(analysisPath, qa2csv.ATTRIBUTE_LIST)

    qa2csv.globalSummary(rootDir, qa2csv.ATTRIBUTE_LIST)
    directory.compress(rootDir)


def sanitizeDataFolders(pathList):
    for idx, path in enumerate(pathList):
        if not directory.isDir(path):
            pathList.pop(idx)
            continue
        # This is to save space on HD, surplus like localizers should be removed
        if directory.getNameFromPath(path) != 'FBIRN_EPI':
            if directory.getNameFromPath(path) != 'ANALYSIS':
                shutil.rmtree(path)
            pathList.pop(idx)
            continue
        if not directory.isContentsDICOM(path):
            print path+" contains non DICOM files!!"
            raise TypeError
    return pathList


if __name__ == "__main__":
    main()