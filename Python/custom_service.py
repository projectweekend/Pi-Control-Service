from rpc import RPCService


RABBIT_URL = os.getenv('RABBIT_URL', None)
assert RABBIT_URL

DEVICE_KEY = os.getenv('DEVICE_KEY', None)
assert DEVICE_KEY
