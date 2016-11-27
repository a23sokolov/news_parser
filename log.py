import logging
import os


def get_logger(name):
    _BASE_PATH = os.path.dirname(__file__)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("{0}/{1}.log".format(_BASE_PATH, 'log'))
    logger.addHandler(file_handler)
    file_handler.setFormatter(formatter)

    return logger
