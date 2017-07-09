#!/bin/sh
celery -B -A task.celery_app worker -f /code/logs/celery.log &
PYTHONPATH='/code' python3 task/wechat_bot.py