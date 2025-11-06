#!/usr/bin/env python
"""
配置检查脚本 - 验证 .env 文件配置是否正确
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def check_config():
    """检查配置"""
    print("=" * 60)
    print("  Telegram Bot 配置检查")
    print("=" * 60)
    print()
    
    # 检查 .env 文件是否存在
    if not Path(".env").exists():
        print("❌ [错误] .env 文件不存在！")
        print()
        print("解决方法：")
        print("  1. 复制模板文件：Copy-Item env.template .env")
        print("  2. 编辑 .env 文件，填入配置")
        print()
        return False
    
    print("✅ .env 文件存在")
    print()
    
    # 尝试加载配置
    try:
        from app.config import settings
        print("✅ 配置加载成功")
        print()
    except Exception as e:
        print(f"❌ [错误] 配置加载失败：{e}")
        print()
        print("请检查 .env 文件格式是否正确")
        return False
    
    # 检查必填配置项
    print("-" * 60)
    print("必填配置项检查：")
    print("-" * 60)
    
    checks = []
    
    # Telegram Bot Token
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_TOKEN != "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11":
        print(f"✅ TELEGRAM_BOT_TOKEN: {settings.TELEGRAM_BOT_TOKEN[:20]}...")
        checks.append(True)
    else:
        print("❌ TELEGRAM_BOT_TOKEN: 未配置或使用示例值")
        print("   请从 @BotFather 获取真实的 Token")
        checks.append(False)
    
    # 管理员ID
    admin_ids = settings.get_admin_ids()
    if admin_ids and admin_ids != [123456789]:
        print(f"✅ ADMIN_USER_IDS: {admin_ids}")
        checks.append(True)
    else:
        print("❌ ADMIN_USER_IDS: 未配置或使用示例值")
        print("   请填入你的 Telegram ID（从 @userinfobot 获取）")
        checks.append(False)
    
    # 密钥检查
    if settings.SECRET_KEY and settings.SECRET_KEY != "your-secret-key-change-this-in-production":
        print(f"✅ SECRET_KEY: {settings.SECRET_KEY[:20]}...")
        checks.append(True)
    else:
        print("❌ SECRET_KEY: 未配置或使用示例值")
        print("   请运行 python generate_keys.py 生成密钥")
        checks.append(False)
    
    if settings.JWT_SECRET_KEY and settings.JWT_SECRET_KEY != "your-jwt-secret-key-change-this":
        print(f"✅ JWT_SECRET_KEY: {settings.JWT_SECRET_KEY[:20]}...")
        checks.append(True)
    else:
        print("❌ JWT_SECRET_KEY: 未配置或使用示例值")
        checks.append(False)
    
    if settings.ENCRYPTION_KEY and settings.ENCRYPTION_KEY != "your-encryption-key-32-characters":
        print(f"✅ ENCRYPTION_KEY: {settings.ENCRYPTION_KEY[:20]}...")
        checks.append(True)
    else:
        print("❌ ENCRYPTION_KEY: 未配置或使用示例值")
        checks.append(False)
    
    print()
    print("-" * 60)
    print("可选配置项：")
    print("-" * 60)
    
    # 数据库
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    
    # Redis
    print(f"REDIS_URL: {settings.REDIS_URL}")
    
    # OCR
    print(f"OCR引擎: {settings.OCR_ENGINE}")
    print(f"OCR功能: {'启用' if settings.ENABLE_OCR else '禁用'}")
    
    # Bot模式
    print(f"Bot模式: {settings.BOT_MODE}")
    
    # 环境
    print(f"运行环境: {settings.APP_ENV}")
    print(f"调试模式: {settings.DEBUG}")
    
    print()
    print("=" * 60)
    
    if all(checks):
        print("🎉 配置检查通过！可以启动 Bot 了！")
        print()
        print("启动命令：")
        print("  python app/main.py")
        print("  或")
        print("  python run.py")
        print()
        return True
    else:
        print("⚠️  配置检查未通过，请修复上述问题后再试。")
        print()
        print("快速修复：")
        print("  1. 运行 python generate_keys.py 生成密钥")
        print("  2. 编辑 .env 文件，填入 Bot Token 和管理员 ID")
        print("  3. 重新运行 python check_config.py 检查")
        print()
        return False


if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)

