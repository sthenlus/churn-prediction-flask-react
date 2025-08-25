from celery import Celery

# Celery uygulamasını oluşturuyoruz.
# Backend (sonuçların saklandığı yer) ve Broker (görev kuyruğu) olarak Redis'i kullanıyoruz.
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['tasks']
)

celery_app.conf.update(
    task_track_started=True,
)