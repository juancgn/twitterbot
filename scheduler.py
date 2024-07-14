from datetime import datetime, timedelta
import config
import logging
from random import randint
import time

class Scheduler:

    def __init__(self):
        """
        The constructor of this class. Initializes the logger and mode attributes.
        """
        # object variables
        self.schedule = None
        self.mode = None
        self.generate = None

        self.logger = self._init_logger()
        self._set_mode()

        self.logger.debug(f"Scheduler initialized in '{self.mode}' mode.")

    def _init_logger(self):
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

    def _set_mode(self):
        """
        Sets up the mode and the generate() function wrt the config file.
        """
        # choose func wrt mode
        self.generation_funcs = {
            'fix' : self._generate_fix,
            'uniform' : self._generate_uniform
        }
        self.mode = config.SCHEDULE_MODE
        self.generate = self.generation_funcs[config.SCHEDULE_MODE]

    def _generate_fix(self):
        """
        Computes the posting times given the input data in the config file. Varies the input data if config file indicates so.
        If no posting time would occur after execution of this code at the same day, the posting will be computed for the following day.
        """
        now = datetime.now().astimezone()

        rv = config.FIX_MODE['random_variance']

        # create time objects from configurated posting times
        posting_times = []
        for t in config.FIX_MODE['posting_times']:
            # create time object from given time string
            t = datetime.strptime(t, config.TIME_FORMAT)

            # vary time if indicated and ensure it don´t exceed 00:00 or 23:59
            lowb = min(t.minute, rv) if t.hour==0 else rv
            uppb = min(59-t.minute, rv) if t.hour==23 else rv

            t += timedelta( minutes=randint(-lowb, uppb) )

            posting_times.append(t.time())

        # catch unsorted input data
        posting_times.sort()

        # decide whether to compute times for today or tomorrow
        posting_day = now.date() + timedelta(days=1) * (posting_times[-1] < now.time())
        
        # create datetime objects and remove passed posting times (may occur on first day)
        schedule = [datetime.combine(posting_day, t).astimezone() for t in posting_times]
        schedule = [posting_time for posting_time in schedule if now < posting_time]

        self.logger.debug(f"Generated posting times for [{posting_day.strftime(config.DATE_FORMAT)}]: {" ".join( t.strftime(config.TIME_FORMAT) for t in schedule )}")
        
        self.schedule = schedule

    def _generate_uniform(self):
        """
        Computes the posting times evenly distributed within the given time window. Only allows up to 1 posting per minute. 
        If no posting time would occur after execution of this code at the same day, the posting will be computed for the following day.
        """
        now = datetime.now().astimezone()

        # parameters
        postings = config.UNIFORM_MODE['postings']

        # start and end time
        start_time, end_time = config.UNIFORM_MODE['time_window']
        start_time, end_time = datetime.strptime(start_time, config.TIME_FORMAT), datetime.strptime(end_time, config.TIME_FORMAT)
        total_space = (end_time-start_time).total_seconds()

        # compute distribution
        space_per_post =  total_space // (postings+1)
        if space_per_post < 60:
            space_per_post = 60
            postings = int(total_space//space_per_post - 1)
            self.logger.warning(f"Posting {config.UNIFORM_MODE['postings']} posts from {start_time.strftime(config.TIME_FORMAT)} to {end_time.strftime(config.TIME_FORMAT)} is too much. Posting {int(postings)} posts instead (1 per minute).")

        # add posting times iteratively
        schedule = []
        curr_time = start_time + timedelta(seconds=space_per_post)
        while len(schedule) < postings:
            schedule.append(curr_time)
            curr_time += timedelta(seconds=space_per_post)

        # compute posting date and correct the schedule
        posting_day = now.date()
        if now.time() > schedule[-1].time():
            posting_day += timedelta(days=1)
        schedule = [
            datetime.combine(posting_day, posting_time.time()).astimezone() for posting_time in schedule
        ]

        self.logger.debug(f"Generated {postings} posting times for [{posting_day.strftime(config.DATE_FORMAT)}]: {" ".join( t.strftime(config.TIME_FORMAT+':%S') for t in schedule )}")

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
        time.sleep(seconds_until_posting)

    def is_empty(self):
        """
        Returns if the list of posting times is empty. Intended to be used as the condition the main loop.
        """
        return len(self.schedule)==0

