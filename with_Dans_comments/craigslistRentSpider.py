from datetime import datetime, date
from scrapy.spider import Spider #[dan]for spiders
from scrapy.selector import Selector #[dan]for xpath
from scrapy.http import Request #[dan]for making the actual http request to web server
from scrapy.utils.response import get_base_url # [dan]for working with url strings
from craigslistRentScraper.items import CraigslistRentItem #[dan]our data model in items.py

class MySpider(Spider):
	name = 'craigslistRent'
	allowed_domains = ['craigslist.org']
	# [dan] subregions of the bay area, and the apartment listings within each region
	start_urls = [
		"http://washingtondc.craigslist.org/sfc/search/apa",
		"http://washingtondc.craigslist.org/sfc/search/apa?s=100",
        "http://washingtondc.craigslist.org/sfc/search/apa?s=200",
		"http://washingtondc.craigslist.org/sfc/search/apa?s=300",
		"http://washingtondc.craigslist.org/sfc/search/apa?s=400"
	]
	
	
	# [dan] define cleaning functions

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
		
		
	
	# [dan] the parser extracts specific things from the webpage once we retrieve it. using xpath
	def parse(self, response):
		
		#create the xpath selector to parse our document
		selection = Selector(response)

		#each posting's root node is the 'row' p class
		#[dan] if you View Source of http://sfbay.craigslist.org/search/eby/apa in your browser
		#[dan] you can see where the HTML for all the listings start. the HTML looks like <p class="row" data-pid="[blahblah]"[etc etc]....
		#[dan] craigslistRentScraper/clistsample.html has an example. in the first 20 lines he reformatted one entry so it's clearer what the hierarchy of HTML elements is
		rows = selection.xpath("//p[@class='row']")
		items = []
		
		for row in rows:

			# [dan] make a new CraigsListRentItem class object (see items.py)			
			item = CraigslistRentItem()

			# [dan] fill out each field within the object			
			#extract the date and time
			# [dan] this is within the <span class="txt"> <span class="pl"><time>. we're getting the "datetime" attribute
			# [dan] extract() returns a list of everything it finds. we only have one thing, so it's a single-element list. ''.join() will basically make it into a string (joins a list with empty string)
			date_time = ''.join(row.xpath("span[@class='txt']/span[@class='pl']/time/@datetime").extract())
			item['date'] = date_time
			
			#extract the ID from the 'row' p class
			# [dan] this field doesn't have to join a list because this query could only match one possible attribute (we're just getting the data-pid attribute for the row, rather than "every possible _____" that matches)
			# [dan] so it only returns one item all the time, rather than a list
			item['pid'] = row.xpath('@data-pid').extract()
			
			#extract and clean the price
			pri = ''.join(row.xpath("span[@class='txt']/span[@class='l2']/span[@class='price']/text()").extract())
			# [dan] call the cleanPriceString() thing we defined earlier. it strips the dollar sign
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
			# [dan] the link that we have in the HTML is a relative link, not the entire URL. For example, <a href="/nby/apa/4753814686.html"> is not the entire URL
			# [dan] we take part of the source URL, then add on the rest
			link = ''.join(row.xpath("span[@class='txt']/span[@class='pl']/a/@href").extract())
			base = base[0:base.find('.org/')+4]
			item['link'] = base + link
			
			#add this item to the list of items
			items.append(item)
			
		return items
		
		
		