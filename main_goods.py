# 这是一个示例 Python 脚本。

# 按 Alt+Shift+X 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import socket

import grpc
import signal,sys,os,argparse
from loguru import logger
#loguru  多线程 异步
#0、logger 日志级别
#1、add到日志
#2、回滚 老化  rotation
#3、压缩
#4、装饰器  @logger.catch
from concurrent import futures

from goods_srv.proto import goods_pb2_grpc

from goods_srv.handler.goods   import GoodsService

from common.grpc_health.v1 import health_pb2_grpc
from common.grpc_health.v1 import health


# 导入consul和配置文件
from common.register.consul import ConsulRegister
from goods_srv.settings import  settings

# sys.path.insert(0,"C:/Users/zhuhangxin/PycharmProjects/mxshop_srvs")# 一般不用绝对路径，需要使用相对路径
BASE_DIR=os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
print(BASE_DIR)
sys.path.insert(0,BASE_DIR)

def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+Shift+B 切换断点。

def onExit(signo,frame,service_id):
    register = ConsulRegister(settings.CONSUL_HOST, settings.CONSUL_PORT)
    logger.info(f"注销{service_id}进程")
    register.deregister(service_id)
    logger.info(f"注销{service_id}进程成功")
    logger.info('进程中断')
    print("后续处理")
    sys.exit(0)

def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp.bind(("",0))
    addr,port=tcp.getsockname()
    tcp.close()
    return port

def  server():
    parser = argparse.ArgumentParser()

    parser.add_argument('--server',nargs='?',type=str,default='192.168.18.179',help='Server address')
    parser.add_argument('--port',nargs='?',type=int,default=0,help='Port number')
    args = parser.parse_args()
    # 不想去掉指定端口或默认端口号的功能
    #必要的时候，可以自动生成
    if args.port ==0:
        port=get_free_tcp_port()
    else:
        port = args.port

    print(args)



#     logger.add("goods_srv/log/goods_{time}.log")#日志生成

    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    logger.critical("严重错误信息")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))


#     注册商品服务
    goods_pb2_grpc.add_GoodsServicer_to_server(GoodsService(),server)


#     注册健康检查
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer,server)

    server.add_insecure_port(f'{args.server}:{port}')

    import  uuid
    from functools import partial
    service_id = str(uuid.uuid1())
    '''
    ctrl + C  sigint
    sigterm   kill
    '''
    signal.signal(signal.SIGINT,partial(onExit,service_id=service_id))
    signal.signal(signal.SIGTERM,partial(onExit,service_id=service_id))#测试，不能通过IDE  是强杀进程、不能优雅退出
    #需要命令行执行，需要把当前路径加入到pythonpath



    logger.info(f"启动服务，ip为{args.server}，port为{port}")
#     print('start service on port 50051')
    server.start()
    logger.info("服务注册开始")

    register = ConsulRegister(settings.CONSUL_HOST, settings.CONSUL_PORT)
    if not register.register(name=settings.SERVICE_NAME, id=service_id, address=args.server, port=port, tags=settings.SERVICE_TAGS, check=None):
        logger.info("服务注册失败")
        sys.exit(0)
    logger.info("服务注册成功")

    server.wait_for_termination()

@logger.catch
def my_function(x, y, z):
    # An error? It's caught anyway!
    return 1 / (x + y + z)

if __name__ == '__main__':
    print_hi('PyCharm')
#     my_function(0,0,0)

    server()
# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
