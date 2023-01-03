#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-Short-Identifier: MIT
# (c) 2023 John Mueller / johnmu.com
# This code is licensed under MIT license (See LICENSE for details)

# 
# Deletes tweets based on a text-file of IDs
# - reads output/tweets_to_delete.csv with a single column for "id"
# - does the needy
# - uses the Twitter API, obviously
#
# Uses fixed file names to reduce accidental usage.
# 
 
import _settings as settings
import tweepy
import csv
import os
import html
import signal
import time
import datetime

api=None
auth=None
client=None
abort=False

# handle ctrl-c gracefully
def handler(signum, frame):
    global abort
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        print("Aborting next possible...")
        abort=True
        exit(1)

# setup Twitter API, ctrl-c handler
def setup():
    global auth, api, client, abort
    print("This requires OAuth2 dancing, which I'm too lazy to do now. FIx if you want.")
    a = 1/0 # code dies here
    auth = tweepy.OAuth1UserHandler(settings.TWITTER_API_KEY, settings.TWITTER_API_KEY_SECRET,
        settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
    api= tweepy.API(auth, wait_on_rate_limit=True)
    client = tweepy.Client(settings.TWITTER_BEARER_TOKEN)
    signal.signal(signal.SIGINT, handler)

# read the collected CSV file
def read_csv(filename):
    res = []
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        for row in reader: res.append(row)
    return res

# do the stuff
def main():
    global auth, api, client, abort
    setup()

    input_filename = os.path.join("output", "tweets_to_delete.csv")
    print("Reading {:s} ...".format(input_filename))
    tweets = read_csv(input_filename)

    # check for validity: one column called "id"
    if len(tweets[0].keys())>1: 
        print("Too many columns, breaking")
        return
    if "id" not in tweets[0]:
        print("No ID column, breaking")
        return

    print("Loaded {:d} tweets".format(len(tweets)))
    counter = 0
    failed = 0
    for item in tweets:
        if abort: break
        counter += 1
        time.sleep(0.1)
        try:
            api.destroy_status(item["id"])
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            print("Couldn't delete status {:s}".format(item["id"]))
            failed +=1
        if (counter % 100 == 0):
            print("... deleted {:d} tweets, {:d} failed ...".format(counter-failed, failed))
    print("Deleted {:d} tweets, {:d} failed".format(counter-failed, failed))

if __name__ == '__main__':
    main()
