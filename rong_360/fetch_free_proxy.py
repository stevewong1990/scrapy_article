# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib.request
import requests
import json
import logging

logger = logging.getLogger(__name__)

HOST = '192.168.1.130'
PROXY_HOST = 'http://{host}:8432'.format(host=HOST)
PROXY_URL = PROXY_HOST + '/?types=0&count=100&country=国内'


def get_html(url):
    request = urllib.request.Request(url)
    request.add_header("User-Agent",
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36")
    html = urllib.request.urlopen(request)
    return html.read()


def get_soup(url):
    soup = BeautifulSoup(get_html(url), "html.parser")
    return soup


def fetch_kxdaili(page):
    """
    从www.kxdaili.com抓取免费代理
    """
    proxies = []
    try:
        url = "http://www.kxdaili.com/dailiip/1/%d.html" % page
        soup = get_soup(url)
        table_tag = soup.find("table", attrs={"class": "segment"})
        trs = table_tag.tbody.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            ip = tds[0].text
            port = tds[1].text
            latency = tds[4].text.split(" ")[0]
            if float(latency) < 0.5:  # 输出延迟小于0.5秒的代理
                proxy = "%s:%s" % (ip, port)
                proxies.append(proxy)
    except:
        logger.warning("fail to fetch from kxdaili")
    return proxies


def img2port(img_url):
    """
    mimvp.com的端口号用图片来显示, 本函数将图片url转为端口, 目前的临时性方法并不准确
    """
    code = img_url.split("=")[-1]
    if code.find("AO0OO0O") > 0:
        return 80
    else:
        return None


def fetch_mimvp():
    """
    从http://proxy.mimvp.com/free.php抓免费代理
    """
    proxies = []
    try:
        url = "http://proxy.mimvp.com/free.php?proxy=in_hp"
        soup = get_soup(url)
        table = soup.find("div", attrs={"id": "list"}).table
        tds = table.tbody.find_all("td")
        for i in range(0, len(tds), 10):
            id = tds[i].text
            ip = tds[i + 1].text
            port = img2port(tds[i + 2].img["src"])
            response_time = tds[i + 7]["title"][:-1]
            transport_time = tds[i + 8]["title"][:-1]
            if port is not None and float(response_time) < 1:
                proxy = "%s:%s" % (ip, port)
                proxies.append(proxy)
    except:
        logger.warning("fail to fetch from mimvp")
    return proxies


def fetch_xici():
    """
    http://www.xicidaili.com/nn/
    """
    proxies = []
    try:
        url = "http://www.xicidaili.com/nn/"
        soup = get_soup(url)
        table = soup.find("table", attrs={"id": "ip_list"})
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tr = trs[i]
            tds = tr.find_all("td")
            ip = tds[1].text
            port = tds[2].text
            speed = tds[6].div["title"][:-1]
            latency = tds[7].div["title"][:-1]
            if float(speed) < 3 and float(latency) < 1:
                proxies.append("%s:%s" % (ip, port))
    except:
        logger.warning("fail to fetch from xici")
    return proxies


def fetch_mimvp_vip():
    proxies = []
    try:
        url = 'http://proxy.mimvp.com/api/fetch.php?orderid=860161120220445752&num=200' \
              '&result_fields=1,2&result_sort_field=2&result_format=json'
        r = requests.get(url)
        text = json.loads(r.text)
        proxies = [proxy['ip:port'] for proxy in text['result']]
    except:
        logger.warning("fail to fetch from mimvp_vip")
    return proxies


def fetch_ip181():
    """
    http://www.ip181.com/
    """
    proxies = []
    try:
        url = "http://www.ip181.com/"
        soup = get_soup(url)
        table = soup.find("table")
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tds = trs[i].find_all("td")
            ip = tds[0].text
            port = tds[1].text
            latency = tds[4].text[:-2]
            if float(latency) < 1:
                proxies.append("%s:%s" % (ip, port))
    except Exception as e:
        logger.warning("fail to fetch from ip181: %s" % e)
    return proxies


def fetch_httpdaili():
    """
    http://www.httpdaili.com/mfdl/
    更新比较频繁
    """
    proxies = []
    try:
        url = "http://www.httpdaili.com/mfdl/"
        soup = get_soup(url)
        table = soup.find("div", attrs={"kb-item-wrap11"}).table
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            try:
                tds = trs[i].find_all("td")
                ip = tds[0].text
                port = tds[1].text
                type = tds[2].text
                if type == u"匿名":
                    proxies.append("%s:%s" % (ip, port))
            except:
                pass
    except Exception as e:
        logger.warning("fail to fetch from httpdaili: %s" % e)
    return proxies


def fetch_66ip():
    """
    http://www.66ip.cn/
    每次打开此链接都能得到一批代理, 速度不保证
    """
    proxies = []
    try:
        # 修改getnum大小可以一次获取不同数量的代理
        url = "http://www.66ip.cn/nmtq.php?getnum=10&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip"
        content = get_html(url)
        urls = content.split("</script>")[-1].split("<br />")
        for u in urls:
            if u.strip():
                proxies.append(u.strip())
    except Exception as e:
        logger.warning("fail to fetch from httpdaili: %s" % e)
    return proxies


def check(proxy):
    url = "https://www.chandashi.com/ranking/index/type/free/country/cn/date/20161125.html"
    proxies = {'https': "http://" + proxy}

    try:
        r = requests.get(url, proxies=proxies, timeout=1)
        return r.status_code == 200
    except Exception as e:
        return False


def get_proxies():
    proxies = []
    resp = requests.get(PROXY_URL)
    if resp.status_code == 200:
        for i in json.loads(resp.text):
            proxies.append('{}:{}'.format(i[0], i[1]))
        return proxies
    else:
        logger.error('cant connect proxy')


def fetch_all(endpage=2):
    proxies = []
    # proxies += fetch_mimvp_vip()
    # print(len(proxies))
    # for i in range(1, endpage):
    #     proxies += fetch_kxdaili(i)
    # proxies += fetch_mimvp()
    # proxies += fetch_xici()
    # proxies += fetch_ip181()
    # proxies += fetch_httpdaili()
    # proxies += fetch_66ip()
    proxies += get_proxies()

    valid_proxies = []
    logger.info("checking proxyes validation")
    for p in proxies:
        if check(p):
            print(p)
            valid_proxies.append(p)
    return valid_proxies


if __name__ == '__main__':
    import sys

    root_logger = logging.getLogger("")
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(name)-8s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S', )
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    proxies = fetch_all()
    for p in proxies:
        print(p)
