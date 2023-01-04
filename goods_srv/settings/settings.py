from playhouse.pool import PooledMySQLDatabase
# 一段时间不连接会断开，再使用会抛出异常（mysql gone away） 所以还要用下面的包

from playhouse.shortcuts import ReconnectMixin

import nacos
import json
from loguru import logger


class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    # python的mro
    pass


# MYSQL_DB= "mxshop_user_srv"
# MYSQL_HOST="192.168.18.160"
# MYSQL_PORT= 3306
# MYSQL_USER= "root"
# MYSQL_PASSWORD= "root"
#
# #consul配置
# CONSUL_HOST="192.168.18.160"
# CONSUL_PORT=8500
#
# # 服务相关配置
# SERVICE_NAME="user-srv"
# SERVICE_TAGS=["python","srv"]


# 以上配置都从nacos读取，仅配置nacos
# 配置nacos
NACOS = {
    "Host": "192.168.18.160",
    "Port": 8848,
    "NameSpace": "eb98a308-3a75-45a7-bb0c-38ff234f497a",
    "User": "nacos",
    "Password": "nacos",
    "DataId": "goods-srv.json",
    "Group": "dev"
}
# 获取配置

client = nacos.NacosClient(f"{NACOS['Host']}:{NACOS['Port']}", namespace=f"{NACOS['NameSpace']}",
                           username=f"{NACOS['User']}", password=f"{NACOS['Password']}")
data_id = f'{NACOS["DataId"]}'
group = f'{NACOS["Group"]}'
json_data = json.loads(client.get_config(data_id, group))
logger.info(json_data)

MYSQL_DB = json_data['mysql']['db']
MYSQL_HOST = json_data['mysql']['host']
MYSQL_PORT = json_data['mysql']['port']
MYSQL_USER = json_data['mysql']['user']
MYSQL_PASSWORD = json_data['mysql']['password']

# consul配置
CONSUL_HOST = json_data['consul']['host']
CONSUL_PORT = json_data['consul']['port']

# 服务相关配置
SERVICE_NAME = json_data['name']
SERVICE_TAGS = json_data['tags']

db = ReconnectMySQLDatabase(database=MYSQL_DB, host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
                            password=MYSQL_PASSWORD)
