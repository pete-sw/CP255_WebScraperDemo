from datetime import datetime, date
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from craigslistRentScraper.items import CraigslistRentItem

class MySpider(Spider):
	name = 'craigslistRent'
	allowed_domains = ['craigslist.org']
	start_urls = [
		"http://washingtondc.craigslist.org/search/apa",
		"http://washingtondc.craigslist.org/search/apa?s=100",
        "http://washingtondc.craigslist.org/search/apa?s=200",
		"http://washingtondc.craigslist.org/search/apa?s=300",
		"http://washingtondc.craigslist.org/search/apa?s=400"
	]
	
	
	
	def cleanPriceString(self, s):
		#remove $ from price string
		s = s.strip('$')
		return s
	
	
	def cleanNeighborhoodString(self, s):
		#remove parentheses and white space padding
		s = s.strip().strip('(').strip(')')
		return s
	
	
	
	def cleanBedroomsString(self, s):
		#if this listing contains number of bedrooms, parse it out
		if('br' in s):
			end = s.find('br')
			begin = s.find('/ ') + 2
			s = s[begin:end]
		else:
			#if there is no bedroom data
			s = ''
		return s
		
		
		
	
	def cleanSqFtString(self, s):
		#if this listing contains square footage, parse it out
		if('ft' in s):
			end = s.find('ft')
			begin = s.find('- ') + 2
			#if there is square footage data but no number of bedrooms, look for a different substring beginning token
			if(begin > end): 
				begin = s.find('/ ') + 2
			s = s[begin:end]
		else:
			#if there is no sqft data
			s = ''
		return s
		
		
		
	
	def parse(self, response):
		
		#create the xpath selector to parse our document
		selection = Selector(response)

		#each posting's root node is the 'row' p class
		rows = selection.xpath("//p[@class='row']")
		items = []
		
		for row in rows:
			
			item = CraigslistRentItem()
			
			#extract the date and time
			date_time = ''.join(row.xpath("span[@class='txt']/span[@class='pl']/time/@datetime").extract())
			item['date'] = date_time
			
			#extract the ID from the 'row' p class
			item['pid'] = row.xpath('@data-pid').extract()
			
			#extract and clean the price
			pri = ''.join(row.xpath("span[@class='txt']/span[@class='l2']/span[@class='price']/text()").extract())
			item['price'] = [self.cleanPriceString(pri)]
			
			#extract and clean the neighborhood data
			nhood = ''.join(row.xpath("span[@class='txt']/span[@class='l2']/span[@class='pnr']/small/text()").extract())
			item['neighborhood'] = [self.cleanNeighborhoodString(nhood)]
			
			#extract and clean the number of bedrooms and square footage
			bedroomsAndSqFt = ''.join(row.xpath("span[@class='txt']/span[@class='l2']/span[@class='housing']/text()").extract())
			item['bedrooms'] = [self.cleanBedroomsString(bedroomsAndSqFt)]
			item['sqft'] = [self.cleanSqFtString(bedroomsAndSqFt)]
			
			#extract the title
			item['title'] = row.xpath("span[@class='txt']/span[@class='pl']/a/text()").extract()
			
			#extract the URL of the page this listing was on from the response object
			base = response.url
			item['sourcepage'] = [base]
			
			#extract and build the link
			link = ''.join(row.xpath("span[@class='txt']/span[@class='pl']/a/@href").extract())
			base = base[0:base.find('.org/')+4]
			item['link'] = base + link
			
			#add this item to the list of items
			items.append(item)
			
		return items
		
		
		