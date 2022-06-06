# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags

def remove_currency(value):
    return value.replace('', '').strip()

class RealEstateItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    address = scrapy.Field()
    postal_code = scrapy.Field()
    price = scrapy.Field()
    image_urls = scrapy.Field()
    agent_name = scrapy.Field()
    agent_link = scrapy.Field()
    full_description = scrapy.Field()
    
    key_features = scrapy.Field()
    building_fabric = scrapy.Field()
    surface_area = scrapy.Field()
    layout = scrapy.Field()
    energy_certificate = scrapy.Field()
    exterior_space = scrapy.Field()
    parking = scrapy.Field()
    
    pass
