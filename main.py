#!/usr/bin/env python3

import sys
import argparse
import re
import configparser
import time
import random

import irc.client
import irc.logging

from queuebot import QueueBot

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c',
                       default='config.ini',
                       help='Specify which config file to use (default: config.ini)')
    parser.add_argument('--target', '-t',
                       default=None,
                       help='Specify what channel to join')
    irc.logging.add_arguments(parser)
    return parser.parse_args()

args = get_args()

thismodule = sys.modules[__name__]
config = configparser.ConfigParser()

res = config.read(args.config)

if len(res) == 0:
    print('config.ini missing. Check out config.example.ini for the relevant data')
    sys.exit(0)

if not 'main' in config:
    print('Missing section [main] in config.ini')
    sys.exit(0)

def main():
    global args

    target = args.target if args.target else config['main']['target']

    irc.logging.setup(args)

    queuebot = QueueBot(target, config)

    try:
        queuebot.connect()
    except irc.client.ServerConnectionError as x:
        print(x)
        sys.exit(1)

    try:
        queuebot.start()
    except KeyboardInterrupt:
        queuebot.quit()
        pass

if __name__ == "__main__":
    main()
