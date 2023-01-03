# twitter_export

Takes your Twitter export file and turns it into CSV files.
Everyone loves CSV files.

MIT license (see file LICENSE).
(c) 2023 John Mueller / johnmu.com
## Setup

```bash
# get repo
git clone https://github.com/softplus/twitter_export
cd twitter_export

# setup python stuff, virtualenv -- recommended
virtualenv .venv && source .venv/bin/activate
pip install -r requirements.txt
# ... run things now ...

# ... when done ...
deactivate
```

## Setup

### Twitter API setup

1. Make a copy of `_settings_sample.py` and call it `_settings.py`
2. Follow the guide at https://python-twitter.readthedocs.io/en/latest/getting_started.html to create a new Twitter app, and to get your tokens.
3. When creating an app, you can use any URL.
4. Copy `API Key`, `API Key Secret`, and `Bearer Token` into the appropriate fields in `_settings.py`

That's all. I think

### Twitter archive

Extract your Twitter archive and place it in the `twitter` folder here.
This folder should include sub-directories for `assets` and `data`.

## Usage

```bash
source .venv/bin/activate
# ...

# read all your own tweets, store Q&A as CSV in files in /output/
python3 json_to_csv.py
python3 csv_to_threads.py

# this takes a long time, it fetches the tweets you replied to via Twitter API.
# note: you must set up the Twitter API first.
python3 csv_to_qa.py

# that's all folks
deactivate
```

## Dependencies

Some of the code uses `tweepy` to access the Twitter API. 

## todos

* compile popular threads to drop onto blog
* export all tweets to csv
* export all posts with images
* stats on tweets/month, tweets/daytime, time-to-reply

## Questions?

Drop me a post at https://johnmu.com/+

