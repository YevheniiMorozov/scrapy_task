import time
from collections import defaultdict

import scrapy
from fake_useragent import UserAgent


ua = UserAgent(verify_ssl=False)


class KijijiSpider(scrapy.Spider):
    name = 'kijiji'
    allowed_domains = ['kijiji.ca']
    headers = {"User-Agent": ua.random}
    count = 0
    locations = [
        "alberta/c37l9003", "edmonton/c37l1700203", "british-columbia/c37l9007", "victoria-bc/c37l1700173"
    ]
    # locations = [
    #     "victoria-bc/c37l1700173"
    # ]

    parsed_links = defaultdict(list)

    def start_requests(self):
        for location in self.locations:
            url = 'https://www.kijiji.ca/b-apartments-condos/' + location
            key = location.split("/")[0]
            yield scrapy.Request(
                url=url, callback=self.parser, headers=self.headers, meta={'location': key}, dont_filter=True
            )

    def parser(self, response):
        # time.sleep(3)
        print("Looking next page")
        self.count += 1
        next_page = response.xpath("//a[@title='Next']//@href").get()
        self.parsed_links[response.request.meta["location"]].append(response.url)
        if self.count == 30:
            self.count = 0
            print("Change headers")
            time.sleep(3)
            self.headers["User-Agent"] = {"User-Agent": ua.random}
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
                print("Now parse page ", url)
                yield scrapy.Request(
                    url=url, callback=self.parse_item_links, headers=self.headers, meta=response.meta
                )

    def parse_item_links(self, response):
        # time.sleep(1)
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
            if self.count % 30 == 0:
                self.count = 0
                time.sleep(3)
            yield response.follow(
                url=item, callback=self.parse_page, headers=self.headers, meta=response.request.meta
            )

    def parse_page(self, response):
        time.sleep(3)
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
            estate_title = response.xpath('//*[@id="vip-body"]/div[1]')
            if response.xpath('//div[@role="presentation"]'):
                estate_title = response.xpath('//*[@id="vip-body"]/div[2]')
            title = estate_title.xpath('.//div/h1/text()').get()
            price = estate_title.xpath('.//div/div/span[1]/text()').get()
            utilities = estate_title.xpath('.//div/div/span[2]/text()').get()
            address = estate_title.xpath('.//div[2]/div/span/text()').get()
            time_posted = estate_title.xpath('.//div[2]/div[2]/time/@datetime').extract_first()
            attributes = response.xpath('//*[@id="vip-body"]/div[3]/div[2]/div/div')
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
                    heat = True
                util3 = attributes.xpath('.//div[1]/ul/li[1]/div/ul/li[3]/svg/@aria-label').extract_first()
                if util3.startswith("Yes"):
                    water = True
            wifi = attributes.xpath('.//div[1]/ul/li[2]/div/ul').get() != "Not Included"
            parking = attributes.xpath('.//div[1]/ul/li[3]/dl/dd/text()').get()
            agreement = attributes.xpath('.//div[1]/ul/li[4]/dl/dd/text()').get()
            pet_friendly = attributes.xpath('.//div[1]/ul/li[5]/dl/dd').get() != "No"
            size = attributes.xpath('.//div[2]/ul/li[1]/dl/dd/text()').get()
            size = size if size != "Not Available" else 0
            furnished = attributes.xpath('.//div[2]/ul/li[2]/dl/dd').get() == "Yes"
            laundry, dishwasher, fridge = ['Laundry (I', 'Dishwasher', 'Fridge / F']
            if response.xpath('.//div[2]/ul/li[3]/div/ul').get() != 'Not Included':
                values = attributes.xpath('.//div[2]/ul/li[3]/div/ul')
                value_list = [values.xpath(f'.//li[{i}]/text()').get()[:10]
                              for i in range(2, 5) if values.xpath(f'.//li[{i}]/text()')]
                laundry = laundry in value_list
                dishwasher = dishwasher in value_list
                fridge = fridge in value_list
            air_conditioning = attributes.xpath('.//div[2]/ul/li[4]/dl/dd').get() != "No"
            outdoor_space = attributes.xpath('.//div[2]/ul/li[5]/dl/dd').get()
            smoking = attributes.xpath('.//div[2]/ul/li[6]/dl/dd').get() != 'No'
            description = response.xpath('//*[@id="vip-body"]/div[4]/div/div[1]/div/div/p[1]/text()[1]').get()
            user_url = response.xpath('//*[@id="vip-body"]/div[5]/div[2]/div/div[1]/div/a/@href').extract_first()
            custom_xpath = '//*[@id="vip-body"]/div[5]/div[2]/div/'
            user_info = {1: True}
            if not user_url:
                user_url = response\
                    .xpath('//*[@id="vip-body"]/div[7]/div[2]/div[2]/div[1]/div/a/@href').extract_first()
                custom_xpath = '//*[@id="vip-body"]/div[7]/div[2]/div[2]/'
                if not user_url:
                    user_info = {}
            if user_info.get(1, None):
                user_url = "https://www.kijiji.ca" + user_url
                owner = response.xpath(f'{custom_xpath}div[2]/div[1]/text()').get() == 'Owner'
                on_kijiji = response.xpath(f'{custom_xpath}div[2]/div[2]/span/text()').get()
                listing = 0 or response.xpath(f'{custom_xpath}div[2]/div[3]/span/text()').get()
                website = response.xpath(f'{custom_xpath}div[2]/div[4]/a').get()
                if website:
                    website = response.xpath(f'{custom_xpath}div[2]/div[4]/a/@href').extract_first()
                user_info = {
                    "url": user_url,
                    'owner': owner,
                    'on_kijiji': on_kijiji,
                    'listening': listing,
                    "website": website
                }

            yield {
                "apartment_id": item_id,
                "title": title,
                "price": price,
                "utilities": utilities,
                "address": address,
                "time": time_posted,
                'location': response.request.meta['location'],
                "included_utilities": {
                    "hydro": hydro,
                    'heat': heat,
                    'water': water,
                    "wifi": wifi,
                    'parking': parking,
                    'agreement': agreement,
                    'pet_friendly': pet_friendly
                },
                'unit': {
                    'size': size,
                    'furnished': furnished,
                    'laundry': laundry,
                    "dishwasher": dishwasher,
                    'fridge': fridge,
                    "conditioning": air_conditioning,
                    'outdoor_space': outdoor_space,
                    'smoking': smoking,
                    'description': description
                },
                'user_info': user_info
            }
