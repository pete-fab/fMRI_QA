#!/usr/bin/env python

import csv
import xml.etree.ElementTree as ET
from StringIO import StringIO
import hashfile
import directory
import bxh


def __get_attribute_value(statsNode, attributeName):
    for child in statsNode.findall("./observation[@name='" + attributeName + "']"):
        return child.text


def save_csv(file_path, data_set, key_set):
    if directory.isFile(file_path):
        directory.delete(file_path)
    with open(file_path, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(key_set)
        for i in range(0, len(data_set)):
            writer.writerow(data_set[i])
    hash = hashfile.save(file_path)

    # save backup file
    try:
        file_name = directory.getFileName(file_path)
        file_directory = directory.getFileDirectory(file_path)
        backup_path = directory.joinPath([file_directory, "." + file_name])
        directory.copy_file(file_path, backup_path)
        hashfile.save(backup_path)
    except:
        print "Failed to create backup csv file"
        raise RuntimeError
    return hash


def __read_analysis_xml(filePath, attributeList):
    # read xml
    with file(filePath) as f:
        xml_string = f.read()

    # strip all namespaces and parse
    it = ET.iterparse(StringIO(xml_string))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
    root = it.root

    # selecting stats node makes search faster
    stats = root[0][1]
    if root[0][1].tag != 'measurementGroup':
        raise ValueError('the XML structure is not valid')

    data = []
    #Add scandate
    temp = __get_attribute_value(stats, "scandate").split('-')
    data.append("".join(temp))
    # Add slice number
    data.append(__get_attribute_value(stats, "slice"))
    # Add file directory
    data.append(directory.getFileDirectory(__get_attribute_value(stats,"diffimagefile")))
    for i, val in enumerate(attributeList):
        data.append(__get_attribute_value(stats, val))

    return data


def __add_series_attributes(attributeList):
    finalAttributeList = list(attributeList)
    finalAttributeList.insert(0, 'resultsFolder')
    finalAttributeList.insert(0, 'sliceIndex')
    finalAttributeList.insert(0, 'seriesIndex')
    return finalAttributeList


def __get_data_list(workingDir, attributeList):
    pathList = directory.getFilePaths(workingDir,'.xml')
    dataList = []

    for i, currentPath in enumerate(pathList):
        data = __read_analysis_xml(currentPath, attributeList)
        # data.insert(0, currentPath)

        # data = __read_analysis_xml(currentPath, attributeList)
        # data.insert(0, currentPath)
        # sliceIndex = directory.getNameFromPath(currentPath).replace(bxh.SLICE_ROOT, '')
        # parts = sliceIndex.split('_')
        # data.insert(0, parts[1])
        # data.insert(0, parts[0])
        dataList.append(data)

    return dataList

def __copy_xmls(workingDir, destinationDir):
    pathList = directory.getChildrenPaths(workingDir)
    dataList = []

    for i, currentPath in enumerate(pathList):
        filePath = directory.joinPath([currentPath, 'summaryQA.xml'])
        sliceIndex = directory.getNameFromPath(currentPath).replace(bxh.SLICE_ROOT, '')
        date = directory.getNameFromPath(workingDir, -2)
        copied_xml_path = directory.joinPath([destinationDir,date+'_'+sliceIndex+'.xml'])
        directory.copy_file(filePath, copied_xml_path)
        hashfile.save(copied_xml_path)


def save_local_summary(workingDir, attributeList, local_summary_file_path, copy_local_summary_path, copy_xml_folder_path):
    finalAttributeList = __add_series_attributes(attributeList)
    pathList = directory.getChildrenPaths(workingDir)
    dataList = []

    for i, currentPath in enumerate(pathList):
        data = __get_data_list(currentPath, attributeList)
        dataList.extend(data)

    save_csv(local_summary_file_path, dataList, finalAttributeList)
    directory.copy_file(local_summary_file_path, copy_local_summary_path)
    hashfile.save(copy_local_summary_path)
    __copy_xmls(workingDir, copy_xml_folder_path)

def save_local_summary_only(workingDir, attributeList, local_summary_file_path):
    finalAttributeList = __add_series_attributes(attributeList)
    pathList = directory.getChildrenPaths(workingDir)
    dataList = []

    for i, currentPath in enumerate(pathList):
        data = __get_data_list(currentPath, attributeList)
        dataList.extend(data)

    save_csv(local_summary_file_path, dataList, finalAttributeList)


def save_global_summary(workingDir, attributeList, file_path):
    finalAttributeList = __add_series_attributes(attributeList)

    # assuming path structure local_summaries/*.xml
    data = __get_data_list(workingDir, attributeList)


    save_csv(file_path, data, finalAttributeList)


def read_csv(file_path):
    if not directory.isFile(file_path):
        raise OSError('File ' + file_path + ' does not exist and cannot be read by readCSV.')
    column_names = []
    data = {}
    with open(file_path, 'rb') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=',')
        isHeaderRow = True
        for row in csv_reader:
            if isHeaderRow == True:
                column_names = row
                for i, val in enumerate(column_names):
                    data[val] = []
            isHeaderRow = False
            for i, val in enumerate(column_names):
                try: # try casting to float
                    data[val].append(float(row[val]))    
                except ValueError:
                    data[val].append(row[val])
    return data

