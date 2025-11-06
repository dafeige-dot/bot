#!/usr/bin/env python
"""
启动脚本 - 解决导入路径问题
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入并运行主程序
if __name__ == "__main__":
    from app.main import main
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n收到中断信号，正在退出...")
    except Exception as e:
        print(f"程序异常退出: {e}")
        sys.exit(1)

