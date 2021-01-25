#!/usr/bin/env python

import datetime as dt
import os, sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import directory
import argparse
import dicom
import my_logger as l


def main():
    today = dt.date.today()
    date_pacs_format = today.strftime("%Y%m%d")
    parser = argparse.ArgumentParser(description='This program copies selected DICOM files from one directory to another',
                                     prog='DICOM filter copy at MCB, UJ',
                                     usage='python filter_copy.py -input /some/path -output /other/path -date 20200917 -project ReferringPhysicianName',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-input', help='Path to folder with folders and files', required=True)
    parser.add_argument('-output', help='Output path', required=True)
    parser.add_argument('-date', help='Search files created on date (YYMMDD); Default is current date', default=date_pacs_format)
    parser.add_argument('-project', help='Set ReferringPhysicianName (project) which will be used to filter data')
    
    args = parser.parse_args()
    correct_project = args.project

    if(not directory.isDir(args.input)):
        raise Exception("input directory does not exist. Provided: " + str(args.input))

    directory.createPath(args.output)
    rl = l.RuntimeLogger(args.output)
    input_date_path = directory.joinPath([args.input, args.date])
    
    rl.info(" Initial parameter provided: " + str(args))
    rl.info(" Copying dicoms from " + input_date_path + " to " + args.output)

    # search and process files
    series_data_paths = directory.getChildrenPaths(input_date_path)
    rl.info(" Series found for date " + args.date + " : " + str(series_data_paths))
    file_paths = []
    for series_data_path in series_data_paths:
        file_paths += directory.getFilePaths(series_data_path,".dcm")

    dicom_paths = filter(lambda item: directory.isDICOM(item), file_paths)
    rl.info(" Found total of " + str(len(dicom_paths)) + " dicom paths")
    dicom_infos = map(lambda item: get_dicom_info(item), dicom_paths) 
    filtered_file_paths = filter(lambda item: item["project"] == correct_project, dicom_infos)
    rl.info(" " + str(len(filtered_file_paths)) + " files meets filtering criteria")
    copied_file_paths = map(lambda item: copy_files(item, args.output), filtered_file_paths)

    # report the results to logger
    if (len(copied_file_paths) > 0):
        rl.info(" For example, file " + copied_file_paths[0]["path"] + " is copied to " + copied_file_paths[0]["destination"] )
    rl.info(" Copied: " + str(len(copied_file_paths)) + " files")
    not_this_project_files = filter(lambda item: item["project"] != correct_project, dicom_infos)
    if (len(not_this_project_files) > 0):
        rl.info(" Files omitted as classified to different project: " + str(not_this_project_files))
    with open(rl.get_path(), 'r') as fin:
        print(fin.read())


def get_dicom_info(dicom_path):
    dicom_info = dicom.read_file(dicom_path)
    info = {
        "path": dicom_path,
        "project": get_dicom_property(dicom_info, "ReferringPhysicianName"),
        "project2": get_dicom_property(dicom_info, "StudyDescription"),
        "subject": get_dicom_property(dicom_info, "PatientID"),
        "series": get_dicom_property(dicom_info, "SeriesDescription"),
    }
    return info


def get_dicom_property(dicom_info, dicom_property, alternative_property = None):
    if (dicom_property in dicom_info):
        return dicom_info.data_element(dicom_property).value 
    else:
        if(alternative_property in dicom_info):
            return dicom_info.data_element(alternative_property).value 
        return "NotSet " + dicom_property


def copy_files(dicom_info, output_path):
    destination_dir = directory.joinPath([
        output_path, 
        dicom_info["project"], 
        dicom_info["subject"], 
        dicom_info["series"],
        ])
    directory.createPath(destination_dir)
    destination_path = directory.joinPath([
        destination_dir,
        directory.getFileName(dicom_info["path"])
    ])
    dicom_info["destination"] = destination_path
    directory.copy_file(dicom_info["path"], destination_path)
    return dicom_info


if __name__ == "__main__":
    main()
