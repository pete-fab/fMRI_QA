#!/usr/bin/env python
import config
import bxh
import directory
import shutil
import qa2csv
import plot_data

def main():

    if config.IS_DEBUG:
        slice_range = config.SLICE_RANGE_DEBUG
        rootDir = directory.sanitizePath(config.DEBUG_DIR)
        atrribute_list = config.ATTRIBUTE_LIST_DEBUG
    else:
        slice_range = config.SLICE_RANGE
        rootDir = directory.sanitizePath(config.DATA_DIR)
        atrribute_list = config.ATTRIBUTE_LIST

    # directory.decompress(rootDir)
    # dateFolderPaths = directory.getChildrenPaths(rootDir)
    # for dateFolderPath in dateFolderPaths:
    #     dataPaths = directory.getChildrenPaths(dateFolderPath)
    #     dataPaths = sanitizeDataFolders(dataPaths)
    #     analysisPath = directory.joinPath([dateFolderPath, bxh.ANALYSIS_FOLDER])
    #     directory.createPath(analysisPath)
    #     for dataPath in dataPaths:
    #         bxh.wrapEPIdata(dataPath, analysisPath)
    #         bxh.analyzeSlices(analysisPath, slice_range)
    #         qa2csv.localSummary(analysisPath, atrribute_list, config.LOCAL_SUMMARY_FILE)
    #
    # qa2csv.globalSummary(rootDir, atrribute_list, config.GLOBAL_SUMMARY_FILE)

    data = qa2csv.readCSV(directory.joinPath([rootDir, config.GLOBAL_SUMMARY_FILE]))
    plot_data.plot_QA(data)
    # directory.compress(rootDir)


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