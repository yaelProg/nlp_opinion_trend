from loguru import logger

from logging_utils import setup_logger
from get_data import main as get_data_main
from clean_data import main as clean_data_main

if __name__ == "__main__":
    setup_logger()
    logger.info("Running main pipeline entrypoint.")
    # get_data_main()
    clean_data_main()
