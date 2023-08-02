# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import sqlite3

from itemadapter import ItemAdapter


class NewsScraperPipeline:
    conn = sqlite3.connect('news-scraper.db')
    cursor = conn.cursor()

    def open_spider(self, spider):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS `news_scraper` (
                                                                            title varchar(100),
                                                                            body text,
                                                                            date datetime,
                                                                            url text,
                                                                            is_sent number(2)
                                                                            )''')
        self.conn.commit()

    def process_item(self, item, spider):
        try:
            title = item['title'].replace("'", '"').replace('`', '"')
        except:
            title = ''
        try:
            body = item['body'].replace("'", '"').replace('`', '"')
        except:
            body = ''
        try:
            date = item['date']
        except:
            date = datetime.datetime.now()
        try:
            url = item['url']
        except:
            url = ''

        self.cursor.execute(f"""select * from news_scraper where  url = '{url}'""")
        is_exist = self.cursor.fetchall()

        if len(is_exist) == 0:
            self.cursor.execute(
                f"""insert into `news_scraper` (`title`, `body`, `date`, `url`, `is_sent`) values ('{title}', '{body}', '{date}', '{url}', 0)""")
            self.conn.commit()

        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
