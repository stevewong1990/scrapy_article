# -*- coding: utf-8 -*-
import os

# Scrapy settings for rong_360 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapy_article'

SPIDER_MODULES = ['scrapy_article.spiders']
NEWSPIDER_MODULE = 'scrapy_article.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'rong_360 (+http://www.yourdomain.com)'  # 爬取得默认User-Agent

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1  # 并发请求的最大值

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1  # 对单个网站进行并发请求的最大值
# CONCURRENT_REQUESTS_PER_IP = 16  # 对单个IP进行并发请求的最大值

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'rong_360.middlewares.Rong360SpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy_article.random_useragent.RandomUserAgentMiddleware': 400,
    'scrapy_article.HttpProxyMiddleware.HttpProxyMiddleware': 999,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

DOWNLOAD_TIMEOUT = 15

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy_article.pipelines.ScrapyArticlePipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# mysql
MYSQL_HOST = ''
MYSQL_DBNAME = ''
MYSQL_USER = ''
MYSQL_PASSWD = ''

# S3
S3_ACCESS_KEY = "AKIAOO4XXXWGJDCMBROQ"
S3_SECRET_KEY = "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"

LOG_FILE = 'logs/spider.log'
LOG_FORMAT = '%(levelname)s %(asctime)s [%(name)s:%(module)s:%(funcName)s:%(lineno)s] [%(exc_info)s] %(message)s'

LOG_LEVEL = 'INFO'


try:
    from scrapy_article.local_settings import *  # noqa
except ImportError:
    pass
