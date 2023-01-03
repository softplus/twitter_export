#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-Short-Identifier: MIT
# (c) 2023 John Mueller / johnmu.com
# This code is licensed under MIT license (See LICENSE for details)

#
# Twitter CSV exporter. Converts the Tweets CSV file into a CSV of your threads
#
# - Reads output/tweets.csv
# - Finds top post, builds your threads
# - Tracks max likes, max shares across all posts in thread
# - Stores thread text with " | " separators
# - Writes to output/threads.csv
# - Doesn't use API
#

import csv
import os
import signal
import datetime

abort=False

# handle ctrl-c gracefully
def handler(signum, frame):
    global abort
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        print("Aborting next possible...")
        abort=True
        exit(1)

# write CSV file
def write_data(filename, dataset):
    localfn = "threads.csv"
    fn = os.path.join("output", localfn)
    if not len(dataset):
        print(datetime.datetime.now().isoformat(), " - Warning: len(dataset)==0 for ", fn)
        return

    print(datetime.datetime.now().isoformat(), 
        " - Writing {:d} lines to {:s}".format(len(dataset), fn))
    with open(fn, 'w', newline='') as csvfile:
        fieldnames = dataset[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="\t")

        writer.writeheader()
        for r in dataset: writer.writerow(r)
    # done

# read the collected CSV file
def read_csv(filename):
    res = []
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        for row in reader: res.append(row)
    return res

# do the stuff
def main():
    global abort
    signal.signal(signal.SIGINT, handler)

    input_filename = os.path.join("output", "tweets.csv")
    output_filename = os.path.join("output", "threads.csv")

    tweets = read_csv(input_filename)
    print("Loaded {:d} tweets".format(len(tweets)))

    threads = []
    ids = [x["id"] for x in tweets]

    print("Seeking thread starters")
    for i in range(len(tweets), 0, -1):
        if abort: break
        t = tweets[i-1]
        if t["reply_id"] not in ids:
            threads.append(t | {
                "last_id": t["id"], "max_likes": int(t["likes"]), 
                "max_shares": int(t["shares"]), "length": 1})
            del tweets[i-1]
    
    print("Found {:d} threads, have {:d} tweets remaining".format(len(threads), len(tweets)))

    while True:
        if abort: break
        found = 0
        last_ids = [x["last_id"] for x in threads]
        for i in range(len(tweets), 0, -1):
            t = tweets[i-1]
            if t["reply_id"] in last_ids:
                idx = last_ids.index(t["reply_id"])
                th = threads[idx]
                th["full_text"] += " | " + t["full_text"]
                if t["urls"]: th["urls"] += (th["urls"] and ",") + t["urls"]
                th["max_likes"] = max(th["max_likes"], int(t["likes"]))
                th["max_shares"] = max(th["max_shares"], int(t["shares"]))
                th["last_id"] = t["id"]
                th["length"] += 1
                del tweets[i-1]
                found += 1
        if found == 0: break
        print("Now {:d} threads, have {:d} tweets remaining".format(len(threads), len(tweets)))

    print("Removing individual posts...")
    for i in range(len(threads), 0, -1):
        if threads[i-1]["length"] == 1: del threads[i-1]

    print("")
    print("Final: Have {:d} threads, have {:d} tweets remaining".format(len(threads), len(tweets)))
    print("")
    print("Remaining tweets:")
    for row in tweets: print(row)

    write_data(output_filename, threads)

if __name__ == '__main__':
    main()