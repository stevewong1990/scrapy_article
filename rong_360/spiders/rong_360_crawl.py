import scrapy
import arrow
import requests

from scrapy.http import Request
from rong_360.items import Rong360Item
from lxml import etree
from scrapy.selector import Selector
from rong_360.s3_client import upload_content
from scrapy.conf import settings
from io import BytesIO


class rong_360_spider(scrapy.Spider):
    name = "rong_360"
    allowed_domains = [".com"]
    start_urls = [
        "https://www.rong360.com/guide/",
    ]

    def parse(self, response):
        if response.status == 200:
            tree = etree.HTML(response.body)
            for element in tree.xpath("//ul[contains(@class ,'list')] | //div"
                                      "[contains(@class ,'gl-block-topline')]"):
                if element.xpath("a[@class='img']"):
                    item = Rong360Item()
                    item['title_text'] = element.xpath("h4/a/@title | "
                                                       "a/h4/a/@title")[0]
                    item['desc_text'] = element.xpath("p/text() | a/p/text()")[
                        0]
                    item['image'] = element.xpath("a/img/@src | a/img/@src")[0]
                    item['raw_url'] = element.xpath("p/a/@href | a/p/a/@href")[
                        0]
                    yield Request(item['raw_url'], headers=settings['HEADERS'],
                                  callback=self.parse_info,
                                  meta={'data': item,
                                        'headers': settings['HEADERS']},
                                  dont_filter=True)
                else:
                    for elem in element.xpath("li"):
                        item = Rong360Item()
                        item['title_text'] = \
                        elem.xpath("a/text() | a[2]/@title | "
                                   "a/@title")[0]
                        item['desc_text'] = None
                        item['image'] = None
                        if elem.xpath("a/span/text()"):
                            item['raw_url'] = elem.xpath("a[2]/@href")[0]
                        else:
                            item['raw_url'] = elem.xpath("a/@href")[0]
                        yield Request(item['raw_url'],
                                      headers=settings['HEADERS'],
                                      callback=self.parse_info,
                                      meta={'data': item},
                                      dont_filter=True)
        else:
            req = response.request
            req.meta["change_proxy"] = True
            yield req

    def parse_info(self, response):
        if response.status == 200:
            item = response.meta['data']
            item['status'] = 0
            item['created_at'] = arrow.now().format('YYYY-MM-DD HH:mm:ss')
            item['platform'] = '融360'
            item['section'] = '资讯'
            item['raw_url'] = response.url
            result = Selector(text=response.body).xpath(
                "//*[@class='act-info']/span/text()").extract()
            if result:
                li_list = result[0].split('\r\n')
                for li in li_list:
                    if len(li.split('时间：')) > 1:
                        item['article_time'] = li.split('时间：')[-1]
                    elif len(li.split('来源：')) > 1:
                        item['source'] = li.split('来源：')[-1]
            else:
                results = Selector(text=response.body).xpath(
                    "//*[@class='bti_left']")
                if results:
                    re_list = results[0].xpath("span/text()").extract()
                    for re in re_list:
                        if len(re.split('来源：')) > 1:
                            item['source'] = re.split('来源：')[-1]
                        elif len(re.split('日期：')) > 1:
                            item['article_time'] = re.split('日期：')[-1]
            file_name = "rong_360/{}/".format(
                response.url.split('/')[-1].split('.')[0])
            result = etree.HTML(response.body).xpath(
                "//*[@class='act-content']")
            if result:
                title = "<h1>" + result[0].xpath("h1")[0].text + "</h1>"
                create_time = result[0].xpath("div[1]/span/text()")[0]
                create_time_ = create_time.split("\r\n")
                s_ = ""
                for ct in create_time_:
                    s_ += ct + ""
                p_list = result[0].xpath("div[2]/p")
                p__text = ""
                if p_list:
                    for p in p_list:
                        if p.xpath("strong/text()"):
                            p_text = "<strong>" + p.xpath("strong/text()")[
                                0] + "</strong>"
                        elif p.xpath("img"):
                            for img_label in p.xpath("img"):
                                p_text = str(etree.tostring(img_label,
                                                            pretty_print=True))
                        else:
                            p_text = p.xpath("text()")[0]
                        p__text += "\n\t" + p_text
                else:
                    p_list__ = result[0].xpath("p")
                    for p__ in p_list__:
                        if p__.xpath("strong/text()"):
                            text__ = "<strong>" + p__.xpath("strong/text()")[
                                0] + "</strong>"
                        elif p__.xpath("img"):
                            for img_label in p__.xpath("img"):
                                text__ = str(etree.tostring(img_label,
                                                            pretty_print=True))
                        else:
                            if "【独家稿件及免责声明】" in p__.xpath("text()")[0]:
                                text__ = ""
                            else:
                                text__ = p__.xpath("text()")[0]
                        p__text += "\n\t" + text__
                article__ = title + "\n\t" + "<span>" + s_ + "</span>" + p__text
                item['s3_key'] = self.upload_path(article__,
                                                  file_name + "article.txt", content_type='text/plain; charset=utf-8')
            else:
                element = etree.HTML(response.body).xpath(
                    "//*[@class='dcl_box']")
                if element:
                    title_ = "<h1>" + element[0].xpath("div[1]/h1/text()")[
                        0] + "</h1>"
                    p_remark_ = ""
                    for span in element[0].xpath("div[1]/div[1]/div[1]/span"):
                        remark = str(span.xpath("text()")[0])
                        p_remark_ += " " + remark
                    content = "<p>" + \
                              element[0].xpath("div[1]/div[3]/p/text()")[
                                  0] + "</p>"
                    data = Selector(text=response.body).xpath(
                        "//*[@class='bta_context']")
                    if data:
                        info = data.xpath("string(.)").extract()[0]
                    p_list_ = element[0].xpath("div[2]/p")
                    p_text__ = ""
                    for p_ in p_list_:
                        if p_.xpath("strong/text()"):
                            p_text_ = "<strong>" + p_.xpath("strong/text()")[
                                0] + "</strong>"
                        elif p_.xpath("img"):
                            for img_label_ in p_.xpath("img"):
                                p_text_ = str(etree.tostring(img_label_,
                                                             pretty_print=True))
                        elif p_.xpath("a"):
                            p_text_ = ""
                        else:
                            p_text_ = p_.xpath("text()")[0]
                        p_text__ += "\n\t" + p_text_
                    article_ = title_ + "\n\t" + "<span>" + p_remark_ \
                               + "</span>" + "\n\t" + content + "\n\t" \
                               + info + p_text__
                    item['s3_key'] = self.upload_path(article_,
                                                      file_name + "article.txt", content_type='text/plain; charset=utf-8')
            if item.get('image'):
                image_name = file_name + item.get('image').split('/')[-1]
                image_url = "https://www.rong360.com" + item.get('image')
                img_response = requests.get(image_url,
                                            headers=settings['HEADERS'])
                if img_response.status_code == 200:
                    content = BytesIO(img_response.content)
                    item['image'] = self.upload_path(content, image_name)
            yield item
        else:
            req = response.request
            req.meta["change_proxy"] = True
            yield req

    def upload_path(self, content, file, content_type='string'):
        upload_content(content, file, content_type=content_type)
        return file
