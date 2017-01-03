#!/usr/bin/env python
import shutil
import sys

import bxh
import config
import directory
import hashfile
import my_logger as l
import plot_data
import qa_csv
import raw_data


def main():
    al = l.AllLogger()
    rl = l.RuntimeLogger()
    rl.info(config.RUNTIME_START)
    if config.IS_DEBUG:
        slice_range = config.SLICE_RANGE_DEBUG
        rootDir = directory.sanitizePath(config.DEBUG_DIR)
        atrribute_list = config.ATTRIBUTE_LIST
    else:
        slice_range = config.SLICE_RANGE
        rootDir = directory.sanitizePath(config.DATA_DIR)
        atrribute_list = config.ATTRIBUTE_LIST
    pacsDir = config.PACS_DIR

    raw_data.RawData(rootDir, pacsDir, directory.joinPath([config.DEBUG_DIR, config.GLOBAL_SUMMARY_FILE]),
                   atrribute_list)

    dateFolderPaths = directory.getChildrenPaths(rootDir)

    for dateFolderPath in dateFolderPaths:
        dataPaths = directory.getChildrenPaths(dateFolderPath)
        dataPaths = sanitizeDataFolders(dataPaths)
        analysisPath = directory.joinPath([dateFolderPath, bxh.ANALYSIS_FOLDER])
        directory.createPath(analysisPath)
        for dataPath in dataPaths:
            bxh.wrapEPIdata(dataPath, analysisPath)
            bxh.analyzeSlices(analysisPath, slice_range)
            qa_csv.save_local_summary(analysisPath, atrribute_list, config.LOCAL_SUMMARY_FILE)

    file_paths = directory.getFilePaths(rootDir, ".gz")
    for filePath in file_paths:
        directory.decompress(filePath)
    qa_csv.save_global_summary(rootDir, atrribute_list, config.GLOBAL_SUMMARY_FILE)

    data = qa_csv.read_csv(directory.joinPath([rootDir, config.GLOBAL_SUMMARY_FILE]))
    plot_data.plot_QA(data, config.PLOTS)

    folderPaths = directory.getChildrenPaths(rootDir)
    for folderPath in folderPaths:
        directory.compress(folderPath)

    # finish and has the runtime log
    rl.info(config.RUNTIME_STOP)
    hashfile.save(rl.get_log_file_path())


def sanitizeDataFolders(pathList):
    for idx, path in enumerate(pathList):
        if not directory.isDir(path):
            pathList.pop(idx)
            continue
        # This is to save space on HD, surplus like localizers should be removed
        if directory.getNameFromPath(path) != config.DATA_SERIESDESCRIPTION:
            if directory.getNameFromPath(path) != bxh.ANALYSIS_FOLDER:
                shutil.rmtree(path)
            pathList.pop(idx)
            continue
        if not directory.isContentsDICOM(path):
            print path + " contains non DICOM files!!"
            raise TypeError
    return pathList


if __name__ == "__main__":
    main()
