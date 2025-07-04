import requests
import os

from dotenv import load_dotenv
import feedparser

load_dotenv()

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

feed_urls = ["https://feeds.feedburner.com/TheDailyWtf", "https://xkcd.com/atom.xml"]


for feed_url in feed_urls:
    d = feedparser.parse(feed_url)
    for entry in d.entries:
        entry_data = {
            "content": entry.summary,
            "username": d.feed.title,
        }

        # if xkcd

        requests.post(DISCORD_WEBHOOK_URL, json=entry_data)
