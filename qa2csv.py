#!/usr/bin/env python

import csv
import xml.etree.ElementTree as ET
from StringIO import StringIO
import os
import directory
import bxh

ATTRIBUTE_LIST = ['percentFluc', 'drift', 'driftfit',
                 'mean', 'SNR', 'SFNR',
                 'rdc',
                 'minFWHMX', 'meanFWHMX', 'maxFWHMX',
                 'minFWHMY', 'meanFWHMY', 'maxFWHMY',
                 'minFWHMZ', 'meanFWHMZ', 'maxFWHMZ',
                 'dispCMassX', 'driftCMassX', 'dispCMassY',
                 'driftCMassY', 'dispCMassZ', 'driftCMassZ',
                 'meanGhost', 'meanBrightGhost']


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

def localSummary(workingDir, attributeList):
    finalAttributeList = addSeriesAttributes(attributeList)
    dataList = getDataList(workingDir, attributeList)
    saveCsv(directory.joinPath([workingDir, 'local_summary.csv']), dataList, finalAttributeList)


def globalSummary(workingDir, attributeList):
    finalAttributeList = addSeriesAttributes(attributeList)
    pathList = directory.getChildrenPaths(workingDir)
    dataList = []

    # assuming path structure workingDIR/QAdate/bxh.ANALYSIS_FOLDER
    for currentPath in pathList:
        data = getDataList(directory.joinPath([currentPath, bxh.ANALYSIS_FOLDER]), attributeList)
        dataList.extend(data)

    saveCsv(directory.joinPath([workingDir, 'global_summary.csv']), dataList, finalAttributeList)