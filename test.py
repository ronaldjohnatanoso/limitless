import redis

# Connect to your local Redis server
r = redis.Redis(host='localhost', port=6379)

# Set a test key
r.set('test_key', 'hello-from-local')

# Optional: confirm it's set
print(r.get('test_key'))
