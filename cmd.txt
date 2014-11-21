scrapy crawl craigslistRent -o temp-rentals.csv -t csv
scrapy crawl latlongSpider -o temp-latlong.csv -t csv
python MergeData.py