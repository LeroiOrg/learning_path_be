import json
import os
from google.cloud import pubsub_v1
from google.api_core import retry

PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_ID = os.getenv("TOPIC_ID", "preprocess-topic")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

publish_retry = retry.Retry(initial=1.0, maximum=10.0, multiplier=2.0, deadline=30.0)

def publish_credit_update(email: str, credits_change: int):
    message = {
        "event": "credit_update",
        "data": {
            "email": email,
            "credits_change": credits_change
        }
    }
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data=data)
    print(f"📨 Mensaje publicado a {topic_path}: {message}")
    return future.result()