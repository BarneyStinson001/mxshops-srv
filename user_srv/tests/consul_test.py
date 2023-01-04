import requests, consul


def register(name, id, address, port):
    url = "http://192.168.18.160:8500/v1/agent/service/register"
    rsp = requests.put(url, headers={"Content-type": "application/json"},
                       json={
                           "Name": name,
                           "Address": address,
                           "Port": port,
                           "Id": id,
                           "Tags": ["service", "mxshop-srv"]})
    if rsp.status_code == 200:
        print("注册成功")
    else:
        print("注册失败：%d" % rsp.status_code)


def deregister(id):
    url = f"http://192.168.18.160:8500/v1/agent/service/deregister/{id}"
    rsp = requests.put(url, headers={"Content-type": "application/json"})
    if rsp.status_code == 200:
        print("注销成功")
    else:
        print("注销失败：%d" % rsp.status_code)


def registerByHTTP(name, id, address, port):
    url = "http://192.168.18.160:8500/v1/agent/service/register"
    rsp = requests.put(url, headers={"Content-type": "application/json"},
                       json={
                           "Name": name,
                           "Address": address,
                           "Port": port,
                           "Id": id,
                           "Tags": ["service", "mxshop-srv"],
                           "Check": {
                               "HTTP": f"http://{address}:{port}/health",
                               "Timeout": "5s",  # 默认1min
                               "Interval": "5s",
                               "DeregisterCriticalServiceAfter": "5s"  #
                           }
                       })
    if rsp.status_code == 200:
        print("注册成功")
    else:
        print("注册失败：%d" % rsp.status_code)


def registerByGRPC(name, id, address, port):
    url = "http://192.168.18.160:8500/v1/agent/service/register"
    rsp = requests.put(url, headers={"Content-type": "application/json"},
                       json={
                           "Name": name,
                           "Address": address,
                           "Port": port,
                           "Id": id,
                           "Tags": ["service", "mxshop-srv"],
                           "Check": {
                               "GRPC": f"{address}:{port}",
                               "GRPCUseTLS": False,
                               "Timeout": "5s",  # 默认1min
                               "Interval": "5s",
                               "DeregisterCriticalServiceAfter": "5s"  #
                           }
                       })
    if rsp.status_code == 200:
        print("注册成功")
    else:
        print("注册失败：%d" % rsp.status_code)


def list_service():
    url="http://192.168.18.160:8500/v1/agent/services"
    rsp = requests.get(url)
    print(rsp.json())


def filter_service(name):
    url="http://192.168.18.160:8500/v1/agent/services"
    params={
        "filter":f'Service == "{name}"',
    }
    rsp=requests.get(url,params=params)
    print(rsp.json())



if __name__ == "__main__":
    #     register("mxshop-svr","mxshop-svr","127.0.0.1",50051)
    #     deregister("mxshop-svr")

    #     注册web层
    #     register("mxshop-web","mxshop-web","127.0.0.1",8021)
    #     deregister("mxshop-web")

    # registerByGRPC("mxshop-svr", "mxshop-svr", "192.168.18.179", 50051)
    # registerByHTTP("mxshop-web", "mxshop-web", "192.168.18.179", 8021)  # consul在虚拟机上，127.0.0.1是指虚拟机ip

    list_service()
    filter_service("user-srv")

