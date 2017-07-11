from celery import Celery

app = Celery('spider')
app.config_from_object('settings')

if __name__ == '__main__':
    app.start()
