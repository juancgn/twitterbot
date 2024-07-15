import sqlite3
import random
import config

def create_new_database():
    """
    Creates and saves the database with sqlite3.
    """
    with sqlite3.connect(config.DATABASE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                quoteID INTEGER PRIMARY KEY,
                quote TEXT NOT NULL 
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS queue (
                ordering INTEGER NOT NULL,
                quoteID INTEGER NOT NULL,
                FOREIGN KEY(quoteID) REFERENCES quotes(quoteID)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                postID INTEGER PRIMARY KEY NOT NULL,
                identifier TEXT NOT NULL UNIQUE,
                timestamp TEXT NOT NULL,
                quoteID INTEGER NOT NULL,
                response_headers TEXT,
                FOREIGN KEY(quoteID) REFERENCES quotes(quoteID)
            )
        """)
        conn.commit()

    print("Database created.")

def insert_quote(quote:str):
    """
    Inserts `quote` to the quotes table and queues it in the `queue` table.
    """
    with sqlite3.connect(config.DATABASE) as conn:
        c = conn.cursor()

        # create new quote
        c.execute("INSERT INTO quotes (quote) VALUES (?)", (quote,))
        quoteID = c.lastrowid

        # append quote to queue
        n = c.execute("SELECT COUNT(*) FROM queue").fetchone()[0]
        c.execute("INSERT INTO queue (quoteID, ordering) VALUES (?, ?)", (quoteID, n+1))
        
        conn.commit()
    
def fill_database():
    """
    Fills the database with the quotes from the rawdata file.
    """
    # load quotes
    with open(config.RAWDATA_FILE, "r") as f:
        quotes = f.read().split("\n")

    # fill database
    for quote in quotes:
        if len(quote) <= config.TWEET_MAX_LENGTH:
            insert_quote(quote)
        else:
            print(f"Warning: Can't add this quote to the database, it's too long for Twitter: {quote}")
    
    print("Database filled.")

def quotes_list():
    """
    Returns a list of the quotes in the database sorted by their position in the queue.
    """
    with sqlite3.connect(config.DATABASE) as conn:
        c = conn.cursor()
        # get quotes as a list sorted by the ordering in the queue
        quotes_list = [
                quote for (quote,) in c.execute("""SELECT quotes.quote FROM quotes JOIN queue 
                                                ON quotes.quoteID = queue.quoteID ORDER BY ordering""").fetchall()
            ]
        conn.commit()

    return quotes_list

def shuffle_raw_list():
    """
    Shuffles the positions of the quotes in the raw data file before it can be used for the database.
    """
    with open(config.RAWDATA_FILE, "r") as f:
        quotes = [q.replace("\n", "") for q in f.readlines()]
    random.shuffle(quotes)
    with open(config.RAWDATA_FILE, "w") as f:
        f.writelines("\n".join(quotes))

    print("Shuffled raw list randomly.")

if __name__=="__main__":
    # create new sqlite3 database and the tables
    create_new_database()

    # fill the database with the quotes in the rawdata file
    fill_database()
    
    # insert a single quote by hand 
    #insert_quote("TEST")

    # get ordered quotes list from database
    #my_quotes = quotes_list()

    # shuffle the rawdata file randomly
    #shuffle_raw_list()
    

    
