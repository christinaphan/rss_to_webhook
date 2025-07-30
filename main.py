#!/usr/bin/env python

import csv
import os
from dotenv import load_dotenv
import feedparser
import requests

load_dotenv()

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

FEED_INFO_FILE = os.environ["FEED_INFO_FILE"]
LAST_SEEN_FILE = os.environ["LAST_SEEN_FILE"]

# Default feeds
default_feeds = [
    "https://feeds.feedburner.com/TheDailyWtf",
    "https://xkcd.com/atom.xml",
    "https://hnrss.org/frontpage?description=0&count=5",
]

# Load feed metadata
feed_urls = []
feed_etags = []
feed_last_modified = []

if os.path.exists(FEED_INFO_FILE):
    with open(FEED_INFO_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            url = row[0]
            etag = row[1] if len(row) > 1 else ""
            last_mod = row[2] if len(row) > 2 else ""
            feed_urls.append(url)
            feed_etags.append(etag)
            feed_last_modified.append(last_mod)
else:
    feed_urls = default_feeds
    feed_etags = ["" for _ in feed_urls]
    feed_last_modified = ["" for _ in feed_urls]

last_seen_ids = {}
if os.path.exists(LAST_SEEN_FILE):
    with open(LAST_SEEN_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                last_seen_ids[row[0]] = row[1]

new_feed_etags = []
new_feed_last_modified = []
new_last_seen_ids = {}

# Main loop
for feed_url, etag, last_mod in zip(feed_urls, feed_etags, feed_last_modified):
    d = feedparser.parse(feed_url, etag=etag, modified=last_mod)

    new_feed_etags.append(d.get("etag", ""))
    new_feed_last_modified.append(d.get("modified") if d.get("modified") else "")

    if d.get("status") == 304 or (last_mod and new_feed_last_modified[-1] == last_mod):
        continue

    last_seen_id = last_seen_ids.get(feed_url)

    # Post only new entries
    new_entries = []
    for entry in d.entries:
        entry_id = entry.get("id") or entry.get("link")
        if entry_id == last_seen_id:
            break
        new_entries.append(entry)

    for entry in reversed(new_entries):
        entry_data = {
            "content": entry.get("link", ""),
            "username": d.feed.get("title", "Feed Bot"),
        }

        if feed_url == "https://hnrss.org/frontpage?description=0&count=5":
            entry_data["content"] = entry.get("comments", "")

        requests.post(DISCORD_WEBHOOK_URL, json=entry_data)

    if d.entries:
        newest_entry = d.entries[0]
        newest_id = newest_entry.get("id") or newest_entry.get("link")
        new_last_seen_ids[feed_url] = newest_id

with open(FEED_INFO_FILE, "w", newline="") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    for url, etag, mod in zip(feed_urls, new_feed_etags, new_feed_last_modified):
        writer.writerow([url, etag, mod])

with open(LAST_SEEN_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    for url in feed_urls:
        last_id = new_last_seen_ids.get(url, last_seen_ids.get(url, ""))
        writer.writerow([url, last_id])
