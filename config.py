"""
This is the configuration file for the twitterbot app.
The most important parameters to check are those for the schedule.
Set a schedule mode and their parameters as desired.
"""

### app
TWEET_MAX_LENGTH = 280

### scheduler
"""
Available modes for generating the posting times are:
    `fix`:          Fix posting times. May vary up to 59 mins, if ´random_variance` is set nonzero.
    `uniform`:      Evenly distributed within the time window. One posting per minute is maximum.
"""
SCHEDULE_MODE = 'uniform'
FIX_MODE = {
        'posting_times' : ['00:04', '00:25', '05:29', '08:01', '10:40', '13:22', '16:00', '18:39', '21:20', '23:11'],
        'random_variance' : 30
}
UNIFORM_MODE = {
        'num_posts' : 10,
        'time_window' : ['07:00', '23:00']
}

### paths
DATABASE = "data.db"
LOGFILE = "twitterbot.log"
CREDENTIALS_FILE = "cred.env"
RAWDATA_FILE = "rawdata.txt"

### formats
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z%z"
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
LOGGER_FORMAT = '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'