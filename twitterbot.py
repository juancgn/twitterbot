import logging
import sqlite3
from random import randint
import tweepy
from datetime import datetime, time, date, timedelta
import requests
import time as ti
import os
from scheduler import Scheduler
import config

def check_database_connection():
     """
     Checks if the database connection can be established and that it has some entries.
     """
     try:
          # request data and try to unpack
          with sqlite3.connect(config.DATABASE) as conn:
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
     if os.path.exists(config.LOGFILE):
        os.remove(config.LOGFILE)

     formatter = logging.Formatter(config.LOGGER_FORMAT, datefmt=config.DATETIME_FORMAT)

     # tweepy logger
     twpy_logger = logging.getLogger("tweepy")
     twpy_logger.setLevel(logging.DEBUG)
     twpy_filehandler = logging.FileHandler(filename=config.LOGFILE)
     twpy_filehandler.setFormatter(formatter)
     twpy_logger.addHandler(twpy_filehandler)

     # app logger
     my_logger = logging.getLogger("twitterbot")
     my_logger.setLevel(logging.DEBUG)
     my_logger_filehandler = logging.FileHandler(filename=config.LOGFILE)
     my_logger_filehandler.setFormatter(formatter)
     my_logger.addHandler(my_logger_filehandler)

     my_logger.debug("Logger initialized.")

     return my_logger

def update_queue():
     """
     Puts the first quote in the queue at a random position in the second half of the queue.
     """
     with sqlite3.connect(config.DATABASE) as conn:
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
     timestamp = datetime.now().astimezone().strftime(config.DATETIME_FORMAT)
     with sqlite3.connect(config.DATABASE) as conn:
          c = conn.cursor()
          c.execute("""INSERT INTO posts (identifier, timestamp, quoteID, response_headers) VALUES (?, ?, ?, ?)""",
                    (identifier, timestamp, quoteID, str(response.headers)))
          conn.commit()

     my_logger.debug(f"Post with identifier {identifier} of quoteID {quoteID} logged in database.")

def get_new_quote():
     """
     Retrieves the first quote from the queue.
     """
     with sqlite3.connect(config.DATABASE) as conn:
          c = conn.cursor()

          # get next quote in queue
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
     with open(config.CREDENTIALS_FILE, "r") as f:
          consumer_key, consumer_secret, access_token, access_token_secret = [line.split(':')[-1] for line in f.read().split()]

     # establish an connection to the API
     client = tweepy.Client(
               consumer_key=consumer_key,
               consumer_secret=consumer_secret,
               access_token=access_token,
               access_token_secret=access_token_secret,
               return_type=requests.Response
          )

     # send tweet
     response = client.create_tweet(text=quote)
     if response.status_code != 201:
          raise tweepy.TweepyException(f"Posting failed. Got response code {response.status_code}.")
     
     return response

if __name__=="__main__":
     my_logger = prepare_logger()
     check_database_connection()

     scheduler = Scheduler()

     # main loop (every day)
     while True:
          
          # generate new posting times
          scheduler.generate()

          while not scheduler.is_empty():

               # sleep until next posting time
               scheduler.sleep()
               
               # get newest quote in the queue
               quote, quoteID = get_new_quote()

               # post the tweet
               try:
                    response = send_tweet(quote)   
                    my_logger.debug(f"Quote posted successfully: {quote}")

               except Exception as e:
                    my_logger.error(f"Posting failed. Error message: {str(e)}")
                    continue

               # if successfull
               log_post(response, quoteID)
               update_queue()
