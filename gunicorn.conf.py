# https://docs.gunicorn.org/en/latest/settings.html

wsgi_app = 'tako.wsgi:application'
bind = '0.0.0.0:8000'
workers = 1
worker_class = 'sync'
accesslog = '-'
loglevel = 'info'
