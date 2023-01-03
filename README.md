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

## Usage

```bash
source .venv/bin/activate
# ...

# read all your own tweets, store Q&A as CSV in files in /output/
python3 json_to_csv.py
python3 csv_to_threads.py

# this takes a long time, it fetches the tweets you replied to via Twitter API.
python3 csv_to_qa.py

# that's all folks
deactivate
```

## todos

* compile popular threads to drop onto blog
* export all tweets to csv
* export all posts with images
* stats on tweets/month, tweets/daytime, time-to-reply
