#!/bin/sh
#celery -B -A celery_app worker -f /code/logs/celery.log
scrapy crawl rong_spider
