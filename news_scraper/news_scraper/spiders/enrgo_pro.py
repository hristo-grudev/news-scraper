import json
import re
from datetime import datetime

import bleach
import scrapy
from bleach.sanitizer import Cleaner

from scrapy.loader import ItemLoader

from .helper import sqlite_query, proces_text
from ..items import NewsScraperItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.energo-pro.bg/bg/profil/xhr/?method=get_interruptions&\\{\\}"

payload = {}
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json; charset=utf-8',
    'Cookie': 'STDXFWSID=5bkjf6al8d3v9edudvnh3p1sti',
    'Pragma': 'no-cache',
    'Referer': 'https://www.energo-pro.bg/bg/planirani-prekysvanija',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}


def clean_new_line(data):
    new_data = [el.strip() for el in data.splitlines()]
    return ' '.join(new_data)


class EnergoProSpider(scrapy.Spider):
    name = 'energo_pro'
    start_urls = [
        'https://www.vik-gabrovo.com/avarii-i-remonti'
    ]

    def parse(self, response):
        response = requests.request("GET", url, headers=headers, data=payload)
        data = json.loads(response.text)
        addresses_data = sqlite_query('SELECT DISTINCT address '
                                      'FROM holidays')

        regex_date = r'\d{1,2}\.\s*\d{1,2}\.\s*\d{2,4}'
        addresses = [a[0] for a in addresses_data if a[0] != None]
        place = ['севлиево', 'столът', 'крушево', 'курмянско']
        for i in data:
            if i['area_name'] == 'Габрово':
                for loc in i['area_locations_for_next_48_hours']:
                    title = clean_new_line(loc['location_period'])
                    body_clean = clean_new_line(loc['location_text'].split(' <p class')[0])
                    date = re.match(regex_date, title)
                    link = title + loc['location_id']
                    if any(p.lower() in body_clean.lower() for p in place):
                        item = ItemLoader(item=NewsScraperItem(), response=response)
                        item.default_output_processor = TakeFirst()
                        item.add_value('title', title.strip())
                        item.add_value('body', body_clean.strip())
                        item.add_value('date', date)
                        item.add_value('url', link.strip())

                        yield item.load_item()
