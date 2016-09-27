#!/usr/bin/env python
import config
import bxh
import directory
import shutil
import qa_csv
import plot_data
import my_logger as l
import hashfile


def main():
    al = l.AllLogger()
    rl = l.RuntimeLogger()
    rl.info(config.RUNTIME_START)
    if config.IS_DEBUG:
        slice_range = config.SLICE_RANGE_DEBUG
        rootDir = directory.sanitizePath(config.DEBUG_DIR)
        atrribute_list = config.ATTRIBUTE_LIST_DEBUG
    else:
        slice_range = config.SLICE_RANGE
        rootDir = directory.sanitizePath(config.DATA_DIR)
        atrribute_list = config.ATTRIBUTE_LIST


    directory.decompress(rootDir)
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

    qa_csv.save_global_summary(rootDir, atrribute_list, config.GLOBAL_SUMMARY_FILE)

    data = qa_csv.read_csv(directory.joinPath([rootDir, config.GLOBAL_SUMMARY_FILE]))
    plot_data.plot_QA(data, config.PLOTS)
    directory.compress(rootDir)

    # finish and has the runtime log
    rl.info(config.RUNTIME_STOP)
    hashfile.save(rl.get_log_file_path())


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
            print path + " contains non DICOM files!!"
            raise TypeError
    return pathList


if __name__ == "__main__":
    main()
