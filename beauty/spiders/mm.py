# -*- coding: utf-8 -*-
import scrapy
import logging
import re
import json
from scrapy.loader import ItemLoader
from beauty.items import BeautyItem

logger = logging.getLogger('beautyLogger')

class MmSpider(scrapy.Spider):
    name = 'mm'
    allowed_domains = ['mm.taobao.com']
    start_urls = [
        'https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8&currentPage=1&pageSize=100',
    ]

    def parse(self, response):
        # for url in self.start_urls:
        #     yield scrapy.Request(url=url, callback=self.parseSeeds)
        for index in range(1,2):
            url = 'https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8&currentPage={0}&pageSize=100'.format(index)
            yield scrapy.Request(url=url, callback=self.parseSeeds)
        

    def parseSeeds(self, response):
        content = response.body
        content = content.decode('gb2312')
        res = json.loads(content)
        seeds = res['data']['searchDOList']
        for seed in seeds:
            name = seed['realName']
            height = seed['height']
            city = seed['city']
            weight = seed['weight']
            avatar = 'http:'+seed['avatarUrl']
            url = 'https://mm.taobao.com/self/aiShow.htm?userId='+str(seed['userId'])
            meta = { 'name': name, 'avatar': avatar, 'city': city, 'height': height, 'weight':weight }
            logger.info('name=%s, height=%s, city=%s, weight=%s, avatar=%s,url=%s',name,height,city,weight,avatar,url)
            yield scrapy.Request(url=url, callback=self.parseDetails, meta=meta)

    
    def parseDetails(self,response):
        images = []
        meta = response.meta
        # logger.info('name=%s',meta['name'])
        allImages = response.css('img').xpath('@src').extract()
        for image in allImages:
            if ''!=image.strip() and image.find('img.alicdn.com/imgextra') != -1:
                images.append('http:'+image)
                break
        details = response.xpath('//div[@id="J_ScaleImg"]').extract()
        details = ''.join(details)
        telephone = re.findall(r'1\d{10}',details)
        loader = ItemLoader(item=BeautyItem(), response=response)
        loader.add_value('name', meta['name'])
        loader.add_value('city', meta['city'])
        loader.add_value('avatar', meta['avatar'])
        loader.add_value('height', meta['height'])
        loader.add_value('weight', meta['weight'])
        loader.add_value('telephone', telephone)
        loader.add_value('details', details)
        loader.add_value('images', images)
        return loader.load_item()

