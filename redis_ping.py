import redis

r = redis.Redis(
    host='redis-19400.crce178.ap-east-1-1.ec2.redns.redis-cloud.com',
    port=19400,
    decode_responses=True,
    username="default",
    password="yXwA8P0O9gn5AT0pjaheQxaAfvdBoaho",
)

try:
    response = r.ping()
    print("PONG" if response else "No response")
except redis.exceptions.RedisError as e:
    print(f"Redis error: {e}")
