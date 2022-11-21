import time
from collections import defaultdict

import scrapy
from fake_useragent import UserAgent
from ..items import ApartmentsItem, UserItem, UnitItem, UtilitiesItem, LocationItem


ua = UserAgent(verify_ssl=False)


class KijijiSpider(scrapy.Spider):
    name = 'kijiji'
    allowed_domains = ['kijiji.ca']
    headers = {"User-Agent": ua.random}
    count = 0
    locations = [
        "alberta/c37l9003", "edmonton/c37l1700203", "british-columbia/c37l9007", "victoria-bc/c37l1700173",
        'manitoba/c37l9006', 'winnipeg/c37l1700192', 'new-brunswick/c37l9005', 'fredericton/c37l1700018',
        'newfoundland/c37l9008', 'st-johns/c37l1700113', "northwest-territories/c37l1700103", 'yellowknife/c37l1700104',
        'ville-de-quebec/c37l1700124', 'ville-de-quebec/c37l1700124', 'yukon/c37l1700101', 'whitehorse/c37l1700102',
        'saskatchewan/c37l9009', 'regina/c37l1700196', 'nova-scotia/c37l9002', 'city-of-halifax/c37l1700321'
    ]

    parsed_links = defaultdict(list)

    def start_requests(self):
        for location in self.locations:
            url = 'https://www.kijiji.ca/b-apartments-condos/' + location
            key = location.split("/")[0]
            yield scrapy.Request(
                url=url,
                callback=self.parser,
                headers=self.headers,
                meta={'location': key},
                dont_filter=True
            )

    def parser(self, response):
        print("Looking next page")
        self.count += 1
        next_page = response.xpath("//a[@title='Next']//@href").get()
        self.parsed_links[response.request.meta["location"]].append(response.url)
        if self.count == 10:
            self.count = 0
            print("Change headers")
            time.sleep(2)
            self.headers["User-Agent"] = ua.random
        if next_page:
            print("page find")
            yield response.follow(
                url=next_page,
                callback=self.parser,
                headers=self.headers,
                meta=response.request.meta,
                dont_filter=True
            )
        elif not response.xpath('//body/text()').get():
            print("Get empty body, retry to find url for next page")
            yield scrapy.Request(
                url=response.url,
                callback=self.parser,
                headers=self.headers,
                meta=response.request.meta,
                dont_filter=True
            )
        else:
            location = response.meta['location']
            for url in self.parsed_links[location]:
                yield scrapy.Request(
                    url=url, callback=self.parse_item_links, headers=self.headers, meta=response.meta
                )

    def parse_item_links(self, response):
        print('Get links from ', response.url)
        items = response.xpath("//div[@class='container-results large-images'][2]//div/div/div[2]/div/div[2]")
        if not items:
            print("Empty data in {}, reparse...".format(response.url))
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_item_links,
                headers=self.headers,
                meta=response.meta,
                dont_filter=True
            )
        for item in items:
            item = item.xpath('.//a/@href').get()
            self.count += 1
            if self.count % 10 == 0:
                self.count = 0
                print("Change headers")
                time.sleep(2)
                self.headers["User-Agent"] = ua.random
            yield response.follow(
                url=item, callback=self.parse_page, headers=self.headers, meta=response.request.meta
            )

    def parse_page(self, response):
        item_id = response.xpath('//*[@id="ViewItemPage"]/div/div/nav/ol/li[5]/a/text()').get()
        if not item_id:
            print("Invalid data, reparse url ", response.url)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_page,
                headers=self.headers,
                meta=response.request.meta,
                dont_filter=True
            )
        else:
            item_location, item_apartment, item_utilities = LocationItem(), ApartmentsItem(), UtilitiesItem()
            item_unit, item_user = UnitItem(), UserItem()
            item_location["name"] = response.request.meta['location']
            estate_title = response.xpath('//*[@id="vip-body"]/div[1]')
            if response.xpath('//div[@role="presentation"]'):
                estate_title = response.xpath('//*[@id="vip-body"]/div[2]')
            item_apartment["apartment_id"] = item_id
            item_apartment["title"] = estate_title.xpath('.//div/h1/text()').get()
            price = estate_title.xpath('.//div/div/span[1]/text()').get()[1:]
            item_apartment["price"] = price.replace(",", '') if price.isdigit() else None
            utilities = estate_title.xpath('.//div/div/span[2]/text()').get()
            item_apartment["include_utilities"] = utilities
            item_apartment["address"] = estate_title.xpath('.//div[2]/div/span/text()').get()
            item_apartment["published"] = estate_title.xpath('.//div[2]/div[2]/time/@datetime').extract_first()
            attributes = response.xpath('//*[@id="vip-body"]/div[2]/div[2]/div/div')
            if not attributes:
                attributes = response.xpath('//*[@id="vip-body"]/div/div[2]/div/div')
            if response.xpath('//*[@id="vip-body"]/div[3]/span[2]').get() == "View Details":
                attributes = response.xpath('//*[@id="vip-body"]/div[4]/div[2]/div/div')
            # utilities
            hydro, water, heat = False, False, False
            if utilities != 'No Utilities Included':
                util1 = attributes.xpath('.//div[1]/ul/li[1]/div/ul/li[1]/svg/@aria-label').extract_first()
                if util1.startswith("Yes"):
                    hydro = True
                util2 = attributes.xpath('.//div[1]/ul/li[1]/div/ul/li[2]/svg/@aria-label').extract_first()
                if util2.startswith("Yes"):
                    water = True
                util3 = attributes.xpath('.//div[1]/ul/li[1]/div/ul/li[3]/svg/@aria-label').extract_first()
                if util3.startswith("Yes"):
                    heat = True
            item_utilities["hydro"], item_utilities["heat"], item_utilities["water"] = hydro, water, heat
            item_utilities["wifi"] = attributes.xpath('.//div[1]/ul/li[2]/div/ul').get() != "Not Included"
            item_utilities["parking"] = attributes.xpath('.//div[1]/ul/li[3]/dl/dd/text()').get()[0]
            item_utilities["agreement"] = attributes.xpath('.//div[1]/ul/li[4]/dl/dd/text()').get()
            pet_friendly = attributes.xpath('.//div[1]/ul/li[6]/dl/dd/text()').get()
            if pet_friendly:
                item_utilities['move_in_date'] = attributes.xpath('.//div[1]/ul/li[5]/dl/dd/span/text()').get()
            else:
                pet_friendly = attributes.xpath('.//div[1]/ul/li[5]/dl/dd/text()').get()
            item_utilities['pet_friendly'] = pet_friendly != "No"
            size = attributes.xpath('.//div[2]/ul/li[1]/dl/dd/text()').get()
            item_unit['size'] = size.replace(",", '') if size != "Not Available" else 0
            item_unit['furnished'] = attributes.xpath('.//div[2]/ul/li[2]/dl/dd').get() == "Yes"
            laundry, dishwasher, fridge = ['Laundry (I', 'Dishwasher', 'Fridge / F']
            if response.xpath('.//div[2]/ul/li[3]/div/ul').get() != 'Not Included':
                values = attributes.xpath('.//div[2]/ul/li[3]/div/ul')
                value_list = [values.xpath(f'.//li[{i}]/text()').get()[:10]
                              for i in range(2, 5) if values.xpath(f'.//li[{i}]/text()')]
                item_unit['laundry'] = laundry in value_list
                item_unit['dishwasher'] = dishwasher in value_list
                item_unit['fridge'] = fridge in value_list
            item_unit['air_condition'] = attributes.xpath('.//div[2]/ul/li[4]/dl/dd').get() != "No"
            item_unit['outdoor_space'] = attributes.xpath('.//div[2]/ul/li[5]/dl/dd').get()
            item_unit['smocking_permitted'] = attributes.xpath('.//div[2]/ul/li[6]/dl/dd').get() != 'No'
            item_apartment["description"] = response\
                .xpath('//*[@id="vip-body"]/div[4]/div/div[1]/div/div/p[1]/text()[1]').get()
            user_url = response.xpath('//*[@id="vip-body"]/div/div/div/div/div/a[1]/@href').extract_first()
            custom_xpath = '//*[@id="vip-body"]/div/div/div/'
            item_user["profile"] = "https://www.kijiji.ca" + user_url
            item_user["owner"] = response.xpath(f'{custom_xpath}div[2]/div[1]/text()').get() == 'Owner'
            if response.xpath(f'{custom_xpath}div[2]/div[2]/text()') == "listing":
                item_user['registry_time'] = response.xpath(f'{custom_xpath}div/div[3]/div[1]/text()')
                item_user['listing'] = response.xpath(f'{custom_xpath}div[2]/div[2]/span/text()').get()
            else:
                item_user['registry_time'] = response.xpath(f'{custom_xpath}div[2]/div[2]/span/text()').get()
                item_user['listing'] = response.xpath(f'{custom_xpath}div[2]/div[3]/span/text()').get() or 1
            website = response.xpath(f'{custom_xpath}div/div/a[2]').get()
            if website:
                item_user['website'] = response.xpath(f'{custom_xpath}div/div/a[2]/@href').extract_first()

            yield {
                'apartment': item_apartment,
                "location": item_location,
                "utilities": item_utilities,
                "units": item_unit,
                "user": item_user
            }
