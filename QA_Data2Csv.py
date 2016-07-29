#!/usr/bin/env python
import csv
import xml.etree.ElementTree as ET
from StringIO import StringIO
import sys
import os

def getAttributeValue(statsNode, attributeName):
    for child in statsNode.findall("./observation[@name='"+attributeName+"']"):
        return child.text

def saveCsv(filePath, dataSet, keySet):
    with open(filePath, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(keySet)
	for i in range( 0,len(dataSet) ):
	        writer.writerow(dataSet[i])

def checkIfDirExists(Dir):
    if not os.path.isdir(Dir):
        raise ValueError(" THe given QA results directory does not exist.")

def summary2CSV(filePath,attributeList):
	#read xml
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
	    data.append( getAttributeValue(stats,val) )
	
	return data

Dir = os.path.dirname(os.path.realpath(__file__))+'/'

attributeList = ['percentFluc','drift','driftfit',
	'mean','SNR','SFNR',
	'rdc',
	'minFWHMX','meanFWHMX','maxFWHMX',
	'minFWHMY','meanFWHMY','maxFWHMY',
	'minFWHMZ','meanFWHMZ','maxFWHMZ',
	'dispCMassX','driftCMassX','dispCMassY',
	'driftCMassY','dispCMassZ','driftCMassZ',
	'meanGhost','meanBrightGhost']

finalAttributeList = list(attributeList)
finalAttributeList.insert(0,'resultsFolder')
finalAttributeList.insert(0,'sliceIndex')
finalAttributeList.insert(0,'measurementSeries')
finalAttributeList.insert(0,'seriesIndex')

#Get subdirs
dirList = next(os.walk('.'))[1]

dataList=[]
for i, val in enumerate(dirList):
	currentDir = Dir + val+'/'
	qaSummaryDirList = next(os.walk(currentDir))[1]
	for n, qsVal in enumerate(qaSummaryDirList):
		qsDir = currentDir + qsVal + '/'
		data = summary2CSV(qsDir+'summaryQA.xml',attributeList) 
		data.insert(0,qsVal)
		index = qsVal.replace('QA_z','')
		data.insert(0,index)
		data.insert(0,val)
		index = val.replace('FANTOM_EPI_TEST','')
		data.insert(0,index)
		dataList.append(data)

saveCsv( Dir+'summary.csv',dataList,finalAttributeList)

