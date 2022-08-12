from __future__ import print_function
from dotenv import load_dotenv

load_dotenv()

import twitter
import asyncio
from os import environ
import feedparser

URL = 'https://calm-wildwood-09447.herokuapp.com/twitterFeed.rss'
data_old = []
urls_to_title = {}
blacklist = ["Transparent App Icons", "Dark Noise",
             "Aloha Browser", "The New York Times"]

seen = []


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def fetch_current():
    feed_data = feedparser.parse(URL)
    for entry in feed_data.entries:
        urls_to_title[entry['link']] = entry['title']
    return [ entry['link'] for entry in feed_data.entries ]


async def main():
    api = twitter.Api(consumer_key=environ.get("DEP_CONS"),
                      consumer_secret=environ.get("DEP_CONS_SEC"),
                      access_token_key=environ.get("DEP_ACC"),
                      access_token_secret=environ.get("DEP_ACC_SEC"))

    data_old = await fetch_current()

    while True:
        try:
            data_now = await fetch_current()
            diff = list(set(data_now) - set(data_old))
            for app_link in diff:
                app_title = urls_to_title[app_link]
                if app_title not in blacklist and app_link not in seen:
                    seen.append(app_link)
                    asyncio.create_task(remove_seen(app_link))
                    status = api.PostUpdate(
                        f'{app_title} just had a TestFlight spot open up! {app_link}')
                    print(f'{status.user.name} posted a new Tweet!\n"{status.text}"')
            data_old = data_now
        except Exception as e:
            print("Error in POST")
            print(e)
        finally:
            await asyncio.sleep(60)


async def remove_seen(item):
    await asyncio.sleep(600)
    print("removing", item)
    if item in seen:
        seen.remove(item)

if __name__ == '__main__':
    print("[✈️] Now watching...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
