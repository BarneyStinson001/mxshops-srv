import abc
class Register(metaclass=abc.ABCMeta):  #抽象基类，继承必须实现下面的方法
    @abc.abstractmethod
    def register(self,name, id, address, port,tags,check):
        pass

    @abc.abstractmethod
    def deregister(self):
        pass

    @abc.abstractmethod
    def list_service(self):
        pass

    @abc.abstractmethod
    def filter_service(self,filter):
        pass