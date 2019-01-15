# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BeautyItem(scrapy.Item):
    # name
    name = scrapy.Field()

    #avatar
    avatar = scrapy.Field()

    #city
    city = scrapy.Field()

    #height
    height = scrapy.Field()

    #weight
    weight = scrapy.Field()

    #wechat
    wechat = scrapy.Field()

    #telephone
    telephone = scrapy.Field()

    #images
    images = scrapy.Field()

    #details
    details = scrapy.Field()

