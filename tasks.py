from celery_app import celery_app
import time

@celery_app.task
def process_upload(key: str, size: int):
    # simulate heavy processing - replace with real logic later
    time.sleep(5)   # pretend this is virus scanning, resizing, etc
    print(f"processed {key}, size={size}")
    return f"{key} processed successfully"