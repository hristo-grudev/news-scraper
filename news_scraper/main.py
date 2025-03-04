import os
import subprocess

spiders = ["vik_gabrovo", "energo_pro"]
project_directory = r"D:\news-scraper\news_scraper"

for spider in spiders:
    os.chdir(project_directory)
    subprocess.run([r"D:\news-scraper\venv\Scripts\python.exe", "-m", "scrapy", "crawl", spider])
