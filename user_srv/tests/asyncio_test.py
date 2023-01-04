import  asyncio

# 协程函数
async def  p(n):
    while True:
        print(n)
                # 协程中sleep需要使用asyncio的sleep.time的sleep方法是阻塞的
        await asyncio.sleep(1)

#主协程
async def main():
    for i in range(1000000):
        # await p(i) #会等待函数结束 ，但一时半会不会结束。作用：将协程运行起来，然后阻塞住
        # print("代码不能运行到这")

        # 方法
        asyncio.create_task(p(i))#这个方法会退出。因为主协程退出了
    await asyncio.sleep(10000)

asyncio.run(main())