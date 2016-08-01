#!/usr/bin/env python
import os
import dicom
import sys
import tarfile
import shutil

SEP = os.path.sep
D_SEP = os.path.sep + os.path.sep


def sanitizePath(pathDir):
    pathDir = pathDir.split('/')
    pathDir = SEP.join(pathDir)
    pathDir = pathDir.split('\\')
    pathDir = SEP.join(pathDir)
    return pathDir.replace(D_SEP, SEP)


def joinPath(stringList):
    path = SEP.join(stringList)
    return sanitizePath(path)


def createPath(pathDir):
    pathDir = sanitizePath(pathDir)
    if isDir(pathDir):
        return False
    os.makedirs(pathDir)
    return True


def delete(pathDir):
    if isFile(pathDir):
        pathDir = sanitizePath(pathDir)
        os.unlink(pathDir)
        return True
    elif isDir(pathDir):
        shutil.rmtree(pathDir)
        return True
    else:
        raise "path or file ("+ pathDir +") given to delete is not existent"


def isDir(pathDir):
    return os.path.isdir(pathDir)


def isFile(path):
    return os.path.isfile(path)


def getChildrenFolders(pathDir):
    return next(os.walk(pathDir))[1]

# Returns immediate sub-folders absolute paths
def getChildrenPaths(pathDir):
    list = getChildrenFolders(pathDir)
    paths = []
    for child in list:
        paths.append(joinPath([pathDir, child]))
    return paths


def getFileNames(pathDir):
    return [x[2] for x in os.walk(pathDir)][0]


def getFilePaths(pathDir):
    list = getFileNames(pathDir)
    paths = []
    for child in list:
        paths.append(joinPath([pathDir, child]))
    return paths


def getAllDescendants(pathDir):
    return [x[0] for x in os.walk(pathDir)]


def getNameFromPath(pathDir,position=-1):
    list = pathDir.split(SEP)
    if len(list) > 0:
        if list[position] != "":
            return list[position]
        else:
            if len(list) > 1:
                return list[position-1]
            else:
                return False
    else:
        return False


def isDICOM(filePath):
    if not isFile(filePath):
        return False

    try:
        ds = dicom.read_file(filePath)
    except dicom.errors.InvalidDicomError:
        return False
    except:
        print 'Undefined error when verifying DICOM file'
        sys.exit(1)
    return True


def isContentsDICOM(pathDir):
    ret = True
    filePaths = getFilePaths(pathDir)
    for filePath in filePaths:
        ret = ret and isDICOM(filePath)
        if not ret:
            return False
    return ret


def compress(path):
    path = sanitizePath(path)
    folderName = getNameFromPath(path)
    tar = tarfile.open(joinPath([path, folderName+".tar.gz"]), "w:gz")
    pathChildren = getChildrenPaths(path)
    for child in pathChildren:
        tar.add(child, getNameFromPath(child)) #second argument required to add relative paths into tar
    tar.close()
    for child in pathChildren:
        delete(child)

def decompress(path):
    path = sanitizePath(path)
    files = getFilePaths(path)

    for file in files:
        if not file.endswith(".tar.gz"):
            continue
        tar = tarfile.open(file)
        tar.extractall(path)
        tar.close()
        delete(file)