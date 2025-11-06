#!/usr/bin/env python3
"""
环境变量密钥生成器
用于生成 .env 文件所需的随机密钥
"""
import secrets


def generate_keys():
    """生成所有需要的密钥"""
    print("=" * 60)
    print("Telegram 商户管理机器人 - 配置密钥生成器")
    print("=" * 60)
    print()
    
    print("请将以下内容复制到您的 .env 文件中：")
    print()
    print("-" * 60)
    
    # 生成 SECRET_KEY
    secret_key = secrets.token_urlsafe(32)
    print(f"SECRET_KEY={secret_key}")
    
    # 生成 JWT_SECRET_KEY
    jwt_secret = secrets.token_urlsafe(32)
    print(f"JWT_SECRET_KEY={jwt_secret}")
    
    # 生成 ENCRYPTION_KEY (32字符)
    encryption_key = secrets.token_urlsafe(24)  # 生成约32个字符
    print(f"ENCRYPTION_KEY={encryption_key}")
    
    print("-" * 60)
    print()
    
    print("[提示]")
    print("1. 这些密钥只生成一次，请妥善保管")
    print("2. 不要将密钥提交到代码仓库")
    print("3. 生产环境部署后不要随意更改密钥")
    print("4. 如需重新生成，再次运行此脚本即可")
    print()
    
    print("=" * 60)


if __name__ == "__main__":
    generate_keys()

