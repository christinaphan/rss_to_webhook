#!/usr/bin/env python

import json
import os

from dotenv import load_dotenv
import feedparser
import requests

load_dotenv()

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
FEED_INFO_JSON = "./feed_info.json"

feed_urls = ["https://feeds.feedburner.com/TheDailyWtf", "https://xkcd.com/atom.xml"]

feed_etags = []
feed_last_modified = []
# load up previous etags and last modified ??
with open(FEED_INFO_JSON, "r") as file:
    feed_etags_dict = json.load(file)
    for feed_url in feed_urls:
        feed_etags.append(feed_etags_dict.get(feed_url, ""))
        feed_last_modified.append(feed_etags_dict.get(feed_url, ""))

for feed_url, feed_etag, feed_last_modified in zip(
    feed_urls, feed_etags, feed_last_modified
):
    d = feedparser.parse(feed_url, etag=feed_etag, modified=feed_last_modified)
    if d.status == 304:
        # feed has not changed since last request
        continue

    for entry in d.entries:
        entry_data = {
            "content": entry.summary,
            "username": d.feed.title,
        }

        # if xkcd

        requests.post(DISCORD_WEBHOOK_URL, json=entry_data)

    # write etag and last modified
    with open(FEED_INFO_JSON, "w") as file:
        pass
