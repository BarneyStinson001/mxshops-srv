import time
import grpc
from peewee import DoesNotExist
from user_srv.model.models import User
from user_srv.proto import user_pb2,user_pb2_grpc
from loguru import logger
from passlib.hash import pbkdf2_sha256
from datetime import date
from google.protobuf import empty_pb2

class UserService(user_pb2_grpc.UserServicer):
    def convert_user_to_rsp(self, user):
        user_info = user_pb2.UserInfoResponse()

        user_info.id = user.id
        user_info.password = user.password
        user_info.mobile = user.mobile

        user_info.role = user.role
        #if user_info.nickname:#字段错误
        #if user_info.nickName:#是看user的字段
        if user.nickname:
            user_info.nickName = user.nickname
        #if user_info.birthday:
        if user.birthday:
            logger.info(user.birthday)
            user_info.birthday = int(time.mktime(user.birthday.timetuple()))
            logger.info(user.birthday)
        if user.gender:#不存在的要非空判断
            user_info.gender = user.gender
        return user_info

    @logger.catch
    def GetUserList(self,request: user_pb2.PageInfo,context):
        #获取用户列表
        #rsp = user_pb2_grpc.UserListResponse()#包错误
        rsp = user_pb2.UserListResponse()

        users = User.select()
        #计算总数
        rsp.total = users.count()
        #分页
        print("请求用户列表服务")
        pageNo= 1#
        pageSize= 10#默认值，每页10个
        start = 0#默认值，从第一个开始
        if request.pageSize:
            pageSize = int(request.pageSize)
        if request.pageNo:
            pageNo= request.pageNo
        start=pageSize*(pageNo-1)
        users = users.limit(pageSize).offset(start)
        # print(users)
        #先从数据库对象user转化成响应的userinforesponse
        for user in users:
            #user_info = user_pb2_grpc.UserInfoResponse()#包错误
            user_info = self.convert_user_to_rsp(user)
            # print(user_info)
            rsp.data.append(user_info)
            # print(len(rsp.data))
        # print(rsp.total)
        return rsp

    @logger.catch
    def GetUserByMobile(self,request: user_pb2.MobileRequest,context):
        try:
            user = User.get(User.mobile==request.mobile)
            return self.convert_user_to_rsp(user)#  和上面共用一个转换
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
            return user_pb2.UserInfoResponse()


    @logger.catch
    def GetUserById(self,request: user_pb2.IdRequest,context):
        try:
            user = User.get(User.id==request.id)
            return self.convert_user_to_rsp(user)#  和上面共用一个转换
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
            return user_pb2.UserInfoResponse()


    @logger.catch
    def CreateUser(self,request: user_pb2.CreateUserInfo,context):
        try:
            user = User.get(User.mobile==request.mobile)
            context.set_code(grpc.StatusCode.AlREADY_EXISTS)
            context.ser_details("用户已存在")
            return user_pb2.UserInfoResponse()
        except DoesNotExist as e:
            pass

        user = User()
        user.nickname=request.nickName
#         user.password=request.password#要保存成密文
        user.password=pbkdf2_sha256.hash(request.password)
        user.mobile= request.mobile
        user.save()

        return self.convert_user_to_rsp(user)

    @logger.catch
    def UpdateUser(self,request: user_pb2.UpdateUserInfo,context):
        try:
            user = User.get(User.id==request.id)
            user.nickname= request.nickname
            user.gender = request.gender
            user.birthday = date.fromtimestamp(request.birthday)
            user.save()
            return empty_pb2.Empty()
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
            return user_pb2.UserInfoResponse()

    @logger.catch
    def CheckPassword(self,request: user_pb2.PasswordCheck,context):
        print(request.password,request.encrypted)
        return user_pb2.CheckPasswordResponse(success=pbkdf2_sha256.verify(request.password,request.encrypted))