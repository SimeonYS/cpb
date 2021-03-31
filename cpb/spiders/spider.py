import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CpbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CpbSpider(scrapy.Spider):
	name = 'cpb'
	start_urls = ['https://www.cpb.bank/resources?page=1']

	def parse(self, response):
		post_links = response.xpath('//a[@class="aTeal"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="nxt-link"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="col-12 col-sm-9"]/strong/text()').get().strip('\xa0|\xa0 ')
		title = response.xpath('//h3[@class="heading"]/text()').get()
		content = response.xpath('//div[@class="content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CpbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
