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


class Pipeline(object):

    def process_item(self, item, spider):
        dbObject = db_handle()
        cursor = dbObject.cursor()
        data = (item['raw_url'], item.get('title'), item.get('desc'),
                item['image'], item.get('source'), item.get('s3_key'),
                item['status'], item['created_at'], item['article_time'],
                item['platform'], item['section'])
        sql = 'replace into v2_rawpromotion (raw_url, title, `desc`, image, ' \
              'source, s3_key, status, created_at, article_time, platform, ' \
              'section) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            cursor.execute(sql, data)
            dbObject.commit()
        except BaseException as e:
            logger.error('***************sql err************* %s' % e)
            dbObject.rollback()
        return item
