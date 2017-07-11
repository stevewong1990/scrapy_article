FROM aciobanu/scrapy

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

ADD /e/workspace/rong_360 /code

WORKDIR /code

RUN mkdir -p logs

ENTRYPOINT ["sh", "entry.sh"]