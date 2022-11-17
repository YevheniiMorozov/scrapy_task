import time
import random
import scrapy
import serializing_and_ua as sua


class KijijiSpider(scrapy.Spider):
    name = 'kijiji'
    allowed_domains = ['kijiji.ca']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/104.0.0.0 Safari/537.36",
    }
    cookies = {'dont_merge_cookies': True}
    count = 0
    url_dict = {}

    def start_requests(self):
        locations = [
            "alberta/c37l9003", "edmonton/c37l1700203", "british-columbia/c37l9007", "victoria-bc/c37l1700173"
        ]
        for location in locations:
            url = 'http://www.kijiji.ca/b-apartments-condos/' + location
            time.sleep(1)
            yield scrapy.Request(
                url=url, callback=self.parse, headers=KijijiSpider.headers, meta={'location': location.split("/")[0]}
            )

        # url = 'https://www.kijiji.ca/b-apartments-condos/victoria-bc/c37l1700173'
        # yield scrapy.Request(url=url, callback=self.parse, headers=KijijiSpider.headers, )

    def parse(self, response):
        items = response.xpath("//div[@class='container-results large-images'][2]//div/div/div[2]/div/div[2]")
        next_page = response.xpath("//a[@title='Next']//@href").get()
        KijijiSpider.url_dict[response.url] = next_page
        if KijijiSpider.url_dict[response.url]:
            yield response.follow(
                url=KijijiSpider.url_dict[response.url],
                callback=self.parse,
                headers=KijijiSpider.headers,
                meta=response.request.meta
            )
        for item in items:
            time.sleep(0.2)
            KijijiSpider.count += 1
            if KijijiSpider.count % 30 == 0:
                KijijiSpider.headers = sua.user_agent()
                KijijiSpider.count = 0
                print("changing user-agent")
                time.sleep(1)
            url = item.xpath(".//@href").get()
            time.sleep(random.random())
            time.sleep(0.2)
            yield response.follow(
                url=url, callback=self.parse_page, headers=KijijiSpider.headers, meta=response.request.meta
            )

        if KijijiSpider.url_dict[response.url]:
            yield response.follow(
                url=KijijiSpider.url_dict[response.url],
                callback=self.parse,
                headers=KijijiSpider.headers,
                meta=response.request.meta
            )

    def parse_page(self, response):

        item_id = response.xpath('//*[@id="ViewItemPage"]/div/div/nav/ol/li[5]/a/text()').get()
        if not item_id:
            print("Invalid data, reparse url ", response.url)
            yield scrapy.Request(
                url=response.url, callback=self.parse_page, headers=KijijiSpider.headers, meta=response.request.meta
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
