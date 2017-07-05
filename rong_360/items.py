# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Rong360Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    raw_url = scrapy.Field()
    title_text = scrapy.Field()
    desc_text = scrapy.Field()
    image = scrapy.Field()
    source = scrapy.Field()
    s3_key = scrapy.Field()
    status = scrapy.Field()
    created_at = scrapy.Field()
    article_time = scrapy.Field()
    platform = scrapy.Field()
    section = scrapy.Field()
