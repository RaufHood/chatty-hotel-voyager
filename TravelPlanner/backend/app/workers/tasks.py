from celery import Celery
from app.core.settings import settings

app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

@app.task
def ping():
    return "pong"
