#!/usr/bin/env python

import os, sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import directory
import argparse
import dicom
import my_logger as l


def main():
    parser = argparse.ArgumentParser(description='This program copies selected Physiology files files from one directory to another',
                                     prog='DICOM filter copy at MCB, UJ',
                                     usage='python copy_physio_files.py -input /some/path -output /other/path -date 20200917 -project ReferringPhysicianName',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-input', help='Path to folder with folders and files', required = True)
    parser.add_argument('-output', help='Output path', required = True)
    parser.add_argument('-project', help='Set ReferringPhysicianName (project) which will be used to filter data')
    parser.add_argument('-max_age', help='Set maximum participant age', default = 2000)
    
    args = parser.parse_args()
    correct_project = args.project
    threshold_year = int(today.strftime("%Y")) - int(args.max_age)

    if(not directory.isDir(args.input)):
        raise Exception("input directory does not exist. Provided: " + str(args.input))

    directory.createPath(args.output)
    logs_path = directory.joinPath([args.output,"sync_logs"])
    directory.createPath(logs_path)
    rl = l.RuntimeLogger(logs_path)
     
    rl.info(" Initial parameter provided: " + str(args))
    rl.info(" Copying dicoms from " + args.input + " to " + args.output)

    # search and process files
    all_folder_paths = directory.getAllDescendants(args.input)
    
    physio_paths = filter(lambda item: "PHYSIOLOG" in directory.getNameFromPath(item), all_folder_paths)
    
    rl.info(" Physio folders found " + " : " + str(physio_paths))
    file_paths = []
    for physio_path in physio_paths:
        file_paths += directory.getFilePaths(physio_path,".IMA")

    dicom_paths = filter(lambda item: directory.isDICOM(item), file_paths)
    rl.info(" Found total of " + str(len(dicom_paths)) + " dicom paths")
    dicom_infos = map(lambda item: get_dicom_info(item), dicom_paths) 
    filtered_file_items = filter(lambda item: does_meet_criteria(item, correct_project, threshold_year, "physio"), dicom_infos)
    filtered_subjects_set = set()
    filter(lambda item: filtered_subjects_set.add(item["subject"]), filtered_file_items)
    rl.info(" " + str(len(filtered_file_items)) + " files meets filtering criteria")
    rl.info(" Found these subject_ids: " + str((list(filtered_subjects_set))))
    copied_file_paths = map(lambda item: copy_files(item, args.output), filtered_file_items)
    print(copied_file_paths)
    rl.info(" Copied these subject_ids: " + str((list(filtered_subjects_set))))

    # report the results to logger
    if (len(copied_file_paths) > 0):
        rl.info(" For example, file " + copied_file_paths[0]["path"] + " is copied to " + copied_file_paths[0]["destination"] )
    rl.info(" Copied: " + str(len(copied_file_paths)) + " files")
    files_not_meeting_criteria = filter(lambda item: not does_meet_criteria(item, correct_project, threshold_year), dicom_infos)
    if (len(files_not_meeting_criteria) > 0):
        rl.info(" Number of files omitted for not meeting criteria: " + str(len(files_not_meeting_criteria)))
        rl.info("Example of files omitted for not meeting criteria: " + str(files_not_meeting_criteria[0:3]).replace("},","},\n"))
    with open(rl.get_path(), 'r') as fin:
        print(fin.read())


def does_meet_criteria(info_dict, correct_project, threshold_year, image_type):
    if info_dict["type"] != image_type:
        return False

    if info_dict["project"] == correct_project:
        return True

    if info_dict["project"] == "NotSet ReferringPhysicianName" or info_dict["project"] is None or info_dict["project"] == "":
        if info_dict["birth_year"] >= threshold_year:
            return True

    return False


def get_dicom_info(dicom_path):
    dicom_info = dicom.read_file(dicom_path)
    birth_date = get_dicom_property(dicom_info,"PatientBirthDate")
    birth_year = int(birth_date[:4])

    image_type = "regular"
    if 'PHYSIO' in get_dicom_property(dicom_info, "ImageType"):
        image_type = "physio"

    
    info = {
        "path": dicom_path,
        "project": get_dicom_property(dicom_info, "ReferringPhysicianName"),
        "project2": get_dicom_property(dicom_info, "StudyDescription"),
        "subject": get_dicom_property(dicom_info, "PatientID"),
        "series": get_dicom_property(dicom_info, "SeriesDescription"),
        "type": image_type,
        "birth_year": birth_year,
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
    subject_prepared = dicom_info["subject"].replace("-","")
    subject_prepared = subject_prepared.replace("_","")
    subject_prepared = ''.join(subject_prepared.split())
    destination_dir = directory.joinPath([
        output_path, 
        dicom_info["project"], 
        subject_prepared, 
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
