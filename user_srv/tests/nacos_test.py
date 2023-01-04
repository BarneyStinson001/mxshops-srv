import nacos

# Both HTTP/HTTPS protocols are supported, if not set protocol prefix default is HTTP, and HTTPS with no ssl check(verify=False)
# "192.168.3.4:8848" or "https://192.168.3.4:443" or "http://192.168.3.4:8848,192.168.3.5:8848" or "https://192.168.3.4:443,https://192.168.3.5:443"
SERVER_ADDRESSES = "192.168.18.160:8848"
NAMESPACE = "3be35766-c3a5-4625-a057-9040dd328691"

# no auth mode
client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE,username="nacos",password="nacos")
# auth mode
#client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE, ak="{ak}", sk="{sk}")

# get config
data_id = "user-srv.yaml"
group = "DEFAULT_GROUP"
print(type(client.get_config(data_id, group)))#返回的是字符串类型  ，用json加载下


import  json
json_data =json.loads(client.get_config(data_id,group))
print(json_data)

def test_callback(args):
    print("配置文化变化")
    print(args)

if __name__=='__main__':
    client.add_config_watcher(data_id,group,test_callback)

    import time
    time.sleep(3000)