FROM stibbons31/alpine-s6-python3:latest

RUN \
 apk add --no-cache --virtual=build-dependencies \
    autoconf \
    automake \
    freetype-dev \
    g++ \
    gcc \
    jpeg-dev \
    lcms2-dev \
    libffi-dev \
    libpng-dev \
    libwebp-dev \
    linux-headers \
    make \
    openjpeg-dev \
    openssl-dev \
    python3-dev \
    tiff-dev \
    zlib-dev

ADD requirements.txt requirements.txt
RUN \
   pip install -r requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

ADD . /code
WORKDIR /code

RUN mkdir -p logs

ENTRYPOINT ["sh", "entry.sh"]