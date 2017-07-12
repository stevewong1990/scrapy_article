#!/bin/sh
celery -B -A scrapy_common.tasks worker -f /code/logs/celery.log
