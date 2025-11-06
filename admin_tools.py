#!/usr/bin/env python
"""
管理员工具 - 生成商户验证码
"""
import sys
import secrets
import string
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))


def generate_merchant_code(length=8):
    """生成随机商户验证码"""
    # 使用字母和数字
    chars = string.ascii_uppercase + string.digits
    # 去除容易混淆的字符
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    
    code = ''.join(secrets.choice(chars) for _ in range(length))
    return code


def generate_batch_codes(count=10):
    """批量生成验证码"""
    codes = []
    for _ in range(count):
        code = generate_merchant_code()
        codes.append({
            'code': code,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'used': False
        })
    return codes


if __name__ == "__main__":
    print("=" * 60)
    print("  商户验证码生成器")
    print("=" * 60)
    print()
    
    try:
        count = int(input("需要生成多少个验证码？(默认 10): ") or "10")
    except ValueError:
        count = 10
    
    print()
    print(f"正在生成 {count} 个验证码...")
    print()
    
    codes = generate_batch_codes(count)
    
    print("-" * 60)
    print(f"{'序号':<6} {'验证码':<12} {'有效期至'}")
    print("-" * 60)
    
    for idx, code_info in enumerate(codes, 1):
        expires = datetime.fromisoformat(code_info['expires_at'])
        print(f"{idx:<6} {code_info['code']:<12} {expires.strftime('%Y-%m-%d')}")
    
    print("-" * 60)
    print()
    
    # 保存到文件
    save = input("是否保存到文件？(y/n): ").lower()
    if save == 'y':
        filename = f"merchant_codes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("商户验证码列表\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for idx, code_info in enumerate(codes, 1):
                f.write(f"{idx}. {code_info['code']}\n")
        
        print(f"✅ 已保存到文件：{filename}")
    
    print()
    print("提示：将这些验证码分配给商户，用于注册。")
    print()


