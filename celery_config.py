from celery.schedules import crontab

# redis
REDIS_HOST = ''
REDIS_PORT = 6379
REDIS_NO = 0
REDIS_USER = ''
REDIS_PASSWD = ''

#celery
CELERY_TASK_SERIALIZER = 'msgpack'
CELERYD_MAX_TASKS_PER_CHILD = 1
CELERY_RESULT_SERILIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_IMPORTS = ("scrapy_common.tasks")
CELERYBEAT_SCHEDULE = {
    'rong_360': {
        'task': 'scrapy_common.tasks.crawl',
        'schedule': crontab(hour='*/3'),
        'args': ()
    },
}

try:
    from scrapy_article.local_settings import *  # noqa
except ImportError:
    pass

BROKER_URL = 'redis://{}:{}@{}:6379'.format(REDIS_USER, REDIS_PASSWD,
                                            REDIS_HOST)
CELERY_RESULT_BACKEND = BROKER_URL
