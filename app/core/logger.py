from loguru import logger

# Configure logger
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=True
)
