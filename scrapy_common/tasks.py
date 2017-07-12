from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_article.spiders.rong_360_crawl import Rong360Spider
from celery import Celery

app = Celery('spider')
app.config_from_object('celery_config')


@app.task
def crawl():
    process = CrawlerProcess(get_project_settings())
    process.crawl(Rong360Spider)
    process.start()

