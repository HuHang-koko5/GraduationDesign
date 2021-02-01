# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GraduationprojectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CeicItem(scrapy.Item):
    time = scrapy.Field()
    epi_lat = scrapy.Field()
    epi_lon = scrapy.Field()
    epi_depth = scrapy.Field()
    mag = scrapy.Field()
    location = scrapy.Field()


class SinaItem(scrapy.Item):
    user_name = scrapy.Field()
    user_blog = scrapy.Field()
    content = scrapy.Field()
    t_time = scrapy.Field()
    like_num = scrapy.Field()
    repost_num = scrapy.Field()
    comment_num = scrapy.Field()
    key_word = scrapy.Field()
    key_time = scrapy.Field()
    epi_lat = scrapy.Field()
    epi_lon = scrapy.Field()
    dotIndex = scrapy.Field()
