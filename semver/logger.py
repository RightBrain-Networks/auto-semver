import logging
import subprocess

# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to INFO
console_logger = logging.StreamHandler()
console_logger.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to console_logger
console_logger.setFormatter(formatter)

# add console_logger to logger
logger.addHandler(console_logger)