#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-Short-Identifier: MIT
# (c) 2023 John Mueller / johnmu.com
# This code is licensed under MIT license (See LICENSE for details)

#
# Twitter CSV exporter. Run this first.
#
# - Processes unzipped Twitter archive from folder twitter/
# - Creates tweets.csv in folder output/
# - Does not use Twitter API, does hacky incremental parsing of JSON file for speed
#

import csv
import os
import html
import signal
import datetime
import json
import email.utils

abort=False # I feel dirty, lol

# handle ctrl-c gracefully
def handler(signum, frame):
    global abort
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        print("Aborting next possible...")
        abort=True
        exit(1)

# write to CSV file
def write_data(filename, dataset, include_header):
    if not len(dataset):
        print(datetime.datetime.now().isoformat(), " - Warning: len(dataset)==0 for ", filename)
        return
    print(datetime.datetime.now().isoformat(), 
        " - Writing {:d} entries to {:s}".format(len(dataset), filename))
    write_type = include_header and "w" or "a"
    with open(filename, write_type, newline='') as csvfile:
        fieldnames = dataset[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="\t")
        if include_header: writer.writeheader()
        for row in dataset: writer.writerow(row)
    # done

# clean text used in tweets; parse HTML, remove CSV-breaking characters
def clean_text(input):
    res = input
    if "&" in res: res = html.unescape(res)
    res = res.replace('"', "'").replace("\n", " ").replace("\t", " ")
    return res

# parse the twitter JS blob into a dictionary
def parse_dict(input):
    ret = {}
    t = input["tweet"]
    ret["created_at"] = email.utils.parsedate_to_datetime(t["created_at"]).isoformat()
    ret["id"] = t["id_str"]
    ret["reply_id"] = (
        "in_reply_to_status_id_str" in t and t["in_reply_to_status_id_str"] or "")
    ret["likes"] = t["favorite_count"]
    ret["shares"] = t["retweet_count"]
    ret["urls"] = ",".join([x["expanded_url"] for x in t["entities"]["urls"]])
    ret["full_text"] = clean_text(t["full_text"])
    return ret

# read file, parse, write it
def main():
    global abort
    signal.signal(signal.SIGINT, handler)

    # paths and filenames hardcoded
    input_filename = os.path.join("twitter", "data", "tweets.js")
    output_filename = os.path.join("output", "tweets.csv")

    is_first_part = True
    include_header = True
    tweet_counter = 0
    line_counter = 0

    dataset = []
    with open(input_filename, "r") as tweets_file:
        buffer = []
        while True:
            if abort: break
            line = tweets_file.readline()
            if not line: break # done
            line_counter += 1
            if (line.strip().startswith("\"tweet\"") or line=="]"):
                if line=="]": buffer.append("(unused)") # hack for end of file
                if not is_first_part: 
                    tweet_data = json.loads("{" + "".join(buffer[:-2]) + "}")
                    tweet_counter += 1
                    item = parse_dict(tweet_data)
                    dataset.append(item)
                    if tweet_counter % 200 == 0:
                        write_data(output_filename, dataset, include_header)
                        include_header = False
                        dataset = []
                else:
                    is_first_part = False
                buffer = [line]
            else:
                buffer.append(line)
    # done
    if dataset:
        write_data(output_filename, dataset, include_header)
    print("done, processed {:d} lines for {:d} tweets".format(line_counter, tweet_counter))

if __name__ == '__main__':
    main()