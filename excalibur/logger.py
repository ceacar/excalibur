import logging
import functools

__default_logging_format = '%(asctime)s|%(levelname)s|%(filename)s|%(module)s|%(funcName)s|%(message)s'

__logger = None


def _remove_excessive_logger_handler(log_instance):
    while log_instance.hasHandlers():
        for i in log_instance.handlers:
            log_instance.removeHandler(i)


def logger_wrapper(orig_func):
    """
    a wrapper used as @logger_wrapper to print log of a function
    """
    # logging.basicConfig(filename='/tmp/{}.log'.format(orig_func.__name__), level=logging.INFO)
    logger = get_stdout_logger()
    @functools.wraps(orig_func)
    def wrapper(*args, **kwargs):
        logger.info(
            'Ran with args: {}, and kwargs: {}'.format(args, kwargs))
        return orig_func(*args, **kwargs)

    return wrapper


def __get_logger(file_handler, level=logging.DEBUG):
    logger = logging.getLogger(__name__)  # if run in main the name would be main, module then module
    # set to DEBUG for root logger by default, so sub logger can have freedom of configuring levels
    _remove_excessive_logger_handler(logger)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(file_handler)
    return logger


def get_stdout_logger(logging_level=logging.DEBUG, logger_format=__default_logging_format):
    """
    usage
    new_logger = get_stdout_logger()
    logger.debug("test123") #here need to use logger instead of default logging
    logger.info("test234") #here need to use logger instead of default logging
    ...
    """
    stream_handler = logging.StreamHandler()  # use this as the same of file handler
    formatter = logging.Formatter(logger_format)
    stream_handler.setFormatter(formatter)
    return __get_logger(stream_handler, level=logging_level)


def get_file_logger(log_file_path='/tmp/logger.log', logging_level=logging.DEBUG, logger_format=__default_logging_format, encoding=None):
    """
    usage
    new_logger = get_file_logger()
    logger.debug("test123") #here need to use logger instad of default logging
    logger.info("test234") #here need to use logger instad of default logging
    ...
    """
    file_handler = logging.FileHandler(log_file_path, encoding=encoding)  # use this as the same of file handler
    formatter = logging.Formatter(logger_format)
    file_handler.setFormatter(formatter)
    return __get_logger(file_handler, level=logging_level)


def getlogger(logger_format=__default_logging_format):
    """
    returns a logger that is shared across module to print to std
    """
    global __logger
    if not __logger:
        __logger = get_stdout_logger(logger_format=logger_format)
    return __logger
