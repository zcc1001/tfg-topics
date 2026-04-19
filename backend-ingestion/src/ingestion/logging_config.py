import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_application_logging(data_dir: str, application_name: str) -> Path:
    logs_dir = Path(os.getenv("LOG_DIR", os.path.join(data_dir, "logs")))
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file_path = logs_dir / f"{application_name}.log"
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler],
        force=True,
    )
    logging.getLogger(__name__).info("File logging enabled at %s", log_file_path)

    return log_file_path
