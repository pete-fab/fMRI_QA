#!/usr/bin/env python
import directory
import hashlib
from os import unlink

HASH_EXTENSTION = ".hash"


def __get_hash_of_file(file_path):
    # file_path = directory.sanitizePath(file_path) # unnecessary
    try:
        if not directory.isFile(file_path):
            raise Exception
        BLOCKSIZE = 65536
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()
    except:
        print "Cannot hash non-existent file"
        raise OSError(file_path)


def __get_path(file_path):
    dir_path = directory.getFileDirectory(file_path)
    name = directory.getNameFromPath(file_path)
    return directory.joinPath([dir_path, "." + name + HASH_EXTENSTION])


def __read(file_path):
    hash_path = __get_path(file_path)
    if directory.isFile(hash_path):
        with open(hash_path, 'r') as f:
            hash = f.readline()
        return hash
    else:
        return False


def save(file_path):
    file_path = directory.sanitizePath(file_path)
    if directory.isFile(file_path):
        hash = __get_hash_of_file(file_path)
        hash_path = __get_path(file_path)
        with open(hash_path, 'w') as f:
            f.write(hash)
        return hash
    else:
        print "cannot save hashfile of non-existent file"
        raise OSError(file_path)


def verify(file_path):
    file_path = directory.sanitizePath(file_path)
    if directory.isFile(file_path):
        hash1 = __read(file_path)
        hash2 = __get_hash_of_file(file_path)
        if hash1 == hash2:
            return True
        else:
            return False
    else:
        print "Attempted to find hashfile for non existent file"
        raise OSError(file_path)


def remove(file_path):
    # important! This deletes file_path's hashfile not the file itself
    hash_path = __get_path(file_path)
    if directory.isFile(hash_path):
        unlink(hash_path)
        return True
    else:
        return False


if __name__ == "__main__":
    print verify("/media/sf_MAGAZYN/Data/QA/QA_fMRI_debug/20160810.tar.gz")
