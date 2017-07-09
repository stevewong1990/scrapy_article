from celery import Celery

app = Celery('wechat')
app.config_from_object('config')

if __name__ == '__main__':
    app.start()
