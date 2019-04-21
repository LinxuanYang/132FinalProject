# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookLink(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()


class Book(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    author = scrapy.Field()
    picture = scrapy.Field()
