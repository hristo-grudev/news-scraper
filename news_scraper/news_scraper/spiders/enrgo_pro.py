import json
import re

import scrapy

from scrapy.loader import ItemLoader

from .helper import sqlite_query
from ..items import NewsScraperItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.energo-pro.bg/bg/profil/xhr/?method=get_interruptions&region_id=3&type=for_next_48_hours"

payload = {}
headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=utf-8',
        'Cookie': 'STDXFWSID=asu4cq8v90dmrn5gc3ca78g02c; _ga=GA1.1.1176135259.1741074850; _ga_3DVMXYKJCR=GS1.1.1741074850.1.1.1741074869.0.0.0',
        'Referer': 'https://www.energo-pro.bg/bg/planirani-prekysvanija',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
}


def clean_new_line(data):
    new_data = [el.strip() for el in data.splitlines()]
    return ' '.join(new_data)


class EnergoProSpider(scrapy.Spider):
    name = 'energo_pro'
    start_urls = [
        'https://www.energo-pro.bg/'
    ]

    def parse(self, response):
        response = requests.request("GET", url, headers=headers, data=payload)
        data = json.loads(response.text)
        addresses_data = sqlite_query('SELECT DISTINCT address '
                                      'FROM holidays')

        regex_date = r'\d{1,2}\.\s*\d{1,2}\.\s*\d{2,4}'
        addresses = [a[0] for a in addresses_data if a[0] != None]
        place = ['севлиево', 'столът', 'крушево', 'кoрмянско']
        for i in data:
            if i['area_name'] == 'Габрово':
                for loc in i['area_locations_for_next_48_hours']:
                    title = clean_new_line(loc['location_period'])
                    body_clean = clean_new_line(loc['location_text'].split(' <p class')[0])
                    date = re.match(regex_date, title)
                    link = title + loc['location_id']
                    if any(p.lower() in body_clean.lower() for p in place):
                        print(link)
                        item = ItemLoader(item=NewsScraperItem(), response=response)
                        item.default_output_processor = TakeFirst()
                        item.add_value('title', title.strip())
                        item.add_value('body', body_clean.strip())
                        item.add_value('date', date)
                        item.add_value('url', link.strip())

                        yield item.load_item()
