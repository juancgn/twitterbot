# Twitterbot

Twitterbot is a Python-based bot for Twitter that reads tweets (called `quotes`) from a local SQLite database and posts them automatically on Twitter. I wrote it to post funny quotes from my favorite character from a CBS show. The bot uses the Tweepy library for interacting with the Twitter API v2 and is designed to post at configurable times. Twitterbot only uses the free-of-charge tools of the Twitter API.

Twitterbot is designed to run permanently and therefore you should run it on a server, a Raspberry Pi oder similar.

## Features

- **Database Connection:** The bot establishes a connection to a local SQLite database that manages quotes, queueing, and post logging.
- **Tweet Posting:** Quotes are posted as Tweets using the Twitter API v2 with Tweepy.
- **Scheduling:** Multiple schedule options are provided which take care of the posting timing
- **Logging:** Events and errors are logged to assist with performance monitoring and troubleshooting.
- **Queueing:** Used quotes will be queued randomly in the second half of the queue, so the quote selection is random enough but an used quote is not posted again too soon.
- **Efficient implementation** Twitterbot uses passive waiting and has therefore a very low CPU usage

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
2. Install requirements with 
    ```
    pip install -r requirements.txt
    ```
## Usage

1. Write your quotes in a new file named `rawdata.txt`, one per line. Ensure they do not exceed the allowed Tweet length. Copy this file to your server using, for example, ssh:

    ```
    scp [-i ssh_private_key] /path/on/your/computer/rawdata.txt username@SERVER_IP:/path/to/directory/of/twitterbot
    ```
2. Create a local SQLite database from the raw data with:
    ```
    python3 database.py
    ```
3. Sign up for a [Twitter developer account](https://developer.x.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api) (the free plan is sufficient) and obtain the credentials from the developer portal.
4. Create a `cred.env` file and add your Twitter API credentials in the following format:
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
6. Run 
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
3. Since I am German, the time data are in a 24hr format. If you use the AM/PM format, you should change the format variables in the `config.py` file to output (and readout) the correct format. You can use `'%I:%M %p'` as time format. I haven't tested this extensively, however, no problems should occur since the `datetime` module handles this internally.
4. Twitter has introduced a [rule](https://help.x.com/en/using-x/automated-account-labels) that automated accounts need to be labeled. For that, a human run account must be connected and will be linked on the profile. Otherwise, Twitter considers the account as a terms-and-conditions-violating account and restricts it.

## Support

If you like this project, please give it a star ⭐ to show your support and help others find it.