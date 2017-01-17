import dicom
import config
import qa_csv
import hashfile
import my_logger as l
import directory as d
import datetime as dt
import dicom
import fmriQA
from glob import glob

logger = l.RuntimeLogger()


class RawData(object):
    def __init__(self, local_root_path, processed_path, unprocessed_path, xml_path, local_summaries_path, server_path,
                 summary_file_path, attribute_list):

        local_path = local_root_path

        self.__validate_dirs(processed_path,"processed_path")
        self.__validate_dirs(unprocessed_path,"unprocessed_path")
        self.__validate_dirs(xml_path,"xml_path")
        self.__validate_dirs(local_path, "local_path")
        self.__validate_dirs(server_path, "server_path")
        self.__validate_dirs(local_summaries_path, "local_summaries_path")


        self.__is_summary_valid = False
        self.__is_archive_files_valid = False

        self.__p_path = processed_path
        self.__up_path = unprocessed_path
        self.__xml_path = xml_path
        self.__l_path = local_path
        self.__local_summaries_path = local_summaries_path
        self.__s_path = server_path
        self.__analysed_dates = set()
        self.__summary_path_unvalidated = summary_file_path
        self.__summary_path = ""
        self.__validate_summary_path(summary_file_path)
        self.__validate_local_archives()
        self.__attrib_list = attribute_list

        self.data = {}
        self.__datasets = []
        self.update_datasets()

    def __validate_dirs(self, pathDir, varName):
        if not d.isDir(pathDir):
            logger.exception(varName + " is not existing directory: " + pathDir)
            raise OSError(pathDir)

    def update_datasets(self):
        logger.info("update_datasets started")
        self.__retrieve_local_sets()
        self.__retrieve_server_sets()
        logger.info("update_datasets finished")

    def set_local_path(self, local_path):
        self.__l_path = local_path

    def set_server_path(self, server_path):
        self.__s_path = server_path

    def __retrieve_local_sets(self):
        logger.debug("__retrieve_local_sets started")
        if not self.__is_summary_valid and self.__is_archive_files_valid:
            # Remake the global summary
            self.__fix_summary_from_local_archives()

        logger.info(str(self.__analysed_dates))
        self.__get_dates_from_local_archives()
        logger.info(str(self.__analysed_dates))
        #Am i not doubling the functionality here?
        # if self.__is_summary_valid:
        #     self.__get_dates_from_summary()
        logger.debug("__retrieve_local_sets finished")


    def __retrieve_server_sets(self):
        dir_names = d.getChildrenFolders(self.__s_path)
        dir_names = sorted(dir_names, reverse=True)
        for dn in dir_names:
            date_time = dt.datetime(int(dn[0:4]), int(dn[4:6]), int(dn[6:]), 0, 0, 0)
            # print date_time
            if not self.__analysed_dates.issuperset(set([date_time])):
            # if datetime > self.__datetime:
                self.__analysed_dates.add(date_time)
                date_string = "{:%Y%m%d}".format(date_time)
                sub_paths = d.getChildrenPaths(d.joinPath([self.__s_path, date_string]))
                for sp in sub_paths:
                    if d.isContentsDICOM(sp):
                        # In this directory there should be only DICOMs - so first file is good as any
                        file_path = d.getOneFilePath(sp)
                        if fmriQA.verify_is_QA_DICOM(file_path):
                            dest = d.joinPath([self.__up_path, date_string, config.DATA_SERIESDESCRIPTION])
                            d.copy_folder_contents(sp, dest)

    def __validate_local_archives(self):
        logger.debug("__validate_local_archives started")
        files = d.getFilePaths(self.__xml_path,".xml")
        self.__is_archive_files_valid = True
        for f in files:
            if not d.isFile(f) or not hashfile.verify(f):
                logger.warning("XML found invalid: " + f)
                name = d.getFileName(f)
                date_string = name[0:8]
                self.__delete_connected_files(date_string)

        files = d.getFilePaths(self.__local_summaries_path,config.SUMMARY_EXT)
        for f in files:
            if not d.isFile(f) or not hashfile.verify(f):
                logger.warning("Local summary found invalid: " + f)
                name = d.getFileName(f)
                date_string = name[0:8]
                self.__delete_connected_files(date_string)

        files = d.getFilePaths(self.__p_path, d.ARCHIVE_EXTENSION)
        for f in files:
            if not d.isFile(f) or not hashfile.verify(f):
                logger.warning("Archive found invalid: " + f)
                name = d.getFileName(f)
                date_string = name[0:8]
                self.__delete_connected_files(date_string)

        logger.debug("__validate_local_archives finished with result: " + str(self.__is_archive_files_valid))

    def __validate_summary_path(self, summary_path):
        logger.debug("__validate_summary_path started")
        if d.isFile(summary_path) and hashfile.verify(summary_path):
            logger.debug("global summary is valid")
            self.__summary_path = summary_path
        else:
            # try backup summary
            logger.debug("global summary is found invalid")
            backup = "." + d.getFileName(summary_path)
            backup_path = d.joinPath([self.__l_path, backup])
            if d.isFile(backup_path) and hashfile.verify(backup_path):
                logger.debug("backup global summary is used")
                self.__summary_path = backup_path
            else:
                self.__summary_path = ""

        if self.__summary_path != "":
            self.__is_summary_valid = True
        logger.debug("__validate_summary_path finished")

    def __get_dates_from_summary(self):
        logger.debug("__get_dates_from_summary started")
        if self.__summary_path != "":
            data = qa_csv.read_csv(self.__summary_path)
            if len(data) != 0:
                date = sorted(data['seriesIndex'], reverse=True)[0]
                date_time = dt.datetime(int(date[0:4]), int(date[4:6]), int(date[6:]), 0, 0, 0)
                self.__analysed_dates.add(date_time)
            else:
                message = "The global summary file should contain data if exists"
                logger.error(message)
                raise BufferError(message)
        logger.debug("__get_dates_from_summary finished")

    def __get_dates_from_local_archives(self):
        if self.__is_archive_files_valid:
            logger.debug("__get_dates_from_local_archives started")
            file_paths = d.getFilePaths(self.__xml_path, ".xml")
            file_paths = sorted(file_paths)
            for f in file_paths:
                name = d.getFileName(f)
                if hashfile.verify(f):
                    date_time = dt.datetime(int(name[0:4]), int(name[4:6]), int(name[6:8]), 0, 0, 0)
                    self.__analysed_dates.add(date_time)
                else:
                    date_string = name[0:8]
                    self.__is_archive_files_valid = False
                    self.__delete_connected_files(date_string)
            logger.debug("__get_dates_from_local_archives finished")

    def __delete_connected_files(self, date_name):
        # date_name format "YYYYmmdd"
        xml_path = d.joinPath([self.__xml_path, date_name + "*.xml"])
        for f in glob(xml_path):
            if d.isFile(f):
                d.delete(f)
                logger.warning("Removed: " + f)
            else:
                logger.warning("File missing: " + f)
        archive_path = d.joinPath([self.__p_path, date_name + d.ARCHIVE_EXTENSION])
        if d.isFile(archive_path):
            d.delete(archive_path)
            logger.warning("Removed: " + archive_path)
        else:
            logger.warning("File missing: " + archive_path)
        local_summary_path = d.joinPath([self.__local_summaries_path, date_name + config.SUMMARY_EXT])
        if d.isFile(local_summary_path):
            d.delete(local_summary_path)
            logger.warning("Removed: " + local_summary_path)
        else:
            logger.warning("File missing: " + local_summary_path)

    def __fix_summary_from_local_archives(self):
        logger.debug("__fix_summary_from_local_archives started")
        if self.__is_archive_files_valid:
            file_paths = d.getFilePaths(self.__xml_path, ".xml")
            file_paths = sorted(file_paths)
            for f in file_paths:
                if not hashfile.verify(f):
                    d.delete(f)
            # create global summary based on trusted local summaries
            qa_csv.save_global_summary(self.__xml_path, self.__attrib_list,
                                       d.joinPath([self.__l_path, d.getFileName(self.__summary_path_unvalidated)]) )
            logger.info("Global summary remade from archive files")
            self.__is_summary_valid = True

            ret = True
        else:
            ret = False
        logger.debug("__fix_summary_from_local_archives finished with result: " + str(ret))
        return ret

if __name__ == "__main__":
    if config.IS_DEBUG:
        atrribute_list = config.ATTRIBUTE_LIST_DEBUG
    else:
        atrribute_list = config.ATTRIBUTE_LIST
    data = RawData(config.DEBUG_DIR,
                   config.PACS_DIR,
                   d.joinPath([config.DEBUG_DIR, config.GLOBAL_SUMMARY_FILE]),
                   atrribute_list
                   )
