#!/usr/bin/env python

# Author: Piotr Faba, github: pete-fab
# Most recent version available at: https://github.com/pete-fab/fMRI_QA
import shutil
import dicom
import bxh
import config
import directory
import hashfile
import my_logger as l
import plot_data
import qa_csv
import raw_data
import argparse



def multi(sourceDataPath, outputPath, slice_range):
    rl.info(config.RUNTIME_START)
    atrribute_list = config.ATTRIBUTE_LIST
    unprocessed_data_path = directory.joinPath([outputPath, config.SUBDIRS['UNPROCESSED_DATA']])
    directory.createPath(unprocessed_data_path)
    processed_data_path = directory.joinPath([outputPath, config.SUBDIRS['PROCESSED_DATA']])
    directory.createPath(processed_data_path)
    local_summaries_path = directory.joinPath([outputPath, config.SUBDIRS['LOCAL_SUMMARIES']])
    directory.createPath(local_summaries_path)
    xml_path = directory.joinPath([outputPath, config.SUBDIRS['LOCAL_XMLS']])
    directory.createPath(xml_path)

    raw_data.RawData(outputPath, processed_data_path, unprocessed_data_path, xml_path, local_summaries_path, sourceDataPath,
                     directory.joinPath([config.DEBUG_DIR, config.GLOBAL_SUMMARY_FILE]), atrribute_list)

    dateFolderPaths = directory.getChildrenPaths(unprocessed_data_path)

    for dateFolderPath in dateFolderPaths:
        dataPaths = directory.getChildrenPaths(dateFolderPath)
        dataPaths = sanitizeDataFolders(dataPaths)
        analysisPath = directory.joinPath([dateFolderPath, bxh.ANALYSIS_FOLDER])
        date = directory.getNameFromPath(dateFolderPath, -1)
        directory.createPath(analysisPath)
        for dataPath in dataPaths:
            rl.debug("multi() dataPath: " + dataPath)
            bxh.wrapEPIdata(dataPath, analysisPath)
            bxh.analyzeSlices(analysisPath, slice_range)
            loc_summary_path = directory.joinPath([ analysisPath, config.LOCAL_SUMMARY_FILE ])
            copy_loc_summary = directory.joinPath([local_summaries_path, date + config.SUMMARY_EXT])
            qa_csv.save_local_summary(analysisPath, atrribute_list, loc_summary_path, copy_loc_summary, xml_path )
        directory.compress(dateFolderPath, directory.joinPath([processed_data_path,date+directory.ARCHIVE_EXTENSION]))


    qa_csv.save_global_summary(xml_path, atrribute_list, directory.joinPath([outputPath, config.GLOBAL_SUMMARY_FILE]) )

    data = qa_csv.read_csv(directory.joinPath([outputPath, config.GLOBAL_SUMMARY_FILE]))
    rl.debug("data: " + str(data))
    plot_data.plot_QA(data, config.PLOTS, outputPath)

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
            raise TypeError(path + " contains non DICOM files!!")
    return pathList


def verify_is_QA_DICOM(file_path):
    if "DICOMDIR" == directory.getFileName(file_path):
        return False

    if not directory.isDICOM(file_path):
        return False

    dicom_info = dicom.read_file(file_path)
    return is_dicom_dict_QA(dicom_info)


def is_dicom_dict_QA(dicom_info):
    # check if this is QA fMRI series
    if not ("RequestingPhysician" in dicom_info
            and "SeriesDescription" in dicom_info
            and "ReferringPhysicianName" in dicom_info):
        return False

    if not (dicom_info.RequestingPhysician == config.DATA_REQUESTINGPHYSICIAN
            and dicom_info.SeriesDescription == config.DATA_SERIESDESCRIPTION
            and dicom_info.ReferringPhysicianName == config.DATA_REFERRINGPHYSICIANNAME):
        return False

    return True

def single(sourceDataPath, analysisPath, slice_range):
    atrribute_list = config.ATTRIBUTE_LIST
    bxh.wrapEPIdata(sourceDataPath, analysisPath)
    bxh.analyzeSlices(analysisPath, slice_range)
    loc_summary_path = directory.joinPath([analysisPath, config.LOCAL_SUMMARY_FILE])
    qa_csv.save_local_summary_only(analysisPath, atrribute_list, loc_summary_path)


if __name__ == "__main__":
    # parse commandline
    parser = argparse.ArgumentParser(description='This is program executes QA for fMRI',
                                     prog='QA for fMRI at MCB, UJ',
                                     usage='python fmriQA.py -mode ',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-mode', help='Choose "single" or "multi" mode (multi includes graphs)', default='single')
    parser.add_argument('-input', help='Path to folder with single set of EPI data', default=config.SUBDIRS['UNPROCESSED_DATA'])
    parser.add_argument('-output', help='Output path', default=config.SUBDIRS['PROCESSED_DATA'])

    slice_list = ""
    for slice in config.SLICE_RANGE:
        slice_list += str(slice) + ", "
    slice_list = slice_list[0:-2] #remove surplus coma
    parser.add_argument('-slices', help='Slices of measurement to be analysed', default=slice_list)
    args = parser.parse_args()

    if not (args.mode == 'single' or args.mode == 'multi'):
        message = 'The allowed modes are: "single" and "multi". The mode used was: ' + args.mode
        rl.error(message)
        raise ValueError(message)

    if(not directory.isDir(args.input)):
        raise Exception("input directory does not exist")
    
    directory.createPath(args.output)
    # definition of logger singleton
    rl = l.RuntimeLogger(args.output)

    if args.slices != "":
        try:
            slice_list = map(int, args.slices.split(","))
        except:
            message = 'There is an error in the slice list: ' + args.slices
            rl.error(message)
            raise ValueError(message)

    rl.info("Running with slices: " + str(slice_list))

    if args.mode == 'multi':
        multi(args.input, args.output, slice_list)
        exit(0)

    if args.mode == 'single':
        single(args.input, args.output, slice_list)
        exit(0)
    else:
        raise Exception("Invalid mode selected")
