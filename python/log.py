#coding: utf-8
import os
import logging


def get_logger():
    path = os.getcwd()
    log_file = os.path.join(path, "query_file_attr.log")
    if not os.path.isfile(log_file):
        fd = open(log_file, "w")
        fd.close()
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler(log_file)
    logger.setLevel(logging.INFO)
    default_format = '[%(asctime)s] %(levelname)1.1s [%(filename)s:%(lineno)d:%(funcName)s]%(message)s'
    formatter = logging.Formatter(default_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger