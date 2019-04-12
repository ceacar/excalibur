import logging
logging.basicConfig(level = logging.DEBUG)

def logger_wrapper(orig_func):
    """
    a wrapper used as @logger_wrapper to print log of a function
    """
    import logging
    logging.basicConfig(filename='/tmp/{}.log'.format(orig_func.__name__), level=logging.INFO)

    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        logging.info(
            'Ran with args: {}, and kwargs: {}'.format(args, kwargs))
        return orig_func(*args, **kwargs)

    return wrapper

__default_logging_format = '%(asctime)s|%(levelname)s|%(filename)s|%(module)s|%(funcName)s|%(message)s'

def __get_logger(file_handler):
    logger = logging.getLogger(__name__) #if run in main the name would be main, module then module
    logger.addHandler(file_handler)
    return logger

def get_stdout_logger(logging_level = logging.DEBUG, logger_format = __default_logging_format):
    """
    usage
    new_logger = get_stdout_logger()
    logger.debug("test123") #here need to use logger instad of default logging
    logger.info("test234") #here need to use logger instad of default logging
    ...
    """
    stream_handler = logging.StreamHandler() #use this as the same of file handler
    stream_handler.setLevel(logging_level)
    formatter = logging.Formatter(logger_format)
    stream_handler.setFormatter(formatter)
    return __get_logger(stream_handler)

def get_file_logger(log_file_path = '/tmp/logger.log', logging_level = logging.DEBUG, logger_format = __default_logging_format):
    """
    usage
    new_logger = get_file_logger()
    logger.debug("test123") #here need to use logger instad of default logging
    logger.info("test234") #here need to use logger instad of default logging
    ...
    """
    file_handler= logging.FileHandler(log_file_path) #use this as the same of file handler
    file_handler.setLevel(logging_level)
    formatter = logging.Formatter(logger_format)
    file_handler.setFormatter(formatter)
    return __get_logger(file_handler)

