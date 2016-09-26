import dicom
import qa_csv
import hashfile


class RawData(object):
    def __init__(self, local_path, server_path, summary_file_path):
        self.__l_path = local_path
        self.__s_path = server_path
        if hashfile.verify(summary_file_path):
            self.__summary_path = summary_file_path
        else:
            self.__summary_path = ""
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
        if self.__summary_path != "":
            data = qa_csv.read_csv(self.__summary_path)
            # good situation can trust the data we have
            # just search for the new data on PACS
        else:
            raise NotImplementedError
            # worse will need to
            # 1.unzip all local data (if any hashfile is wrong - redownload that file and queue up for analysis)
            # 2.read local files

    def __retrieve_server_sets(self):
        print "s"


if __name__ == "__main__":
    data = RawData("///", "ddd")
    data.
