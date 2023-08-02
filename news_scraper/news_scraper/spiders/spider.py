from datetime import datetime

import scrapy

from scrapy.loader import ItemLoader

from .helper import sqlite_query
from ..items import NewsScraperItem
from itemloaders.processors import TakeFirst


class VikGabrovoSpider(scrapy.Spider):
    name = 'vik_gabrovo'
    start_urls = [
        'https://www.vik-gabrovo.com/avarii-i-remonti'
    ]

    def parse(self, response):
        news_links = response.xpath('//h2/a/@href').getall()
        data = sqlite_query(f"""select distinct url from news_scraper""")
        existing_links = [link[0] for link in data]
        print(existing_links)
        for news_link in news_links:
            if f'https://www.vik-gabrovo.com{news_link}' not in existing_links:
                yield response.follow(news_link, self.parse_data)

        # next_page = response.xpath('//ul[@class="pagination ms-0 mb-4"]//a/@href').getall()
        # yield from response.follow_all(next_page, self.parse)

    def parse_data(self, response):
        title = response.xpath('//h1[@itemprop="headline"]/text()').get()
        body = response.xpath('//div[@itemprop="articleBody"]//text()').getall()
        body = ''.join(body)
        date = response.xpath('//time/@datetime').get().split('+')[0]
        datetime_object = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")

        print(title, body, datetime_object, response.url)

        if not title:
            print('NPO: ', response.text)
        item = ItemLoader(item=NewsScraperItem(), response=response)
        item.default_output_processor = TakeFirst()
        item.add_value('title', title.strip())
        item.add_value('body', body.strip())
        item.add_value('date', date)
        item.add_value('url', response.url)

        yield item.load_item()
