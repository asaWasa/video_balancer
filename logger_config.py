import os

log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)

LOG_SIZE = 25 * 1024 * 1024  # 25 Mb

BACKUPS = 5

CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "[MAIN]|[%(levelname)s]|[%(asctime)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed_colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s[MAIN]|[%(levelname)s]|[%(asctime)s] - %(message)s%(reset)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
        },
        "uvicorn": {
            "format": "[UVICORN]|[%(levelname)s]|[%(asctime)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "uvicorn_colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s[UVICORN]|[%(levelname)s]|[%(asctime)s] - %(message)s%(reset)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                'DEBUG': 'cyan',
                'INFO': 'blue',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed_colored",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(log_dir, "main.log"),
            "formatter": "detailed",
            "maxBytes": LOG_SIZE,
            "backupCount": BACKUPS,
        },
        "uvicorn_console": {
            "class": "logging.StreamHandler",
            "formatter": "uvicorn_colored",
        },
        "uvicorn_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(log_dir, "uvicorn.log"),
            "formatter": "uvicorn",
            "maxBytes": LOG_SIZE,
            "backupCount": BACKUPS,
        },
    },
    "loggers": {
        "": {"level": "INFO", "handlers": ["console", "file"]},
        "uvicorn": {"level": "INFO", "handlers": ["uvicorn_console", "uvicorn_file"], "propagate": False},
        "uvicorn.access": {"level": "INFO", "handlers": ["uvicorn_console", "uvicorn_file"], "propagate": False},
        "uvicorn.error": {"level": "INFO", "handlers": ["uvicorn_console", "uvicorn_file"], "propagate": False},
        "fastapi": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
    },
}
