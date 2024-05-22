import logging

from .constants import PYTHON_ENVIRONMENT

logging.basicConfig()

if  PYTHON_ENVIRONMENT == "development":
    logging.getLogger().setLevel(logging.DEBUG)
