"""
This is the configuration file for the twitterbot app.
The most important parameters to check are those for the schedule.
Set a schedule mode and their parameters as desired.
"""

# app
POSTING_HOURS = [9, 12, 15, 18, 21]
TWEET_MAX_LENGTH = 280

# paths
DATABASE = "data.db"
LOGFILE = "twitterbot.log"
CREDENTIALS_FILE = "cred.env"
POSTING_SCHEDULE_LOG = "posting_schedule.log"
RAWDATA_FILE = "rawdata.txt"

# formats
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z%z"
SCHEDULE_LOG_DATETIME_FORMAT = "[%Y-%m-%d] %H:%M"
DATE_FORMAT = "%Y-%m-%d"
LOGGER_FORMAT = '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'