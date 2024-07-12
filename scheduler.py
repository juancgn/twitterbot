from datetime import datetime, time, date, timedelta
import config
import logging
from random import randint
import time as ti

class Scheduler:

    def __init__(self):
        """
        The constructor of this class. Initializes the logger and other empty object variables.
        """
        self.curr_date = None
        self.schedule = None
        self.logger = self.init_logger()

        self.logger.debug("Scheduler initialized.")

    def init_logger(self):
        """
        Creates the logger.
        """
        formatter = logging.Formatter(config.LOGGER_FORMAT, datefmt=config.DATETIME_FORMAT)

        logger = logging.getLogger("scheduler")
        logger.setLevel(logging.DEBUG)
        filehandler = logging.FileHandler(config.LOGFILE)
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)

        return logger

    def generate(self):
        """
        Generates the schedule with respect to the config posting hours and current datetime.
        """
        now = datetime.now().astimezone()

        # get posting hours
        posting_hours = config.POSTING_HOURS.copy()

        # check if there are remaining posting hours for today
        start_posting_today = (now.hour+1 < posting_hours[-1])

        # determine whether to start posting today or tomorrow
        curr_date = now.date()
        if not start_posting_today:
            curr_date += timedelta(days=1)

        # create posting_times
        schedule = [ 
                datetime.combine(
                            date = curr_date, 
                            time = time(hour=h-randint(0,1), minute=randint(0, 59))
                        ).astimezone()
                        for h in posting_hours 
            ]

        # only use those posting_times for today whose posting_hours is at least 2 hrs is in the future
        if start_posting_today:
            schedule = [schedule[i] for i in range(len(schedule)) if posting_hours[i]>now.hour+1]
        
        self.logger.debug(f"Generated posting hours for [{curr_date.strftime(config.DATE_FORMAT)}]: {" ".join( t.strftime(config.TIME_FORMAT) for t in schedule )}")
        
        self.curr_date = curr_date
        self.schedule = schedule

    def sleep(self):
        """
        Gets the runtime to sleep until the next posting time.
        """
        # compute sleeping time
        now = datetime.now().astimezone()
        next_posting_time = self.schedule.pop(0)
        seconds_until_posting = (next_posting_time - now).total_seconds()

        # sleep
        self.logger.debug(f"Sleep until [{next_posting_time.strftime(config.DATETIME_FORMAT)}]")
        ti.sleep(seconds_until_posting)

    def is_empty(self):
        """
        Returns if the list of posting times is empty. Intended to be used as the condition the main loop.
        """
        return len(self.schedule)==0

