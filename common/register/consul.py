import consul,requests

from  common.register import base#引入基类

class ConsulRegister(base.Register):
    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.c=consul.Consul(host=host,port=port)

    def register(self,name, id, address, port,tags,check):
        if check==None:
            check={
                "GRPC":f"{address}:{port}",
                "GRPCUseTLS":False,
                "Timeout":"5s",
                "Interval":"5s",
                "DeregisterCriticalServiceAfter":"15s"
            }
        else:
            check=check
        return self.c.agent.service.register(name=name,service_id=id,address=address,port=port,tags=tags,check=check)

    def deregister(self,id):
        return self.c.agent.service.deregister(id)

    def list_service(self):
        return self.c.agent.services()

    def filter_service(self,filter):
        #consul没有，需要自己实现
        url= f"http://{self.host}:{self.port}/v1/agent/services"
        params={
            "filter":filter
        }
        return requests.get(url,params=params).json()
