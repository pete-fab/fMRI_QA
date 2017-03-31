# implement logging here log outputs rertireved by run_shell
# implementation from: http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
# Test this module and implement logger based on: https://docs.python.org/2/howto/logging.html
import inspect
import logging
import config
import directory
import os
from time import strftime, localtime


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GeneralLogger(logging.Logger):
    __metaclass__ = Singleton

    def __init__(self, log_directory=os.path.dirname(os.path.realpath(__file__))):
        if config.IS_DEBUG:
            log_directory = config.DEBUG_DIR
        log_directory = directory.sanitizePath(log_directory)
        if not directory.isDir(log_directory):
            print "Directory to save logs does not exist"
            raise OSError(log_directory)
        logging.Logger.__init__(self, 'root')
        self.__log_dir = log_directory
        # create log formatter
        self.__myformatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s')
        self.__l_path = directory.joinPath([log_directory, ".root_logger.log"])
        self.__myhandler = logging.FileHandler(self.__l_path, mode='a', encoding=None, delay=False)
        self.__myhandler.setLevel(logging.DEBUG)
        self.__myhandler.setFormatter(self.get_formatter())
        self.addHandler(self.__myhandler)
        # self.setLevel(logging.DEBUG)

    def get_log_dir(self):
        return self.__log_dir

    def get_formatter(self):
        return self.__myformatter

    def error(self, msg, *args, **kwargs):
        """
        Overriding error() function of logging.Logger object.
        It makes error() call _my_child logger instead of the main logger
        :param msg:
        :param args:
        :param kwargs:
        """
        logging.Logger.error(self, self.get_module_name() + ";" + msg)
        if self._my_child.isEnabledFor(logging.ERROR):
            self._my_child._log(logging.ERROR, self.get_module_name() + ";" + msg, args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """
        Overriding debug() function of logging.Logger object.
        It makes debug() call _my_child logger instead of the main logger
        :param msg:
        :param args:
        :param kwargs:
        """
        logging.Logger.debug(self, self.get_module_name() + ";" + msg)
        if self._my_child.isEnabledFor(logging.DEBUG):
            self._my_child._log(logging.DEBUG, self.get_module_name() + ";" + msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Overriding info() function of logging.Logger object.
        It makes info() call _my_child logger instead of the main logger
        :param msg:
        :param args:
        :param kwargs:
        """
        logging.Logger.info(self, self.get_module_name() + ";" + msg)
        if self._my_child.isEnabledFor(logging.INFO):
            self._my_child._log(logging.INFO, self.get_module_name() + ";" + msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Overriding warning() function of logging.Logger object.
        It makes warning() call _my_child logger instead of the main logger
        :param msg:
        :param args:
        :param kwargs:
        """
        logging.Logger.warning(self, self.get_module_name() + ";" + msg)
        if self._my_child.isEnabledFor(logging.WARNING):
            self._my_child._log(logging.WARNING, self.get_module_name() + ";" + msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Overriding critical() function of logging.Logger object.
        It makes critical() call _my_child logger instead of the main logger
        :param msg:
        :param args:
        :param kwargs:
        """
        logging.Logger.critical(self, self.get_module_name() + ";" + msg)
        if self._my_child.isEnabledFor(logging.CRITICAL):
            self._my_child._log(logging.CRITICAL, self.get_module_name() + ";" + msg, args, **kwargs)

    def get_module_name(self):
        callerframerecord = inspect.stack()[2]  # 0 represents this line
        # 1 represents line at caller
        # 2 is caller of the caller
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        return directory.getFileNameWithoutExtension(info.filename)
        # print 'File with error: '+info.filename                       # __FILE__     -> Test.py
        # print 'Function: '+info.function                       # __FUNCTION__ -> Main
        # print 'Line number: '+str(info.lineno)

    def get_log_file_path(self):
        return self.__l_path


class RuntimeLogger(GeneralLogger):
    def __init__(self):
        GeneralLogger.__init__(self)
        self.__l_path = directory.joinPath([self.get_log_dir(),
                                            "." + strftime("%Y-%m-%d_%H-%M-%S", localtime()) + config.RUNTIME_LOG
                                            ])
        print "Runtime logger path " + self.__l_path
        self.__myhandler = logging.FileHandler(self.__l_path, mode='a', encoding=None, delay=False)
        self.__myhandler.setLevel(logging.INFO)
        self.__myhandler.setFormatter(self.get_formatter())
        self._my_child = self.getChild('RunTimeLogger')
        self._my_child.parent.setLevel(logging.INFO)  # This is a hack.
        # Otherwise it is set to logging.WARNING and info and debug are not logged. Because child cannot log more than a parent
        self._my_child.addHandler(self.__myhandler)  # set child handler


# class AllLogger(GeneralLogger):
#     def __init__(self):
#         GeneralLogger.__init__(self)
#         self.__l_path = directory.joinPath([self.get_log_dir(), config.ALL_LOG])
#         print "Alllogger path " + self.__l_path
#         self.__myhandler = logging.FileHandler(self.__l_path, mode='a', encoding=None, delay=False)
#         self.__myhandler.setLevel(logging.DEBUG)
#         self.__myhandler.setFormatter(self.get_formatter())
#         self._my_child = self.getChild('AllLogger')
#         self._my_child.parent.setLevel(logging.DEBUG)  # This is a hack.
#         # Otherwise it is set to logging.WARNING and info and debug are not logged. Because child cannot log more than a parent
#         self._my_child.addHandler(self.__myhandler)  # set child handler


if __name__ == "__main__":
    # example usage:
    # a = AllLogger()
    # a.critical("test critical message")

    r = RuntimeLogger()
    r.critical("runtime critical")
    # a.critical("2nd critical")

    # expected output:
    # RuntimeLogger file contains formatted:
    # runtime critical

    # AllLogger file contains formatted:
    # test critical message
    # 2nd critical

    # There is a background root logger that contains all messages
