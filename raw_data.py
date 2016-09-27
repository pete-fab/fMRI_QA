import dicom
import config
import directory
import qa_csv
import hashfile
import my_logger as l
import directory as d
import datetime as dt

la = l.AllLogger()


class RawData(object):
    def __init__(self, local_path, server_path, summary_file_path, attribute_list):
        if not d.isDir(local_path):
            al.exception("Local_path is not existing directory: " + local_path)
            raise OSError(local_path)

        if not d.isDir(local_path):
            al.exception("server_path is not existing directory: " + server_path)
            raise OSError(server_path)

        self.__is_summary_valid = False
        self.__is_archive_files_valid = True

        self.__l_path = local_path
        self.__s_path = server_path
        self.__datetime = dt.datetime(1, 1, 1, 0, 0, 0)
        self.__summary_path_unvalidated = summary_file_path
        self.__summary_path = ""
        self.__validate_summary_path(summary_file_path)
        self.__attrib_list = attribute_list


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

        # Gets date from archives and checks their validity
        self.__get_date_from_local_archives()
        if not self.__is_summary_valid and self.__is_archive_files_valid:
            # Remake the global summary
            self.__fix_summary_from_local_acrhives()

        if self.__is_summary_valid:
            self.__get_data_from_summary()
            self.__get_date_from_data()
            print self.__datetime
            # rlogs only useful to narrow down the date within the porgram run cycle
            self.__get_date_from_rlogs()
            print self.__datetime

        print self.__datetime
        raise NotImplementedError

    def __retrieve_server_sets(self):
        raise NotImplementedError

    def __validate_summary_path(self, summary_path):
        if d.isFile(summary_path) and hashfile.verify(summary_path):
            self.__summary_path = summary_path
        else:
            # try backup summary
            backup = "." + directory.getFileName(summary_path)
            backup_path = directory.joinPath([self.__l_path, backup])
            if directory.isFile(backup_path) and hashfile.verify(backup_path):
                self.__summary_path = backup_path
            else:
                self.__summary_path = ""

        if self.__summary_path != "":
            self.__is_summary_valid = True

    def __get_data_from_summary(self):
        raise NotImplementedError("Convienient way of combining data later is required")

    def __get_date_from_data(self):

        if self.__summary_path != "":
            data = qa_csv.read_csv(self.__summary_path)
            if len(data) != 0:
                date = sorted(data['seriesIndex'], reverse=True)[0]
                datetime = dt.datetime(int(date[0:4]), int(date[4:6]), int(date[6:]), 0, 0, 0)
                if datetime > self.__datetime:
                    self.__datetime = datetime
            else:
                message = "The global summary file should contain data if exists"
                la.error(message)
                raise BufferError(message)

    def __get_date_from_rlogs(self):
        rlogs = directory.getFilePaths(self.__l_path, ".rlog")
        if len(rlogs) == 0:
            la.warn("No runtime logs found so far. It's OK if this is first run")
            return False
        for r_log in rlogs:
            if hashfile.verify(r_log):
                name = directory.getFileName(r_log)
                datetime = dt.datetime(int(name[1:5]), int(name[6:8]), int(name[9:11]), int(name[12:14]),
                                       int(name[15:17]), int(name[18:20]))
                if datetime > self.__datetime:
                    self.__datetime = datetime
            else:
                la.warning("There exists rlog with modified hashfile: " + r_log)

    def __get_date_from_local_archives(self):
        file_paths = directory.getFilePaths(self.__l_path, ".gz")
        file_paths = sorted(file_paths)
        for f in file_paths:
            if hashfile.verify(f):
                name = directory.getFileName(f)
                datetime = dt.datetime(int(name[0:4]), int(name[4:6]), int(name[6:8]), 0, 0, 0)
                if datetime > self.__datetime:
                    self.__datetime = datetime
            else:
                self.__is_archive_files_valid = False
                la.warning("There exists an analysis archive with modified hashfile: " + f + ". All will be removed")

        if not self.__is_archive_files_valid:
            for f in file_paths:
                directory.delete(f)
                la.warning("Removed: " + f)

    def __fix_summary_from_local_acrhives(self):
        if self.__is_archive_files_valid:
            file_paths = directory.getFilePaths(self.__l_path, ".gz")
            file_paths = sorted(file_paths)
            # unzip all
            for f in file_paths:
                if hashfile.verify(f):
                    directory.decompress(f)
                else:
                    la.error("This file was verifired a moment ago and there is hash mismatch already: " + f)
                    raise OSError(f)
            # create global summary based on trusted local summaries
            qa_csv.save_global_summary(self.__l_path, self.__attrib_list,
                                       directory.getFileName(self.__summary_path_unvalidated))
            la.info("Global summary remade from archive files")
            self.__is_summary_valid = True

            # zip the folders
            dir_paths = directory.getChildrenPaths(self.__l_path)
            for d in dir_paths:
                directory.compress(d)

            return True
        else:
            return False

if __name__ == "__main__":
    if config.IS_DEBUG:
        atrribute_list = config.ATTRIBUTE_LIST_DEBUG
    else:
        atrribute_list = config.ATTRIBUTE_LIST
    data = RawData(config.DEBUG_DIR, config.PACS_DIR,
                   directory.joinPath([config.DEBUG_DIR, config.GLOBAL_SUMMARY_FILE]), atrribute_list)
