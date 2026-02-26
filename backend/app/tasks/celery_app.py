from celery import Celery\ncelery_app = Celery('tasks')\ncelery_app.config_from_object('app.core.config', namespace='CELERY')
