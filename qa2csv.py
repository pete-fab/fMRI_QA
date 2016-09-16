#!/usr/bin/env python

import csv
import xml.etree.ElementTree as ET
from StringIO import StringIO
import os
import directory
import bxh

def getAttributeValue(statsNode, attributeName):
    for child in statsNode.findall("./observation[@name='" + attributeName + "']"):
        return child.text


def saveCsv(filePath, dataSet, keySet):
    with open(filePath, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(keySet)
        for i in range(0, len(dataSet)):
            writer.writerow(dataSet[i])


def checkIfDirExists(Dir):
    if not os.path.isdir(Dir):
        raise ValueError(" THe given QA results directory does not exist.")


def readSummary(filePath, attributeList):
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
    for i, val in enumerate(attributeList):
        data.append(getAttributeValue(stats, val))

    return data

def addSeriesAttributes(attributeList):
    finalAttributeList = list(attributeList)
    finalAttributeList.insert(0, 'resultsFolder')
    finalAttributeList.insert(0, 'sliceIndex')
    finalAttributeList.insert(0, 'seriesIndex')
    return finalAttributeList

def getDataList(workingDir, attributeList):
    pathList = directory.getChildrenPaths(workingDir)
    dataList = []

    for i, currentPath in enumerate(pathList):
        data = readSummary(directory.joinPath([currentPath, 'summaryQA.xml']), attributeList)
        data.insert(0, currentPath)
        sliceIndex = directory.getNameFromPath(currentPath).replace(bxh.SLICE_ROOT, '')
        data.insert(0, sliceIndex)
        data.insert(0, directory.getNameFromPath(workingDir,-2))
        dataList.append(data)

    return dataList

def localSummary(workingDir, attributeList, local_summary_file):
    finalAttributeList = addSeriesAttributes(attributeList)
    dataList = getDataList(workingDir, attributeList)
    saveCsv(directory.joinPath([workingDir, local_summary_file]), dataList, finalAttributeList)


def globalSummary(workingDir, attributeList, file_name):
    finalAttributeList = addSeriesAttributes(attributeList)
    pathList = directory.getChildrenPaths(workingDir)
    dataList = []

    # assuming path structure workingDIR/QAdate/bxh.ANALYSIS_FOLDER
    for currentPath in pathList:
        data = getDataList(directory.joinPath([currentPath, bxh.ANALYSIS_FOLDER]), attributeList)
        dataList.extend(data)

    saveCsv(directory.joinPath([workingDir, file_name]), dataList, finalAttributeList)

def readCSV(file_path):
    if not directory.isFile(file_path):
        raise NameError('File '+ file_path +' does not exist and cannot be read by readCSV.')
    column_names = []
    data = {}
    with open(file_path, 'rb') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=',')
        isHeaderRow = True
        for row in csv_reader:
            if isHeaderRow == False:
                for i, val in enumerate(column_names):
                    data[val].append(row[val])
            else:
                column_names = row
                for i, val in enumerate(column_names):
                    data[val] = [row[val]]
                isHeaderRow = False
    return data

