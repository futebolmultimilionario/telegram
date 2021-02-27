import requests
import re
from furl import furl

from telethon import types  #events, functions, Button

LINK_REGEX = r"(?:https.//|http://)((amzn.to/|bit.ly/|fkrt.it/)([a-zA-Z0-9\-_]{7,10}))"
AMAZON_REFERRAL = "empty"
FLIPKART_REFERRAL = "empty"


def redirect(url):
    r = requests.get(url, allow_redirects=True)
    return r.url


def url_parser(event):
    text = event.text
    regex = re.search(LINK_REGEX, text)
    if regex is not None:
        link_redirect = redirect(regex.group(0))
        if "amazon" in link_redirect:
            link_parsed = furl(link_redirect)
            link_parsed.set({"tag": AMAZON_REFERRAL})
            text = text.replace(regex.group(0), link_parsed.url)
        elif "flipkart" in link_redirect:
            link_parsed = furl(link_redirect)
            link_parsed.set({"affid": FLIPKART_REFERRAL})
            text = text.replace(regex.group(0), link_parsed.url)
        return text
    else:
        pass


async def button_copier(event):
    text = {}
    n = 0
    for button_list in event.buttons:
        for button in button_list:
            if isinstance(button.button, types.KeyboardButtonCallback):
                n += 1
                res = await button.click()
                text[n] = res.message
    return text
