import logging
import warnings
from logging.handlers import TimedRotatingFileHandler

from stably_discordant_server.config import config


def setup_logger(
    dir_path: str = f"{config['misc_settings']['log_dir']}/stable-discord.log"
) -> logging.Logger:
    """Set up the logger including the formatting and logging both to a file with rotating logs and I/O stream

    Args:
        dir_path: The file path for the logging directory

    Returns:
        logging.Logger: The logger object.
    """
    if not dir_path:
        warnings.warn("Empty log_dir set in config.toml so defaulting to logs/ as logs_dir.")
        dir_path = "logs/stable-discord.log"

    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        level=logging.INFO,
        handlers=[
            TimedRotatingFileHandler(dir_path, "midnight", backupCount=7),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger()

    return logger
