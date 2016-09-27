#!/usr/bin/env python
import os
import dicom
import sys
import tarfile
import shutil
import hashfile

SEP = os.path.sep
D_SEP = os.path.sep + os.path.sep
ARCHIVE_EXTENSION = ".tar.gz"

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
        hashfile.remove(pathDir)
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


def getFileNames(path_dir, ext=""):
    if ext == "":
        return [x[2] for x in os.walk(path_dir)][0]
    else:
        # path_paths = getFilePaths(path_dir)
        files = [x[2] for x in os.walk(path_dir)][0]
        return filter(lambda x: getExtenstion(x) == ext, files)


def getExtenstion(file_path):
    (root, ext) = os.path.splitext(file_path)
    return ext


def getFilePaths(pathDir, ext=""):
    list = getFileNames(pathDir, ext)
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
        dicom.read_file(filePath)
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


def compress(dir_path):
    dir_path = sanitizePath(dir_path)
    archive_path = dir_path + ARCHIVE_EXTENSION
    try:
        tar = tarfile.open(archive_path, "w:gz")
        tar.add(dir_path, getNameFromPath(dir_path))  # second argument required to add relative paths into tar
        tar.close()
        delete(dir_path)
        hashfile.save(archive_path)
        return True
    except OSError:
        # when open() call was made to nonexistent file it was created. Need to close it and delete.
        tar.close()
        delete(archive_path)
        raise OSError
    except:
        print "Compression of folder " + dir_path + " went wrong!"
        raise RuntimeError


def getFileName(filePath):
    filePath = sanitizePath(filePath)
    return os.path.basename(filePath)


def getFileNameWithoutExtension(filePath):
    filePath = sanitizePath(filePath)
    return os.path.basename(os.path.splitext(filePath)[0])


def getFileDirectory(filePath):
    filePath = sanitizePath(filePath)
    res = filePath.replace(SEP + os.path.basename(filePath), "")
    return res


def decompress(file_path):
    file_path = sanitizePath(file_path)

    if isFile(file_path) and file_path.endswith(ARCHIVE_EXTENSION):
        if hashfile.verify(file_path):
            tar = tarfile.open(file_path)
            directory = getFileDirectory(file_path)
            # name = getFileNameWithoutExtension(file_path)
            tar.extractall(directory)
            tar.close()
            delete(file_path)
            return True
        else:
            delete(file_path)
            return False
    else:
        if isFile(file_path):
            raise OSError("Attempted to decompress non-archive:", file_path)
        else:
            raise OSError("Attempted to decompress non existent file:", file_path)


def copy_file(source_path, destination_path):
    source_path = sanitizePath(source_path)
    destination_path = sanitizePath(destination_path)
    if isFile(source_path):
        shutil.copy2(source_path, destination_path)
    else:
        print "Tried to copy non-existent file"
        raise OSError(source_path)


if __name__ == "__main__":
    # print getFileName("a/b/c.txt")
    # hash = compress("/media/sf_MAGAZYN/Data/QA/QA_fMRI_debug/20160810")
    # print hash
    getFileNames("/media/sf_MAGAZYN/Data/QA/QA_fMRI_debug/", ".rlog")
    # decompress("/media/sf_MAGAZYN/Data/QA/QA_fMRI_debug/20160810.tar.gz")
    # print hash_file("/media/sf_MAGAZYN/Data/QA/QA_fMRI_debug/20160810.tar.gz")
