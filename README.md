# Twitterbot

Twitterbot is a Python-based bot for Twitter that reads tweets (called `quotes`) from a local SQLite database and automatically posts them on Twitter. I wrote it to post funny quotes from my favorite character from a CBS show automatically. The bot uses the Tweepy library for interacting with the Twitter API v2 and is designed to post at configurable times. Twitterbot only uses the free-of-charge tools of the Twitter API.

Twitterbot is designed to run permanently and therefore you should run it on a server, a Raspberry Pi oder another systems which is up permanently.

## Features

- **Database Connection:** The bot establishes a connection to a local SQLite database that manages quotes, queueing, and post logging.
- **Tweet Posting:** Quotes are posted as tweets using the Twitter API with Tweepy.
- **Scheduling:** Multiple schedule options are provided which take care of the posting timing
- **Logging:** Events and errors are logged to assist with performance monitoring and troubleshooting.
- **Queueing:** Used quotes will be queued randomly in the second half of the queue, so the quote selection is random enough but a quote is definitely not posted again too soon.

## Requirements

- Python 3.x
- Tweepy 4.14.10 or newer
- SQLite (for the local database, comes with the Python standard library)

## Installation

1. Clone the repository to your server:
   ```bash
   git clone https://github.com/juancgn/twitterbot.git
   cd twitterbot
   ```
2. Install tweepy with 
    ```
    pip install -r requirements.txt
    ```
## Usage

1. Write your quotes in a new file named `rawdata.txt`, one per line. Ensure they do not exceed the allowd Tweet length. Copy this file to your server using, for example, ssh:

    ```
    scp [-i ssh_private_key] /path/on/your/computer/rawdata.txt username@SERVER_IP:/path/to/directory/of/twitterbot
    ```
2. Run the following command on your server to create a local SQLite database from the raw data:
    ```
    python3 database.py
    ```
3. Sign up for a [Twitter developer account](https://developer.x.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api) (the free plan is sufficient) and obtain the credentials from the developer portal.
4. Create a `cred.env` file and add your Twitter API credentials in the following format:: 
    ```
    consumer_key:XXXXXXX
    consumer_secret:XXXXXXX
    access_token:XXXXXXX
    access_token_secret:XXXXXXX
    ```
    Copy the credentials file to your server, too.
5. Open the `config.py` and set the parameters. You can manipulate the file on the ssh terminal with: 
    ```
    vim config.py
    ```
    Press `i` to manipulate the file, `Esc` when finished and `:wq` to save and close.
    The most important parameters are those for the schedule. Choose a `SCHEDULE_MODE` and adjust their corresponding parameters. Change the allowed Tweet length if you have Twitter blue.
6. Start the bot with 
    ```
    nohup python3 twitterbot.py &
    ```
    to start the bot and ensure it continues running in the background even when you log out from your server. The bot now posts daily new quotes from the database on the computed posting times.
7. To stop the bot, find out which process ID it has on your system with 
    ```
    ps aux | grep twitterbot
    ```
    and stop it with
    ```
    kill PROCESS_ID
    ```

## Notes
1. The script `database.py` also provides some other useful database related functions.
2. The computed posting times and all the other logs will be written in a `twitterbot.log` file.
3. Since I am German, the time data are in a 24hr format. If you use the AM/PM format, you should change the format variables in the `config.py` file to output (and read) the correct format. You can use `'%I:%M %p'` as time format. However, the code should work for you as well, since the `datetime` modul handles this internally.

## Support

If you use this bot and find it helpful, I'd love to hear about your project! Feel free to share your feedback, suggestions, or just let me know how you're using the bot. You find my email address on my Github profile.

If you like this project, please give it a star ⭐ to show your support and help others find it.