import scrapy
import arrow
import requests
import os

from scrapy.http import Request
from rong_360.items import ArticleItem
from scrapy.selector import Selector
from rong_360.s3_client import upload_content
from io import BytesIO
from fake_useragent import UserAgent


class rong_360_spider(scrapy.Spider):
    name = "rong_360"
    allowed_domains = ["rong360"]
    start_urls = [
        "https://www.rong360.com/guide/",
    ]

    def parse(self, response):
        if response.status == 200:
            for element in Selector(text=response.body).xpath(
                    "//ul[contains(@class ,'list')] | //div[contains"
                    "(@class ,'gl-block-topline')]"):
                if element.xpath("a[@class='img']"):  # 获取带header image 的url
                    item = ArticleItem()
                    item['title'] = element.xpath("h4/a/@title | a/h4/a"
                                                       "/@title").extract()[0]
                    item['desc'] = element.xpath("p/text() | a/p/text()"
                                                      ).extract()[0]
                    item['image'] = element.xpath("a/img/@src | a/img/@src"
                                                  ).extract()[0]
                    item['raw_url'] = element.xpath("p/a/@href | "
                                                    "a/p/a/@href").extract()[0]
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
                            item['raw_url'] = elem.xpath("a[2]/@href"
                                                         ).extract()[0]
                        else:
                            item['raw_url'] = elem.xpath("a/@href").extract()[0]
                        yield Request(item['raw_url'],
                                      callback=self.parse_info,
                                      meta={'data': item},
                                      dont_filter=True)
        else:
            req = response.request
            req.meta["change_proxy"] = True
            yield req

    def parse_info(self, response):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;"
                      "q=0.9,image/webp,*/*;q=0.8",
        }
        if response.status == 200:
            item = response.meta['data']
            item['status'] = 4
            item['created_at'] = arrow.now().format('YYYY-MM-DD HH:mm:ss')
            item['platform'] = '融360'
            item['section'] = '资讯'
            item['raw_url'] = response.url
            result = Selector(text=response.body).xpath(
                "//*[@class='act-info']/span/text() | //*[@class='bti_left']"
                "/span/text()").extract()
            if len(result) > 1:
                for res in result:
                    item = get_source(res, item)
            else:
                r_list = result[0].split('\r\n')
                for r in r_list:
                    item = get_source(r, item)
            file_name = "rong_360/{}/".format(
                response.url.split('/')[-1].split('.')[0])

            result = Selector(text=response.body).xpath(
                "//*[@class='act-content'] | //*[@class='dcl_box']")
            if result:
                h1 = result[0].xpath("h1").extract()
                if h1:
                    title = h1[0]
                else:
                    title = "<h1>" + \
                            result[0].xpath("div[1]/h1/text()").extract()[
                                0] + "</h1>"
                remark_list = result[0].xpath(
                    "div[1]/span/text() | div[1]/div[1]/div[1]/span/text()").extract()
                res = ''
                if len(remark_list) > 1:
                    for remark in remark_list:
                        if "编辑" not in remark:
                            res += remark.strip() + " "
                    print(res)
                else:
                    print(2)
                    rem = remark_list[0].split("\r\n")
                    for re in rem:
                        if "作者" not in re:
                            res += re.strip() + " "
                    print(res)
                if result[0].xpath("div[1]/div[3]/p/text()"):
                    summary = \
                    result[0].xpath("div[1]/div[3]/p/text()").extract()[0]
                p_text = ""
                if result[0].xpath("div[2]/p"):
                    for p in result[0].xpath("div[2]/p"):
                        if p.xpath("strong/text()"):  # 文章中字体加粗的内容
                            content = "<strong>" + p.xpath(
                                "strong/text()").extract()[0] + "</strong>"
                        elif p.xpath("img"):  # 文章中带有图片的
                            content = "<img/>" + p.xpath("img/@src").extract()[
                                0]
                        elif p.xpath("a"):  # 排除文章内容中有广告语的内容
                            content = ""
                        else:
                            content = p.xpath("text()").extract()[0]
                        p_text += "\n\t" + content
                else:
                    for contents in result[0].xpath("p"):
                        if contents.xpath("strong/text()"):
                            text = "<strong>" + contents.xpath(
                                "strong/text()").extract()[0] + "</strong>"
                        elif contents.xpath("img"):
                            text = "<img/>" + \
                                   contents.xpath("img/@src").extract()[
                                       0]
                        else:
                            if "【独家稿件及免责声明】" not in contents.xpath(
                                    "text()").extract()[0]:
                                text = contents.xpath("text()").extract()[0]
                        p_text += "\n\t" + text
                text_content = title + "\n\t" + res + "\n\t" + summary + "\n\t" + p_text
                print(text_content)

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
    elif len(re.split('日期：')) > 1:
        item['article_time'] = re.split('日期：')[-1]
    elif len(re.split('时间：')) > 1:
        item['article_time'] = re.split('时间：')[-1]
    return item