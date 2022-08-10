from __future__ import print_function
from dotenv import load_dotenv

load_dotenv()

import twitter
import asyncio
from os import environ
import feedparser

URL = 'https://calm-wildwood-09447.herokuapp.com/twitterFeed.rss'
data_old = []
urls_dict = {}
blacklist = ["Transparent App Icons", "Dark Noise",
             "Aloha Browser", "The New York Times"]

seen = []


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def fetch_current():
    feed_data = feedparser.parse(URL)
    results = { entry['title']: entry['link'] for entry in feed_data.entries }
    return results


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
            for app in diff:
                if app not in blacklist and app not in seen:
                    seen.append(app)
                    try:
                        status = api.PostUpdate(
                            f'{app} just had a TestFlight spot open up! {urls_dict[app]}')
                        print(f'{status.user.name} posted {status.text}')
                        print(f'Just posted about {app}!')
                    except Exception as e:
                        print(e)
                    asyncio.create_task(remove_seen(app))
                    print("NEW", app + urls_dict[app])
            data_old = data_now
        except Exception as e:
            print("Error in POST")
            print(e)
        finally:
            await asyncio.sleep(60)


async def remove_seen(item):
    await asyncio.sleep(360)
    print("removing", item)
    if item in seen:
        seen.remove(item)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
