import consul
import json
from urllib.parse import urlparse

class ConsulHelper:
    def __init__(self, host='consul', port=8500, url=None, token=None):
        if url:
            parsed = urlparse(url)
            host = parsed.hostname or host
            port = parsed.port or port
        self.c = consul.Consul(host=host, port=port, token=token or "")

    def get_config(self, key):
        _, data = self.c.kv.get(key)
        if data:
            raw_val = data['Value'].decode('utf-8')
            try:
                return json.loads(raw_val)
            except json.JSONDecodeError:
                return raw_val
        return {}