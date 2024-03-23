import logging

def get_logger():
    """
    Initializes and returns a logger with a predefined configuration.

    This function creates a logger named 'config_sdk' set to log INFO and higher level messages.
    It adds a StreamHandler to the logger, which outputs log messages to the console. The log
    messages are formatted to include the timestamp, logger name, log level, and the log message.

    Returns:
        logging.Logger: A configured Logger object ready for logging messages.

    Example:
        >>> logger = get_logger()
        >>> logger.info('Application started')
        2023-03-23 10:00:00,000 - config_sdk - INFO - Application started
    """
    logger = logging.getLogger("config_sdk")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
