import subprocess

spiders = ["vik_gabrovo", "energo_pro"]

for spider in spiders:
    subprocess.run(["scrapy", "crawl", spider])
