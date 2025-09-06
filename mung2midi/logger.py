"""
Provides the default logger for this submodule. 
Use this logger for all logging within the module to ensure consistent configuration and control.

Usage inside the module example:

    from .logger import logger
    logger.info("This will log info message")

Usage outside the module example:

    import logging
    from mung2midi.logger import logger
    logger.setLevel(logging.INFO)
"""

import logging

MUNG2MIDI_LOGGER_NAME = "mung2midi"
logger = logging.getLogger(MUNG2MIDI_LOGGER_NAME)
logger.addHandler(logging.NullHandler())

def get_logger() -> logging.Logger:
    return logger