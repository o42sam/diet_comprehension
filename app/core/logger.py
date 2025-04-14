from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")
logger.add("logs/app.log", rotation="500 MB", level="DEBUG")