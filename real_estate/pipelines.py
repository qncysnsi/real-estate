# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter
import datetime

class RealEstatePipeline:
    def process_item(self, item, spider):
        
        filename = item['/Users/qncysnsi/Python/real-estate/funda/output/housing-sale-' + datetime.datetime.today().strftime('%Y-%m-%d')]
        
        del item['/Users/qncysnsi/Python/real-estate/funda/output/housing-sale-' + datetime.datetime.today().strftime('%Y-%m-%d')]

        # if the file exists it will append the data 
        JsonItemExporter(open(filename, "w+")).export_item(item)

        return item
    
