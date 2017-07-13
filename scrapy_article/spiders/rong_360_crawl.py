# -*- coding: utf-8 -*-

import arrow
import requests
import scrapy
import time

from io import BytesIO
from fake_useragent import UserAgent
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy_article.items import ArticleItem
from scrapy_common.s3_client import upload_content
from scrapy_article.pipelines import get_all_rawl_url


class Rong360Spider(scrapy.Spider):
    name = "rong_spider"
    allowed_domains = ["rong360"]
    start_urls = [
        "https://www.rong360.com/guide/",
    ]

    def parse(self, response):
        if response.status == 200:
            raw_url_list = get_all_rawl_url()
            for element in Selector(text=response.body).xpath(
                    "//ul[contains(@class ,'list')] | //div[contains"
                    "(@class ,'gl-block-topline')]"):
                time.sleep(10)
                if element.xpath("a[@class='img']"):  # 获取带header image 的url
                    item = ArticleItem()
                    item['title'] = element.xpath("h4/a/@title | a/h4/a"
                                                  "/@title").extract()[0]
                    item['desc'] = element.xpath("p/text() | a/p/text()"
                                                 ).extract()[0]
                    item['image'] = element.xpath("a/img/@src | a/img/@src"
                                                  ).extract()[0]
                    url = get_raw_url(element.xpath(
                        "p/a/@href | a/p/a/@href").extract()[0], raw_url_list)
                    self.logger.info('request url is %s', url)
                    if url:  # 判断url是否抓取过子页面
                        item['raw_url'] = url
                        yield Request(item['raw_url'],
                                      callback=self.parse_info,
                                      meta={'data': item},
                                      dont_filter=True)
                else:
                    for elem in element.xpath("li"):  # 不带header image 的url
                        item = ArticleItem()
                        item['title'] = \
                            elem.xpath("a/text() | a[2]/@title | "
                                       "a/@title").extract()[0]
                        item['desc'] = None
                        item['image'] = None
                        if elem.xpath("a/span/text()"):  # 头条 url
                            article_url = elem.xpath("a[2]/@href").extract()[0]
                        else:
                            article_url = elem.xpath("a/@href").extract()[0]
                        if get_raw_url(article_url, raw_url_list):
                            item['raw_url'] = get_raw_url(article_url,
                                                          raw_url_list)
                            self.logger.info('request url is %s',
                                             item['raw_url'])
                            yield Request(item['raw_url'],
                                          callback=self.parse_info,
                                          meta={'data': item},
                                          dont_filter=True)
        else:
            req = response.request
            req.meta["change_proxy"] = True
            self.logger.info("chang proxy")
            yield req

    def parse_info(self, response):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;"
                      "q=0.9,image/webp,*/*;q=0.8",
        }
        source_time = Selector(text=response.body).xpath(
            "//*[@class='act-info']/span/text()").extract()
        self.logger.info('request url is %s', source_time)
        if source_time:  # 有的url子页面内不是文章
            if response.status == 200:
                item = response.meta['data']
                item['status'] = 4
                item['created_at'] = arrow.now().format('YYYY-MM-DD HH:mm:ss')
                item['platform'] = '融360'
                item['section'] = '资讯'
                item['raw_url'] = response.url
                r_list = source_time[0].split('\r\n')
                for r in r_list:
                    item = get_source(r, item)
                file_name = "rong_360/{}/".format(
                    response.url.split('/')[-1].split('.')[0])
                result = Selector(text=response.body).xpath(
                    "//*[@class='act-content']")
                if result:
                    title = result[0].xpath("h1").extract()[0]
                    res = ''.join([item['article_time'], item['source']])
                    text_content = title + "\n\t" + res + "\n\t"
                    if result[0].xpath("div[2]/p"):
                        for p in result[0].xpath("div[2]/p"):
                            text_content += ''.join("\n\t" + get_text(p))
                    else:
                        for contents in result[0].xpath("p"):
                            text_content += ''.join("\n\t" + get_text(contents))
                    item['s3_key'] = upload_path(text_content.strip(),
                                                 file_name + "index.html",
                                                 content_type='text/html; charset=utf-8')

                if item.get('image'):  # 把header image存到s3中
                    image_name = file_name + item.get('image').split('/')[-1]
                    image_url = "https://www.rong360.com" + item.get('image')
                    img_response = requests.get(image_url,
                                                headers=headers.update(
                                                    {
                                                        'user-agent': get_user_agent()}))
                    if img_response.status_code == 200:
                        content = BytesIO(img_response.content)
                        item['image'] = upload_path(content, image_name)
                yield item
            else:
                req = response.request
                req.meta["change_proxy"] = True
                self.logger.info("chang proxy")
                yield req


def upload_path(content, file, content_type='string'):
    upload_content(content, file, content_type=content_type)
    return file


def get_user_agent():
    ua = UserAgent()
    return ua.random


def get_source(re, item):
    if len(re.split('来源：')) > 1:
        item['source'] = re.split('来源：')[-1]
    elif len(re.split('时间：')) > 1:
        item['article_time'] = re.split('时间：')[-1]
    return item


def add_tag(content, flag):
    if flag == 1:
        return "<strong>" + content + "</strong>"
    else:
        return "<img>" + content


def get_raw_url(url, url_list):
    if url not in url_list:
        return url


def get_text(contents):
    if contents.xpath("strong/text()"):  # 文章中字体加粗的内容
        text = contents.xpath("string(.)").extract()[0].strip()
    elif contents.xpath("img"):  # 文章中带有图片的
        text = contents.xpath("img/@src").extract()[0].strip()
    else:
        if contents.xpath("a | strong/a"):  # 排除文章内容中有广告语的内容
            text = ""
        elif "【独家稿件及免责声明】" in contents.xpath("text()").extract()[0].strip():
            text = ""
        else:
            text = contents.xpath("string(.)").extract()[0].strip()
    return text
