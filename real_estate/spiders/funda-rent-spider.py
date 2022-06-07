# packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import datetime
import json

from real_estate.items import RealEstateItem

# housing sale property scraper class
class HousingSale(scrapy.Spider):
    # scraper name
    name = 'funda-for-rent'

    # base URL
    base_url = 'https://www.funda.nl/en/'

    # custom headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    # custom settings
    custom_settings = {
        'CONCURRENT_REQUEST_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1

    }

    # postal code area radius (default: 0km)
    area_radius = 0

    # current page counter
    current_page = 0

    # range postcodes
    postcode_range = range(1811, 1812)

    # crawler's entry point
    def start_requests(self):

        # init filename
        filename = '/Users/qncysnsi/Python/real-estate/funda/output/housing-sale-' + \
            datetime.datetime.today().strftime('%Y-%m-%d')  # -%H-%M')

        # loop over the range of postcodes
        for postcode in self.postcode_range:
            # reset current page counter
            self.current_page = 1
            # postcodes count
            count = 1
            # generate next postcode link
            next_postcode = self.base_url
            next_postcode += 'huur/' + \
                str(postcode) + '/+' + str(self.area_radius) + \
                'km/p' + str(self.current_page)
            # crawl next postcode link
            yield scrapy.Request(
                url=next_postcode,
                headers=self.headers,
                meta={
                    'postcode': postcode,
                    'filename': filename,
                    'count': count
                },
                callback=self.parse_links
            )
            # increment postcodes count
            count += 1
            break
        
    # parse links

    def parse_links(self, response):
        # extract meta data
        postcode = response.meta.get('postcode')
        filename = response.meta.get('filename')
        count = response.meta.get('count')

        # loop over property cards
        for card in response.css('div[class="search-result-main"]'):
            listening_url = card.css('a::attr(href)').get()

            # crawl listening URL
            yield response.follow(
                url=listening_url,
                headers=self.headers,
                meta={
                    'postcode': postcode,
                    'filename': filename
                },
                callback=self.parse_listing
            )

        # handeling pagination within each postcode URL
        try:
            try:
                # extract total pages
                total_pages = response.css('div[class="pagination-pages"]')
                total_pages = total_pages.css('a *::text').getall()
                total_pages = max([
                    int(page.replace('\r\n', '').strip())
                    for page in total_pages
                    if page.replace('\r\n', '').strip().isdigit()
                ])

                # increment current page counter
                self.current_page += 1
                total_pages = 1

            except:
                total_pages = 1
                self.current_page = 1

                # check the if current page is within the legal page range
            if self.current_page <= total_pages:
                # generate next page URL
                next_page = self.base_url
                next_page += 'koop/' + \
                    str(postcode) + '/+' + str(self.area_radius) + \
                    'km/p' + str(self.current_page)
                print('NEXT PAGE:', next_page)

                # print debug information
                print('PAGE %s | %s' % (self.current_page, total_pages))

                # crawl next page
                yield response.follow(
                    url=next_page,
                    headers=self.headers,
                    meta={
                        'postcode': postcode,
                        'filename': filename,
                        'count': count
                    },
                    callback=self.parse_links
                )
        except:
            pass

    # parse property listing
    def parse_listing(self, response):

        item = RealEstateItem()
        # extract meta data
        # postcode = response.meta.get('postcode')
        filename = response.meta.get('filename')
        # title = response.meta.get('title')

        # 'id':                   response.css().url.split('huis-')[1].split('-')[0],
        # 'url':                  response.url,

        item['title'] = response.css(
            'span[class="object-header__title"]::text').get(),

        item['address'] = ', '.join(list(filter(None, [
            text.get().replace('\n', '').strip()
            for text in
            response.css(
                'h1[class="fd-m-top-none fd-m-bottom-xs fd-m-bottom-s--bp-m"] *::text')
        ]))),
        item['postal_code'] = response.css(
            'span[class="object-header__subtitle fd-color-dark-3"]::text').get().replace('\n', '').strip(),

        item['price'] = response.css(
            'strong[class="object-header__price"]::text').get(),
        item['image_urls'] = '',

        item['agent_name'] = response.css(
            'a[class="object-contact-aanbieder-link"]::text').get(),

        item['agent_link'] = 'https://www.funda.nl' + \
            response.css(
                'a[class="object-contact-aanbieder-link"]::attr(href)').get(),

        item['full_description'] = list(filter(None, [
            text.get().replace('\n', '').strip()
            for text in
            response.css(
                'div[class="object-description-body"] *::text')
        ])),

        item['key_features'] = [],
        item['building_fabric'] = [],
        item['surface_area'] = [],
        item['layout'] = [],
        item['energy_certificate'] = [],
        item['exterior_space'] = [],
        item['parking'] = []

### key features extraction ###
        try:
            # key features
            key_features = {}

            # extract feature selector
            feature_selector = response.css(
                'h3[class="object-kenmerken-list-header"] + dl[class="object-kenmerken-list"]')

            # extract feature keys
            feature_keys = list(filter(None, [
                val.replace('\n', '').strip()
                for val in
                Selector(text=feature_selector.get()).css(
                    'dt *::text').getall()
            ]))

            # extract feature values
            feature_vals = (list(filter(None, [
                val.replace('\n', '').strip()
                for val in
                Selector(text=feature_selector.get()).css(
                    'dd *::text').getall()
            ])))

            del feature_vals[2:4]

            # combine keys and values into a dictionary
            for index in range(0, len(feature_vals)):
                key_features[feature_keys[index]] = feature_vals[index]

            # store key features
            item['key_features'] = key_features

        except:
            pass

#### building fabric extraction ###
        try:

            # headers
            headers = response.css('h3[class="object-kenmerken-list-header"]')

            # key features
            key_features = {}

            # init construction index
            construction_index = None

            for index in range(0, len(headers)):
                if headers[index].css('::text').get() == 'Construction':
                    construction_index = index

            # extract feature selector
            feature_selector = response.css(
                'h3[class="object-kenmerken-list-header"] + dl[class="object-kenmerken-list"]')
            feature_selector = feature_selector[construction_index]

            # extract feature keys
            feature_keys = Selector(text=feature_selector.get()).css(
                'dt *::text').getall()

            # extract feature values
            feature_vals = (list(filter(None, [
                val.replace('\n', '').strip()
                for val in
                Selector(text=feature_selector.get()).css(
                    'dd *::text').getall()
            ])))

            # combine keys and values into a dictionary
            for index in range(0, len(feature_vals)):
                key_features[feature_keys[index]] = feature_vals[index]

            # store key features
            item['building_fabric'] = key_features

        except:
            pass


#### surface area extraction ###
        try:

            # headers
            headers = response.css('h3[class="object-kenmerken-list-header"]')

            # key features
            key_features = {}

            # init construction index
            construction_index = None

            for index in range(0, len(headers)):
                if headers[index].css('::text').get() == 'Surface areas and volume':
                    construction_index = index

            # extract feature selector
            feature_selector = response.css(
                'h3[class="object-kenmerken-list-header"] + dl[class="object-kenmerken-list"]')
            feature_selector = feature_selector[construction_index]

            # extract feature keys
            feature_keys = Selector(text=feature_selector.get()).css(
                'dt *::text').getall()

            feature_keys = feature_keys[3:]

            # extract feature values
            feature_vals = (list(filter(None, [
                val
                .replace('\n', '').strip()
                .replace('\n\n', '').strip()
                .replace('\n', '').strip()
                for val in
                Selector(text=feature_selector.get()).css(
                    'span *::text').getall()
            ])))

            # combine keys and values into a dictionary
            for index in range(0, len(feature_vals)):
                feature_vals = [item.replace("\u20ac ", "")
                                for item in feature_vals]
                key_features[feature_keys[index]] = feature_vals[index]

            # store key features
            item['surface_area'] = key_features
        except:
            pass

#### layout extraction ###
        try:

            # headers
            headers = response.css('h3[class="object-kenmerken-list-header"]')

            # key features
            key_features = {}

            # init construction index
            construction_index = None

            for index in range(0, len(headers)):
                if headers[index].css('::text').get() == 'Layout':
                    construction_index = index

            # extract feature selector
            feature_selector = response.css(
                'h3[class="object-kenmerken-list-header"] + dl[class="object-kenmerken-list"]')
            feature_selector = feature_selector[construction_index]

            # extract feature keys
            feature_keys = Selector(text=feature_selector.get()).css(
                'dt *::text').getall()

            # extract feature values
            feature_vals = (list(filter(None, [
                val.replace('', '').strip()
                for val in
                Selector(text=feature_selector.get()).css(
                    'dd *::text').getall()
            ])))

            # combine keys and values into a dictionary
            for index in range(0, len(feature_vals)):
                feature_vals = [item.replace("\u20ac ", "")
                                for item in feature_vals]
                # feature_vals = [item.replace(" kosten koper", "") for item in feature_vals]
                key_features[feature_keys[index]] = feature_vals[index]

            # store key features
            item['layout'] = key_features
        except:
            pass

#### energy extraction ###
        try:

            # headers
            headers = response.css('h3[class="object-kenmerken-list-header"]')

            # key features
            key_features = {}

            # init construction index
            construction_index = None

            for index in range(0, len(headers)):
                if headers[index].css('::text').get() == 'Energy':
                    construction_index = index

            # extract feature selector
            feature_selector = response.css(
                'h3[class="object-kenmerken-list-header"] + dl[class="object-kenmerken-list"]')
            feature_selector = feature_selector[construction_index]

            # extract feature keys
            feature_keys = Selector(text=feature_selector.get()).css(
                'dt *::text').getall()

            # extract feature values
            feature_vals = (list(filter(None, [
                val.replace('\n', '').strip()
                for val in
                Selector(text=feature_selector.get()).css(
                    'span *::text').getall()
            ])))

            # combine keys and values into a dictionary
            for index in range(0, len(feature_vals)):
                key_features[feature_keys[index]] = feature_vals[index]

            # store key features
            item['energy_certificate'] = key_features
        except:
            pass

#### Exterior space ###
        try:

            # headers
            headers = response.css('h3[class="object-kenmerken-list-header"]')

            # key features
            key_features = {}

            # init construction index
            construction_index = None

            for index in range(0, len(headers)):
                if headers[index].css('::text').get() == 'Exterior space':
                    construction_index = index

            # extract feature selector
            feature_selector = response.css(
                'h3[class="object-kenmerken-list-header"] + dl[class="object-kenmerken-list"]')
            feature_selector = feature_selector[construction_index]

            # extract feature keys
            feature_keys = Selector(text=feature_selector.get()).css(
                'dt *::text').getall()

            # extract feature values
            feature_vals = (list(filter(None, [
                val.replace('\n', '').strip()
                for val in
                Selector(text=feature_selector.get()).css(
                    'dd *::text').getall()
            ])))

            # combine keys and values into a dictionary
            for index in range(0, len(feature_vals)):
                key_features[feature_keys[index]] = feature_vals[index]

            # store key features
            item['exterior_space'] = key_features
        except:
            pass

#### Parking ###
        try:

            # headers
            headers = response.css('h3[class="object-kenmerken-list-header"]')

            # key features
            key_features = {}

            # init construction index
            construction_index = None

            for index in range(0, len(headers)):
                if headers[index].css('::text').get() == 'Parking':
                    construction_index = index

            # extract feature selector
            feature_selector = response.css(
                'h3[class="object-kenmerken-list-header"] + dl[class="object-kenmerken-list"]')
            feature_selector = feature_selector[construction_index]

            # extract feature keys
            feature_keys = Selector(text=feature_selector.get()).css(
                'dt *::text').getall()

            # extract feature values
            feature_vals = (list(filter(None, [
                val.replace('\n', '').strip()
                for val in
                Selector(text=feature_selector.get()).css(
                    'dd *::text').getall()
            ])))

            # combine keys and values into a dictionary
            for index in range(0, len(feature_vals)):
                key_features[feature_keys[index]] = feature_vals[index]

            # store key features
            item['parking'] = key_features
        except:
            pass

        # # write data to JSON-file
        # with open(filename + ".json", 'w+') as f:
        #     f.write(json.dumps(final_list, indent=4))

        yield item


# main driver
if __name__ == '__main__':
    # run scraper
    process = CrawlerProcess()
    process.crawl(HousingSale)
    process.start()
