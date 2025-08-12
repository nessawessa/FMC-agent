"""Basic logging configuration for FM&C Agent."""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """Set up basic logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Defaults to INFO.
    """
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Set third-party libraries to WARNING to reduce noise
    logging.getLogger("openpyxl").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
