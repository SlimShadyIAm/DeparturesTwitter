from __future__ import print_function

try:
    import configparser
except ImportError as _:
    import ConfigParser as configparser

import getopt
import sys
import twitter
import asyncio
from os import environ
import aiohttp
from bs4 import BeautifulSoup, element

URL = 'https://departures.to/'
WEBHOOK_URL = environ.get("TESTFLIGHT")
data_old = []
urls_dict = {}
blacklist = ["Transparent App Icons", "Dark Noise",
             "Aloha Browser", "The New York Times"]
seen = []


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def fetch_current():
    current_apps = []
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, URL)
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all(class_='columns')

        for result in results:
            try:
                if isinstance(result, element.Tag):
                    if result.find('p', class_="has-text-success") is not None:

                        time = result.find(
                            'p', class_="has-text-light").text.strip()
                        try:
                            if ("second" in time) or ("minute" in time and int(time.split()[0]) < 5) or ("now" in time):
                                name = result.find(
                                    'p', class_="has-text-warning").text.strip()

                                urls_dict[name] = f'https://departures.to{result.find_parent("a")["href"]}'
                                current_apps.append(name)
                        except ValueError:
                            pass
            except Exception as e:
                print("Error in main()")
                print(e)

    return current_apps


async def main():
    api = twitter.Api(consumer_key=environ.get("DEP_CONS"),
                      consumer_secret=environ.get("DEP_CONS_SEC"),
                      access_token_key=environ.get("DEP_ACC"),
                      access_token_secret=environ.get("DEP_ACC_SEC"))

    data_old = await fetch_current()
    print(data_old)

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
