# debug_run.py - PyCharm 调试 ADK 专用脚本
from google.adk.cli import main

# 等价于命令行：adk run .
if __name__ == "__main__":
    # 运行 Agent（和 adk run . 完全一致）
    main(["run", "."])

    # 👇 如果要调试 Web UI，替换成这行
    # main(["web"])