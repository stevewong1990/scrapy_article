FROM hub.creditdev.com/python:ubuntu
EXPOSE 8110

ADD . /code
WORKDIR /code

ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt -i http://pypi.douban.com/simple/

RUN mkdir -p logs

ENTRYPOINT ["sh", "entry.sh"]