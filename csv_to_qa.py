#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-Short-Identifier: MIT
# (c) 2023 John Mueller / johnmu.com
# This code is licensed under MIT license (See LICENSE for details)

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
    auth = tweepy.OAuth2BearerHandler(settings.TWITTER_API_TOKEN)
    api= tweepy.API(auth, wait_on_rate_limit=True)
    client = tweepy.Client(settings.TWITTER_API_TOKEN)
    signal.signal(signal.SIGINT, handler)

# write output
def write_data(filename, dataset, include_header):
    if not len(dataset):
        print(datetime.datetime.now().isoformat(), " - Warning: len(dataset)==0 for ", filename)
        return
    print(datetime.datetime.now().isoformat(), 
        " - Writing {:d} lines to {:s}".format(len(dataset), filename))
    write_type = include_header and "w" or "a"
    with open(filename, write_type, newline='') as csvfile:
        fieldnames = dataset[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="\t")
        if include_header: writer.writeheader()
        for r in dataset: writer.writerow(r)
    # done

# clean twitter texts for CSV files
def clean_text(input):
    res = input
    if "&" in res: res = html.unescape(res)
    res = res.replace('"', "'").replace("\n", " ").replace("\t", " ")
    return res

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

    input_filename = os.path.join("output", "tweets.csv")
    output_filename = os.path.join("output", "qa.csv")

    tweets = read_csv(input_filename)
    print("Loaded {:d} tweets".format(len(tweets)))
    ids = [x["id"] for x in tweets]
    filtered = []
    for row in tweets:
        if abort: break
        if not row["reply_id"]: continue
        if row["reply_id"] in ids: continue
        filtered.append(row)
    tweets = filtered
    print("Dropped all but {:d} tweets".format(len(tweets)))
    
    skip_lines = 0
    line_count = 0
    dataset = []
    include_header = (skip_lines==0)

    # Fetch tweets from timeline a page at a time, if a reply
    for status in tweets:
        if abort: break
        line_count += 1
        if line_count < skip_lines: continue

        last_id = status["id"]
        time.sleep(0.1)
        if line_count%20==0:
            print(datetime.datetime.now().isoformat(), 
                " - Last ID: {:s}, line: {:d} of {:d}".format(last_id, line_count, len(tweets)))

        try:
            reply_to = api.get_status(status["reply_id"], tweet_mode="extended")
        except:
            print("Couldn't find ID ", status["reply_id"], 
                " for your ", status["id"], " " , status["full_text"][:40])
            continue

        if not reply_to:
            print("Couldn't fetch reply ", status["reply_id"], 
                " for your ", status["id"], " " , status["full_text"][:40])
            continue

        item = {}
        item["op_date"] = reply_to.created_at.isoformat()
        item["op_user"] = reply_to.user.screen_name
        item["op_post"] = clean_text(reply_to.full_text)
        item["op_id"] = reply_to.id_str
        item["op_urls"] = ",".join([x["expanded_url"] for x in reply_to.entities["urls"]])
        item["reply_date"] = status["created_at"]
        item["reply_post"] = clean_text(status["full_text"])
        item["reply_urls"] = status["urls"]
        item["reply_id"] = status["id"]
        item["op_likes"] = reply_to.favorite_count
        item["op_shares"] = reply_to.retweet_count
        item["reply_likes"] = status["likes"]
        item["reply_shares"] = status["shares"]
        dataset.append(item)

        if len(dataset)>100:
            write_data(output_filename, dataset, include_header)
            include_header = False
            dataset = []

    if len(dataset):
        write_data(output_filename, dataset, include_header)

if __name__ == '__main__':
    main()
