import logging


def get_logger():

    logger = logging.getLogger("linuxguard")

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(
            "linuxguard.log"
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
