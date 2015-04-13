# twitch-queuebot

## About

This is a simple bot for handling queues in twitch chat. Subs have priority over regulars in the queue.

The bot is coded is tested in Python 3.4

## Download

Just clone this git repo!

## Install

The bot depends on one Python dependency, namely the library called `irc`.

    [sudo] pip install irc
    
## Run

Before you run the bot, rename `config.example.ini` to `config.ini` and edit it with your preferred settings.

Once you have installed the dependencies and fixed the config file, run the bot by executing the following command:

`python main.py`

## Commands
Command                     | Description
--------------------------- | ----------------------
!queue join                 | join the queue (only if it's active)
!queue remove USERNAME      | Remove USERNAME from the queue
!queue add USERNAME         | Add USERNAME to the queue
!queue enable               | Start the queue
!queue disable              | Stop the queue
!queue clear                | Clear all participants from the queue
!queue                      | List the participants of the queue (up to ~15)
!queue winner               | Remove the person who's first in the queue and print his name.
