# -*- coding: utf-8 -*-

import boto3
import logging

from scrapy_article.settings import S3_ACCESS_KEY, S3_SECRET_KEY

logger = logging.getLogger(__name__)
_s3 = None
_s3_res = None


def _get_s3():
    global _s3
    if _s3:
        return _s3
    _s3 = boto3.client('s3', 'cn-north-1',
                       aws_access_key_id=S3_ACCESS_KEY,
                       aws_secret_access_key=S3_SECRET_KEY, )
    return _s3


def _get_s3_resource():
    global _s3_res
    if _s3_res:
        return _s3_res
    _s3_res = boto3.resource('s3', 'cn-north-1',
                             aws_access_key_id=S3_ACCESS_KEY,
                             aws_secret_access_key=S3_SECRET_KEY, )
    return _s3_res


def generate_download_url(key, bucket='79res'):
    return _get_s3().generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key
        }
    )


def upload_content(content, filename, content_type='string', bucket="79res"):
    try:
        bucket = _get_s3_resource().Bucket(bucket)
        return bucket.put_object(Body=content, Key=filename,
                                 ContentType=content_type)
    except:
        logger.warning("cannot upload %s to %s", filename, bucket, exc_info=1)
        return None
