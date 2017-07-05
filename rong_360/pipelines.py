# -*- coding: utf-8 -*-
import pymysql.cursors
from scrapy.conf import settings


def db_handle():
    coon = pymysql.connect(
        host=settings['MYSQL_HOST'],
        user=settings['MYSQL_USER'],
        passwd=settings['MYSQL_PASSWD'],
        db=settings['MYSQL_DBNAME'],
        charset='utf8',
        use_unicode=True
    )
    return coon


class Rong360Pipeline(object):

    def process_item(self, item, spider):
        dbObject = db_handle()
        cursor = dbObject.cursor()
        data = (item['raw_url'], item.get('title_text'), item.get('desc_text'),
                item['image'], item.get('source'), item.get('s3_key'),
                item['status'], item['created_at'], item['article_time'],
                item['platform'], item['section'])
        sql = 'replace into v2_rawpromotion (raw_url, title_text, desc_text, image, ' \
              'source, s3_key, status, created_at, article_time, platform, ' \
              'section) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            cursor.execute(sql, data)
            dbObject.commit()
        except BaseException as e:
            print('***************sql err************* %s' % e)
            dbObject.rollback()
        return item
