import grpc
from loguru import logger
from user_srv.proto import user_pb2_grpc,user_pb2

class UserTest():
    def __init__(self):
        channel = grpc.insecure_channel("127.0.0.1:50051")
        self.stub=user_pb2_grpc.UserStub(channel)

    def user_list(self,pageSize,pageNo):
        rsp: user_pb2.UserListResponse = self.stub.GetUserList(user_pb2.PageInfo(pageNo=pageNo,pageSize=pageSize))
        print(rsp.total)
        for user in rsp.data:
#             print(user)
            print(f"{user.mobile},{user.nickName},{user.birthday}")
    def getbyid(self, id):
#         rsp: user_pb2.UserInfoResponse = self.stub.GetUserById(id)
        rsp: user_pb2.UserInfoResponse = self.stub.GetUserById(user_pb2.IdRequest(id=id))

        print(rsp.mobile,rsp.nickName)

    def getbymobile(self,mobile):
#         rsp: user_pb2.UserInfoResponse = self.stub.GetUserByMobile(mobile)
        rsp: user_pb2.UserInfoResponse = self.stub.GetUserByMobile(user_pb2.MobileRequest(mobile=mobile))
        print(rsp.mobile,rsp.nickName,rsp.birthday)#modile
        return rsp
    def createUser(self,nickname,mobile,password):
        rsp: user_pb2.UserInfoResponse = self.stub.CreateUser(user_pb2.CreateUserInfo(nickName=nickname,password=password,mobile=mobile))
        print(rsp.id)

    def updateuser(self,id,nickname,gender,birthday):
        rsp: user_pb2.UserInfoResponse = self.stub.UpdateUser(user_pb2.UpdateUserInfo(id=id,nickname=nickname,gender=gender,birthday=birthday))
        print(rsp)
    @logger.catch
    def checkpassword(self,password,encrypted):
        rsp: user_pb2.CheckPasswordResponse = self.stub.CheckPassword(user_pb2.PasswordCheck(password=password,encrypted=encrypted))
        print(rsp)
if __name__ == "__main__":
    user = UserTest()
#     user.user_list(8,1)
#     print("test getbyid")
#     user.getbyid("4")
#     print("test getbymobile")
#     user.getbymobile("18812345674")
#     user.updateuser("1","lisi","male",1658674221)
#

#     user.createUser("test0724","12345678910","123456")
    u1=user.getbymobile("12345678910")
    print(u1.password)
    print(user.checkpassword("123456",u1.password))