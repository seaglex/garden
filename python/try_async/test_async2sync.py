import asyncio


# 定义一个你需要调用的异步方法
async def async_task(name: str, delay: int) -> str:
    """示例异步方法：模拟耗时操作"""
    print(f"开始执行异步任务 {name}，延迟 {delay} 秒")
    await asyncio.sleep(delay)
    result = f"异步任务 {name} 执行完成"
    print(result)
    return result


# 定义普通的同步函数，在其中调用异步方法
def sync_function(task_name: str, delay: int) -> str:
    """同步函数中调用异步方法"""
    try:
        # 关键步骤1：获取当前正在运行的事件循环
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # 兜底：如果当前没有运行的循环（防止极端情况），创建新循环（不推荐，仅兜底）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # 关键步骤2：用已有循环执行异步函数，直到完成
    result = loop.run_until_complete(async_task(task_name, delay))
    return result


# 系统外层的异步主程序（已存在的异步上下文）
async def main():
    print("外层异步主程序启动")

    # 在异步上下文里调用同步函数，同步函数内部再调用异步方法
    sync_result = sync_function("测试任务", 2)
    print(f"同步函数获取到异步方法的结果：{sync_result}")

    print("外层异步主程序结束")


# 仅用于启动整个程序（外层的异步入口）
if __name__ == "__main__":
    asyncio.run(main())