# backend/app/queue/redis_client.py
# 🧩 Handles connecting to Redis and publishing messages

import redis
from backend.app.core.config import settings  # ✅ fixed import path

# Create a global Redis client
redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

def push_message(queue_name: str, data: dict):
    """
    Push a JSON-safe dict into a Redis list (FIFO queue).
    Args:
        queue_name (str): The name of the queue (e.g. "messages").
        data (dict): The message payload.
    """
    import json
    payload = json.dumps(data)
    redis_client.rpush(queue_name, payload)
    print(f"📨 Message pushed to queue '{queue_name}'")
