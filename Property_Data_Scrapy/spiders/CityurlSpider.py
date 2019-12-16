# -*- coding: utf-8 -*-

import scrapy
from Property_Data_Scrapy.items import UrlItem

class CityurlSpider(scrapy.Spider):
    '''
    爬取城市链接
    '''
    name = 'CityurlSpider'
    allowed_domains = ['fang.com']
    start_urls = ["https://esf.fang.com/newsecond/esfcities.aspx"]

    def parse(self,response):

        Url = UrlItem()
        province_list = response.xpath('//div[@class="letterSelt"]/div[@class="outCont"]/ul/li')
        for i in range(len(province_list)):
            province_name = province_list.xpath('./strong/text()')[i].extract()
            city_list = province_list[i].xpath('./a')
            for j in range(len(city_list)):
                city_name = city_list.xpath('./text()')[j].extract()
                city_url = city_list.xpath('./@href')[j].extract()
                city_url = city_url.replace("http:","")
                city_url = city_url.replace("1","")
                city_url = city_url.replace("/","")
                city_url = "https://" + city_url
                Url['province_name'] = province_name
                Url['city_name'] = city_name
                Url['city_url'] = city_url
                yield Url