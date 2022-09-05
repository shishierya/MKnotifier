import logging
import os

if os.path.exists("./test.log"):
    os.remove("./test.log")

logger = logging.getLogger('test_logger')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('test.log', 'a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s - %(process)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def info(log_msg):
    logger.info(log_msg)


def warning(log_msg):
    logger.warning(log_msg)
