"""
启动演示模式的简化脚本
"""

import subprocess
import sys
import os

def main():
    """主函数"""
    print("=" * 60)
    print("启动灵光问题树 - 演示模式")
    print("=" * 60)
    print()

    # 设置环境变量以跳过Streamlit的交互提示
    env = os.environ.copy()
    env["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "1"
    env["STREAMLIT_GLOBAL_SHOW_WARNING_ON_DIRECT_EXECUTION"] = "0"
    env["STREAMLIT_GLOBAL_SHOW_TUTORIALS"] = "false"
    env["STREAMLIT_GLOBAL_GATHER_USAGE_STATS"] = "false"

    # 构建命令
    cmd = [
        sys.executable,
        "-m", "streamlit", "run", "demo.py",
        "--global.developmentMode", "false",
        "--browser.gatherUsageStats", "false"
    ]

    print("启动命令:", " ".join(cmd))
    print()
    print("应用将在浏览器中打开...")
    print("请访问: http://localhost:8501")
    print("按 Ctrl+C 停止应用")
    print("=" * 60)
    print()

    try:
        # 运行Streamlit
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n用户中断，停止应用...")
    except Exception as e:
        print(f"启动失败: {e}")
        print("\n备用方案:")
        print("1. 手动运行: python -m streamlit run demo.py")
        print("2. 当出现邮箱输入提示时，直接按回车跳过")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())