import dicom
import config
import qa_csv
import hashfile
import my_logger as l
import directory as d
import datetime as dt
import dicom
import fmriQA


la = l.AllLogger()


class RawData(object):
    def __init__(self, local_root_path, processed_path, unprocessed_path, xml_path, server_path, summary_file_path, attribute_list):

        local_path = local_root_path
        self.__p_path = processed_path
        self.__up_path = unprocessed_path
        self.__xml_path = xml_path
        if not d.isDir(local_path):
            la.exception("Local_path is not existing directory: " + local_path)
            raise OSError(local_path)

        if not d.isDir(server_path):
            la.exception("server_path is not existing directory: " + server_path)
            raise OSError(server_path)

        self.__is_summary_valid = False
        self.__is_archive_files_valid = True

        self.__l_path = local_path
        self.__s_path = server_path
        self.__analysed_dates = set()
        # self.__datetime = dt.datetime(1, 1, 1, 0, 0, 0)
        self.__summary_path_unvalidated = summary_file_path
        self.__summary_path = ""
        self.__validate_summary_path(summary_file_path)
        self.__attrib_list = attribute_list

        self.data = {}
        self.__datasets = []
        self.update_datasets()

    def update_datasets(self):
        self.__retrieve_local_sets()
        self.__retrieve_server_sets()

    def set_local_path(self, local_path):
        self.__l_path = local_path

    def set_server_path(self, server_path):
        self.__s_path = server_path

    def __retrieve_local_sets(self):

        if not self.__is_summary_valid and self.__is_archive_files_valid:
            # Remake the global summary
            self.__fix_summary_from_local_archives()

        self.__get_dates_from_local_archives()
        if self.__is_summary_valid:
            self.__get_dates_from_summary()

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


    def __validate_summary_path(self, summary_path):
        if d.isFile(summary_path) and hashfile.verify(summary_path):
            self.__summary_path = summary_path
        else:
            # try backup summary
            backup = "." + d.getFileName(summary_path)
            backup_path = d.joinPath([self.__l_path, backup])
            if d.isFile(backup_path) and hashfile.verify(backup_path):
                self.__summary_path = backup_path
            else:
                self.__summary_path = ""

        if self.__summary_path != "":
            self.__is_summary_valid = True

    def __get_dates_from_summary(self):
        if self.__summary_path != "":
            data = qa_csv.read_csv(self.__summary_path)
            if len(data) != 0:
                date = sorted(data['seriesIndex'], reverse=True)[0]
                date_time = dt.datetime(int(date[0:4]), int(date[4:6]), int(date[6:]), 0, 0, 0)
                self.__analysed_dates.add(date_time)
                # if date_time > self.__datetime:
                #     self.__datetime = date_time
            else:
                message = "The global summary file should contain data if exists"
                la.error(message)
                raise BufferError(message)
    #
    #
    # #Get latest date from all rlogs
    # def __get_date_from_rlogs(self):
    #     rlogs = d.getFilePaths(self.__l_path, ".rlog")
    #     if len(rlogs) == 0:
    #         la.warn("No runtime logs found so far. It's OK if this is first run")
    #         return False
    #     for r_log in rlogs:
    #         if hashfile.verify(r_log):
    #             name = d.getFileName(r_log)
    #             datetime = dt.datetime(int(name[1:5]), int(name[6:8]), int(name[9:11]), int(name[12:14]),
    #                                    int(name[15:17]), int(name[18:20]))
    #             if datetime > self.__datetime:
    #                 self.__datetime = datetime
    #         else:
    #             la.warning("There exists rlog with modified hashfile: " + r_log)

    def __get_dates_from_local_archives(self):
        file_paths = d.getFilePaths(self.__p_path, ".gz")
        file_paths = sorted(file_paths)
        for f in file_paths:
            if hashfile.verify(f):
                name = d.getFileName(f)
                date_time = dt.datetime(int(name[0:4]), int(name[4:6]), int(name[6:8]), 0, 0, 0)
                self.__analysed_dates.add(date_time)
                # if date_time > self.__datetime:
                #     self.__datetime = date_time
            else:
                self.__is_archive_files_valid = False
                la.warning("There exists an analysis archive with modified hashfile: " + f + ". All will be removed")

        if not self.__is_archive_files_valid:
            for f in file_paths:
                d.delete(f)
                la.warning("Removed: " + f)

    def __fix_summary_from_local_archives(self):
        if self.__is_archive_files_valid:
            file_paths = d.getFilePaths(self.__xml_path, ".xml")
            file_paths = sorted(file_paths)
            for f in file_paths:
                if not hashfile.verify(f):
                    d.delete(f)
            # create global summary based on trusted local summaries
            qa_csv.save_global_summary(self.__xml_path, self.__attrib_list,
                                       d.joinPath([self.__l_path, d.getFileName(self.__summary_path_unvalidated)]) )
            la.info("Global summary remade from archive files")
            self.__is_summary_valid = True

            return True
        else:
            return False

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
