"""
API 使用示例
演示如何通过HTTP API发送定向群组广播
"""
import requests
import json
import sys

# ==================== 配置区 ====================
API_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-secret-key"  # 请修改为你的实际API密钥
# ===============================================


def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def get_groups():
    """获取所有群组列表"""
    print_section("步骤 1: 获取群组列表")
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{API_URL}/groups", headers=headers)
        response.raise_for_status()
        
        groups = response.json()
        print(f"✅ 成功获取 {len(groups)} 个群组:\n")
        
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['group_name']}")
            print(f"     ID: {group['group_id']}")
            print(f"     商户号: {group['merchant_code']}")
            print(f"     状态: {'✅ 活跃' if group['is_active'] else '❌ 未激活'}")
            print()
        
        return groups
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ API密钥无效，请检查配置")
        else:
            print(f"❌ HTTP错误: {e}")
        return []
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def send_text_broadcast(group_ids, message):
    """发送文本广播"""
    print_section("步骤 2: 发送文本广播")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "group_ids": group_ids,
        "message": message
    }
    
    print(f"目标群组: {len(group_ids)} 个")
    print(f"消息内容:\n{'-'*40}\n{message}\n{'-'*40}\n")
    
    try:
        response = requests.post(
            f"{API_URL}/broadcast/groups",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        
        print(f"✅ {result['message']}")
        print(f"\n📊 发送统计:")
        print(f"  • 总计: {result['total']} 个群组")
        print(f"  • 成功: {result['success_count']} 个")
        print(f"  • 失败: {result['failed_count']} 个")
        
        if result['failed_groups']:
            print(f"\n❌ 失败详情:")
            for failed in result['failed_groups']:
                print(f"  • 群组 {failed['group_id']}: {failed['error'][:50]}")
        
        return result['success']
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误: {e}")
        if e.response:
            print(f"响应: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def send_photo_broadcast(group_ids, photo_url, caption):
    """发送图片广播"""
    print_section("步骤 2: 发送图片广播")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "group_ids": group_ids,
        "photo_url": photo_url,
        "caption": caption
    }
    
    print(f"目标群组: {len(group_ids)} 个")
    print(f"图片URL: {photo_url}")
    print(f"说明文字: {caption}\n")
    
    try:
        response = requests.post(
            f"{API_URL}/broadcast/groups",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        
        print(f"✅ {result['message']}")
        print(f"\n📊 发送统计:")
        print(f"  • 总计: {result['total']} 个群组")
        print(f"  • 成功: {result['success_count']} 个")
        print(f"  • 失败: {result['failed_count']} 个")
        
        return result['success']
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  Telegram Bot API 使用示例")
    print("="*60)
    print(f"API地址: {API_URL}")
    print(f"API密钥: {API_KEY[:10]}...")
    
    # 1. 获取群组列表
    groups = get_groups()
    
    if not groups:
        print("\n⚠️ 没有可用的群组，请先在Telegram中绑定群组")
        return
    
    # 2. 选择发送方式
    print_section("选择发送方式")
    print("1. 发送文本消息")
    print("2. 发送图片消息")
    print("3. 发送到所有群组")
    print("4. 退出")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == "4":
        print("👋 再见！")
        return
    
    # 3. 选择目标群组
    if choice in ["1", "2"]:
        print_section("选择目标群组")
        for i, group in enumerate(groups, 1):
            print(f"{i}. {group['group_name']} ({group['group_id']})")
        
        selection = input("\n请输入群组编号（多个用逗号分隔，或输入'all'选择全部）: ").strip()
        
        if selection.lower() == 'all':
            selected_groups = [g['group_id'] for g in groups]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_groups = [groups[i]['group_id'] for i in indices if 0 <= i < len(groups)]
            except:
                print("❌ 无效的输入")
                return
    elif choice == "3":
        selected_groups = [g['group_id'] for g in groups]
    else:
        print("❌ 无效的选择")
        return
    
    if not selected_groups:
        print("❌ 没有选择任何群组")
        return
    
    # 4. 发送消息
    if choice == "1":
        print_section("输入消息内容")
        message = input("请输入要发送的消息: ").strip()
        if message:
            send_text_broadcast(selected_groups, message)
        else:
            print("❌ 消息不能为空")
    
    elif choice == "2":
        print_section("输入图片信息")
        photo_url = input("请输入图片URL: ").strip()
        caption = input("请输入说明文字（可选）: ").strip()
        if photo_url:
            send_photo_broadcast(selected_groups, photo_url, caption)
        else:
            print("❌ 图片URL不能为空")
    
    elif choice == "3":
        message = "📢 这是一条发送到所有群组的测试消息"
        confirm = input(f"\n⚠️ 确认发送到所有 {len(selected_groups)} 个群组? (y/n): ")
        if confirm.lower() == 'y':
            send_text_broadcast(selected_groups, message)
        else:
            print("❌ 已取消")
    
    print_section("完成")
    print("✅ 操作完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 操作被中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 程序异常: {e}")
        sys.exit(1)
