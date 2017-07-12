# -*- coding: utf-8 -*-
import pymysql.cursors
import logging

from scrapy.conf import settings

logger = logging.getLogger(__name__)


def db_handle():
    conn = pymysql.connect(
        host=settings['MYSQL_HOST'],
        user=settings['MYSQL_USER'],
        passwd=settings['MYSQL_PASSWD'],
        db=settings['MYSQL_DBNAME'],
        charset='utf8',
        use_unicode=True
    )
    return conn


class ScrapyArticlePipeline(object):

    def process_item(self, item, spider):
        data = (item['raw_url'], item.get('title'), item.get('desc'),
                item['image'], item.get('source'), item.get('s3_key'),
                item['status'], item['created_at'], item['article_time'],
                item['platform'], item['section'])
        sql = 'replace into v2_rawpromotion (raw_url, title, `desc`, image, ' \
              'source, s3_key, status, created_at, article_time, platform, ' \
              'section) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        operation_database(sql, data=data)
        return item


def get_all_rawl_url():
    sql = 'select vr.raw_url from v2_rawpromotion vr'
    raw_url_list = operation_database(sql).fetchall()
    return raw_url_list


def operation_database(sql, data=None):
    db_object = db_handle()
    cursor = db_object.cursor()
    try:
        cursor.execute(sql, data)
        db_object.commit()
    except BaseException as e:
        logger.error('sql exception is %s', e)
        db_object.rollback()
    return cursor
