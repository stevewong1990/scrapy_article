# -*- coding: utf-8 -*-

# Scrapy settings for rong_360 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'rong_360'

SPIDER_MODULES = ['rong_360.spiders']
NEWSPIDER_MODULE = 'rong_360.spiders'

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
    'rong_360.HttpProxyMiddleware.HttpProxyMiddleware': 999,
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
    'rong_360.pipelines.Rong360Pipeline': 300,
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
MYSQL_HOST = '139.196.120.201'
MYSQL_DBNAME = 'spider'
MYSQL_USER = 'lyloan'
MYSQL_PASSWD = 'Lyloan$1'

# S3
S3_ACCESS_KEY = "AKIAOO4XXXWGJDCMBROQ"
S3_SECRET_KEY = "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"


DB_URI = ''

# redis
REDIS_HOST = ''
REDIS_PORT = 6379
REDIS_NO = 0
REDIS_USER = ''
REDIS_PASSWD = ''

# celery
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_RESULT_SERILIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_IMPORTS = ("task.format_article", "task.rong_360_article")
CELERYBEAT_SCHEDULE = {
    'format_account': {
        'task': 'task.format_article.format_wechat_article',
        'schedule': crontab(hour='*/3', minute=0),
        'args': ()
    },
    # 'wechat_bot': {
    #     'task': 'task.wechat_bot.send_message',
    #     'schedule': crontab(hour='10, 18', minute=36),
    #     'args': ()
    # }
    'rong_360_format': {
        'task': 'task.rong_360_article.format_rong360_article',
        'schedule': crontab(hour='*/3', minute=0),
        'args': ()
    },
}

try:
    from local_settings import *  # noqa
except ImportError:
    pass

BROKER_URL = 'redis://{}:{}@{}:6379'.format(REDIS_USER, REDIS_PASSWD,
                                            REDIS_HOST)  # noqa
CELERY_RESULT_BACKEND = BROKER_URL
