import os
import logging

from config import LOG_FILE

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Create a logger
logger = logging.getLogger("LOGZ")
logger.setLevel(logging.DEBUG)  # Set level to capture all messages

# Create handlers
console_handler = logging.StreamHandler()  # For console output
file_handler = logging.FileHandler(LOG_FILE)  # Save logs to file

# Set levels for handlers
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

# Define a log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)