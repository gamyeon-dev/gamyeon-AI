import consul
import json

class ConsulHelper:
    def __init__(self, host='consul', port=8500):
        self.c = consul.Consul(host=host, port=port)

    def get_config(self, key):
        """Consul KV에서 설정값을 가져와 딕셔너리로 반환
        
        args :
            key: consul상의 key

        returns :
            key에 해당되는 value의 딕셔너리
        """
        _, data = self.c.kv.get(key)
        if data:
            raw_val = data['Value'].decode('utf-8')
            try:
                return json.loads(raw_val)
            except json.JSONDecodeError:
                return raw_val
        return {} # 값이 없으면 빈 딕셔너리 반환