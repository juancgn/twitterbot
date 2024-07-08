import logging
import sqlite3
from random import randint
import tweepy
from datetime import datetime, time, date, timedelta
import requests
import time as ti
import os

# configs
DATABASE = "data.db"
LOGFILE = "twitterbot.log"
CREDENTIALS_FILE = "cred.env"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z%z"
SCHEDULE_LOG_DATETIME_FORMAT = "[%Y-%m-%d] %H:%M"
DATE_FORMAT = "%Y-%m-%d"

POSTING_HOURS_CONF_FILE = "posting_hours.conf"
POSTING_SCHEDULE_LOG = "posting_schedule.log"


def check_database_connection():
     """
     Checks if the database connection can be established and that it has some entries.
     """
     try:
          # request data and try to unpack
          with sqlite3.connect(DATABASE) as conn:
               c = conn.cursor()
               _, _ = c.execute("SELECT quoteID, quote FROM quotes").fetchone()
               _, _ = c.execute("SELECT ordering, quoteID FROM queue").fetchone()
               conn.commit()
     except Exception as e:
          my_logger.fatal(f"Database check failed. Terminate. Message: {str(e)}")
          exit()
     my_logger.debug("Database connection established.")
     
def prepare_logger():
     """
     Initializes the loggers for tweepy and app.
     """
     # delete old logfile if exists
     if os.path.exists(LOGFILE):
        os.remove(LOGFILE)

     # define formatter for both loggers
     formatter = logging.Formatter('[%(asctime)s] [%(name)s] %(levelname)s: %(message)s', datefmt=DATETIME_FORMAT)

     # tweepy logger
     twpy_logger = logging.getLogger("tweepy")
     twpy_logger.setLevel(logging.DEBUG)
     twpy_filehandler = logging.FileHandler(filename=LOGFILE)
     twpy_filehandler.setFormatter(formatter)
     twpy_logger.addHandler(twpy_filehandler)

     # own logger
     my_logger = logging.getLogger("twitterbot")
     my_logger.setLevel(logging.DEBUG)
     my_logger_filehandler = logging.FileHandler(filename=LOGFILE)
     my_logger_filehandler.setFormatter(formatter)
     my_logger.addHandler(my_logger_filehandler)

     my_logger.debug("Logger initialized.")
     return my_logger

def update_queue():
     """
     Puts the first quote in the queue at a random position in the second half.
     """
     # insert randomly in the second half
     with sqlite3.connect(DATABASE) as conn:
          c = conn.cursor()

          # compute new position
          n = c.execute("SELECT COUNT(*) FROM queue").fetchone()[0]
          i = randint(n//2+1, n)

          # get quoteID of first entry
          quoteID = c.execute("SELECT quoteID FROM queue WHERE ordering = 1").fetchone()[0]

          # move first entry to new position
          c.execute("UPDATE queue SET ordering = ordering - 1 WHERE ordering <= ?", (i,))
          c.execute("UPDATE queue SET ordering = (?) WHERE quoteID = (?)", (i, quoteID))
          
          conn.commit()
     my_logger.debug(f"Queue updated. Put first entry to position {i}/{n}.")
     
def log_post(response, quoteID):
     """
     Logs the post into the database using the information provided by the response.
     """
     identifier = response.json()['data']['id']
     timestamp = datetime.now().astimezone().strftime(DATETIME_FORMAT)
     with sqlite3.connect(DATABASE) as conn:
          c = conn.cursor()
          c.execute("""INSERT INTO posts (identifier, timestamp, quoteID, response_headers) VALUES (?, ?, ?, ?)""",
                    (identifier, timestamp, quoteID, str(response.headers)))
          conn.commit()

     my_logger.debug(f"Post with identifier {identifier} of quoteID {quoteID} logged in database.")

def get_new_quote():
     """
     Retrieves the first quote from the queue.
     """
     with sqlite3.connect(DATABASE) as conn:
          c = conn.cursor()

          # get newest quote
          quote, quoteID = c.execute("""SELECT quotes.quote, quotes.quoteID
                                   FROM quotes JOIN queue ON quotes.quoteID = queue.quoteID 
                                   WHERE queue.ordering = 1"""
                              ).fetchone()
                            
          conn.commit()
     return quote, quoteID

def send_tweet(quote):
     """
     Sends the tweet via tweepy.
     """
     # get credentials
     with open(CREDENTIALS_FILE, "r") as f:
          consumer_key, consumer_secret, access_token, access_token_secret = [line.split(':')[-1] for line in f.read().split()]

     client = tweepy.Client(
               consumer_key=consumer_key,
               consumer_secret=consumer_secret,
               access_token=access_token,
               access_token_secret=access_token_secret,
               return_type=requests.Response
          )

     # send
     response = client.create_tweet(text=quote)
     if response.status_code != 201:
          raise tweepy.TweepyException(f"Posting failed. Got response code {response.status_code}.")
     
     return response

def generate_new_posting_times():
     """
     Generates new posting times in the area of the hours and logs them in the corresponding log file.
     The clocktimes are generate randomly inside a two-hour space centered by the provided hours.
     """
     now = datetime.now().astimezone()

     # get posting hours config
     with open(POSTING_HOURS_CONF_FILE, 'r') as f:
          posting_hours = [int(h) for h in f.readline().strip().split(" ")]

     # check if there are remaining posting hours for today
     start_posting_today = (now.hour+1 < posting_hours[-1])
     
     # determine whether to start posting today or tomorrow
     posting_date = now.date()
     if not start_posting_today:
          posting_date += timedelta(days=1)

     # create posting_times
     posting_times = [ 
               datetime.combine(
                         date = posting_date, 
                         time = time(hour=h-randint(0,1), minute=randint(0, 59))
                    ).astimezone()
                    for h in posting_hours 
          ]

     # only use those posting_times for today whose posting_hours is at least 2 hrs is in the future
     if start_posting_today:
          posting_times = [posting_times[i] for i in range(len(posting_times)) if posting_hours[i]>now.hour+1]
     
     # log times
     with open(POSTING_SCHEDULE_LOG, 'w') as f:
          f.write( f"Computed on [{now.strftime(DATETIME_FORMAT)}]\n"
               + "\n".join( t.strftime(SCHEDULE_LOG_DATETIME_FORMAT) for t in posting_times )
               + "\n"
          )

     my_logger.debug(f"Computed posting hours for [{posting_times[0].strftime(DATE_FORMAT)}].")
     return posting_times

def sleep_until(clocktime):
     """
     Pauses the app until the provided time is reached.
     """
     # compute sleeping time
     now = datetime.now().astimezone()
     seconds_until_posting = (clocktime - now).total_seconds()

     # sleep
     my_logger.debug(f"Sleep until [{clocktime.strftime(DATETIME_FORMAT)}]")
     ti.sleep(seconds_until_posting)

if __name__=="__main__":
     my_logger = prepare_logger()
     check_database_connection()

     # main loop
     while True: # every day
          
          # compute new posting times
          posting_times = generate_new_posting_times()

          while len(posting_times)>0:
               # get next posting time and sleep until then
               next_posting_time = posting_times.pop(0)
               sleep_until(next_posting_time)
               
               # get newest quote in the queue
               quote, quoteID = get_new_quote()

               # try to post
               try:
                    response = send_tweet(quote)   
                    my_logger.debug(f"Quote posted successfully: {quote}")

               except Exception as e:
                    my_logger.error(f"Posting failed. Error message: {str(e)}")
                    continue

               # if successfull
               log_post(response, quoteID)
               update_queue()

     