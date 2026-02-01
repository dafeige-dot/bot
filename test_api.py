"""
API 测试脚本
"""
import requests
import json
from typing import List, Dict

# 配置
API_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-secret-key"  # 请修改为你的API密钥

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def test_health():
    """测试健康检查接口"""
    print("\n" + "="*50)
    print("测试 1: 健康检查")
    print("="*50)
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_get_groups():
    """测试获取群组列表"""
    print("\n" + "="*50)
    print("测试 2: 获取群组列表")
    print("="*50)
    
    try:
        response = requests.get(f"{API_URL}/groups", headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ 成功获取 {len(groups)} 个群组:")
            for group in groups:
                print(f"  - {group['group_name']} (ID: {group['group_id']})")
            return groups
        else:
            print(f"❌ 失败: {response.text}")
            return []
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def test_broadcast_text(group_ids: List[int]):
    """测试发送文本广播"""
    print("\n" + "="*50)
    print("测试 3: 发送文本广播（包含换行）")
    print("="*50)
    
    if not group_ids:
        print("⚠️ 跳过: 没有可用的群组")
        return False
    
    # 构建多行消息
    message = """🧪 API测试消息

这是一条测试广播消息

测试内容：
  • 换行支持
  • 多行文本
  • Emoji显示

测试时间：2025-02-01

━━━━━━━━━━━━━━━━━━"""
    
    data = {
        "group_ids": group_ids[:1],  # 只发送到第一个群组
        "message": message
    }
    
    print(f"目标群组: {group_ids[:1]}")
    print(f"消息内容:\n{'-'*40}\n{message}\n{'-'*40}")
    
    try:
        response = requests.post(
            f"{API_URL}/broadcast/groups",
            headers=headers,
            json=data
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            print(f"✅ 广播成功: {result['success_count']}/{result['total']}")
        else:
            print(f"❌ 广播失败")
        
        return result.get('success', False)
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_broadcast_with_invalid_key():
    """测试无效API密钥"""
    print("\n" + "="*50)
    print("测试 4: 无效API密钥（应该失败）")
    print("="*50)
    
    invalid_headers = {
        "X-API-Key": "invalid-key",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_URL}/groups", headers=invalid_headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ 正确拒绝了无效密钥")
            return True
        else:
            print(f"❌ 应该返回401，实际返回: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_broadcast_invalid_params():
    """测试无效参数"""
    print("\n" + "="*50)
    print("测试 5: 无效参数（应该失败）")
    print("="*50)
    
    # 缺少必填参数
    data = {
        "group_ids": []  # 空列表
    }
    
    try:
        response = requests.post(
            f"{API_URL}/broadcast/groups",
            headers=headers,
            json=data
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ 正确拒绝了无效参数")
            print(f"错误信息: {response.json()}")
            return True
        else:
            print(f"❌ 应该返回400，实际返回: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Telegram Bot API 测试套件")
    print("="*60)
    print(f"API地址: {API_URL}")
    print(f"API密钥: {API_KEY[:10]}...")
    
    results = []
    
    # 测试1: 健康检查
    results.append(("健康检查", test_health()))
    
    # 测试2: 获取群组列表
    groups = test_get_groups()
    results.append(("获取群组列表", len(groups) >= 0))
    
    # 测试3: 发送文本广播（如果有群组）
    if groups:
        group_ids = [g['group_id'] for g in groups]
        confirm = input("\n⚠️ 是否发送测试消息到第一个群组? (y/n): ")
        if confirm.lower() == 'y':
            results.append(("发送文本广播", test_broadcast_text(group_ids)))
        else:
            print("⏭️ 跳过发送测试")
    
    # 测试4: 无效API密钥
    results.append(("无效API密钥", test_broadcast_with_invalid_key()))
    
    # 测试5: 无效参数
    results.append(("无效参数", test_broadcast_invalid_params()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-"*60)
    print(f"总计: {passed + failed} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被中断")
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
