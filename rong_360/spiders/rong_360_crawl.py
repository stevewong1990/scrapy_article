import scrapy
import arrow
import requests

from scrapy.http import Request
from rong_360.items import Rong360Item
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
                    item = Rong360Item()
                    item['title_text'] = element.xpath("h4/a/@title | a/h4/a"
                                                       "/@title").extract()[0]
                    item['desc_text'] = element.xpath("p/text() | a/p/text()"
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
                        item = Rong360Item()
                        item['title_text'] = \
                            elem.xpath("a/text() | a[2]/@title | "
                                       "a/@title").extract()[0]
                        item['desc_text'] = None
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
            item['status'] = 0
            item['created_at'] = arrow.now().format('YYYY-MM-DD HH:mm:ss')
            item['platform'] = '融360'
            item['section'] = '资讯'
            item['raw_url'] = response.url
            result = Selector(text=response.body).xpath(
                "//*[@class='act-info']/span/text()").extract()
            if result:  # 资讯文章子页面有两种（时间和来源）的排序位置
                for li in result[0].split('\r\n'):
                    if len(li.split('时间：')) > 1:
                        item['article_time'] = li.split('时间：')[-1]
                    elif len(li.split('来源：')) > 1:
                        item['source'] = li.split('来源：')[-1]
            else:
                results = Selector(text=response.body).xpath(
                    "//*[@class='bti_left']")
                if results:
                    for re in results[0].xpath("span/text()").extract():
                        if len(re.split('来源：')) > 1:
                            item['source'] = re.split('来源：')[-1]
                        elif len(re.split('日期：')) > 1:
                            item['article_time'] = re.split('日期：')[-1]
            file_name = "rong_360/{}/".format(
                response.url.split('/')[-1].split('.')[0])
            result = Selector(text=response.body).xpath(
                "//*[@class='act-content']")
            if result:  # 资讯文章子页面的文章内容有2种页面样式，
                title = "<h1>" + result[0].xpath("h1").extract()[0] + "</h1>"
                create_time = result[0].xpath("div[1]/span/text()").extract()[0]
                create_time_ = create_time.split("\r\n")
                s_ = ""
                for ct in create_time_:
                    s_ += ct + ""
                p__text = ""
                if result[0].xpath("div[2]/p"):  # 1.<div class='act-content'><div>文章内容</div></div>
                    for p in result[0].xpath("div[2]/p"):
                        if p.xpath("strong/text()"):
                            p_text = "<strong>" + p.xpath(
                                "strong/text()").extract()[0] + "</strong>"
                        elif p.xpath("img"):
                            p_text = "<img/>" + p.xpath("img/@src").extract()[0]
                        else:
                            p_text = p.xpath("text()").extract()[0]
                        p__text += "\n\t" + p_text
                else:  # 2.<div>文章内容</div>
                    for p__ in result[0].xpath("p"):
                        if p__.xpath("strong/text()"):
                            text__ = "<strong>" + p__.xpath(
                                "strong/text()").extract()[0] + "</strong>"
                        elif p__.xpath("img"):
                            text__ = "<img/>" + p__.xpath("img/@src").extract()[
                                0]
                        else:
                            if "【独家稿件及免责声明】" in p__.xpath(
                                    "text()").extract()[0]:
                                text__ = ""
                            else:
                                text__ = p__.xpath("text()").extract()[0]
                        p__text += "\n\t" + text__
                article__ = title + "\n\t" + "<span>" + s_ + "</span>" + p__text
                item['s3_key'] = upload_path(article__,
                                                  file_name + "article.txt",
                                                  content_type='text/plain; charset=utf-8')
            else:  # 3.<div class='dcl_box'><div>文章内容</div></div>
                element = Selector(text=response.body).xpath(
                    "//*[@class='dcl_box']")
                if element:
                    title_ = "<h1>" + element[0].xpath("div[1]/h1/text()"
                                                       ).extract()[0] + "</h1>"
                    p_remark_ = ""
                    for span in element[0].xpath("div[1]/div[1]/div[1]/span"):
                        p_remark_ += " " + str(span.xpath("text()"
                                                          ).extract()[0])  # 获取日期和来源
                    content = "<p>" + \
                              element[0].xpath("div[1]/div[3]/p/text()"
                                               ).extract()[0] + "</p>"
                    data = Selector(text=response.body).xpath(
                        "//*[@class='bta_context']")
                    if data:  # 由于标签中的文本被镶嵌的标签给分开了，用data.xpath("string(.)").extract()[0]可取全部文本
                        info = data.xpath("string(.)").extract()[0]
                    p_text__ = ""
                    for p_ in element[0].xpath("div[2]/p"):  # 获取资讯文章内容
                        if p_.xpath("strong/text()"):  # 文章中字体加粗的内容
                            p_text_ = "<strong>" + p_.xpath(
                                "strong/text()").extract()[0] + "</strong>"
                        elif p_.xpath("img"):  # 文章中带有图片的
                            p_text_ = "<img/>" + p_.xpath("img/@src").extract()[
                                0]
                        elif p_.xpath("a"):  # 排除文章内容中有广告语的内容
                            p_text_ = ""
                        else:
                            p_text_ = p_.xpath("text()").extract()[0]
                        p_text__ += "\n\t" + p_text_
                    article_ = title_ + "\n\t" + "<span>" + p_remark_ \
                               + "</span>" + "\n\t" + content + "\n\t" \
                               + info + p_text__
                    item['s3_key'] = upload_path(article_,
                                                 file_name + "article.txt",
                                                 content_type='text/plain; charset=utf-8')
            if item.get('image'):  # 把header image存到s3中
                image_name = file_name + item.get('image').split('/')[-1]
                image_url = "https://www.rong360.com" + item.get('image')
                img_response = requests.get(image_url,
                                            headers=headers.update(
                                                {'user-agent': get_user_agent()}))
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
