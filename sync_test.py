import os
import json
import sys

def main():
    # GitHub Actions 会把触发时传来的数据存放在这个环境变量中
    event_path = os.getenv('GITHUB_EVENT_PATH')
    
    with open(event_path, 'r') as f:
        event_data = json.load(f)
    
    # 提取快捷指令发来的 client_payload
    payload = event_data.get('client_payload', {})
    
    first_name = payload.get('fname', 'Unknown')
    last_name = payload.get('lname', 'Unknown')
    phone = payload.get('phone', 'N/A')

    print("--- 收到数据同步请求 ---")
    print(f"姓名: {first_name} {last_name}")
    print(f"电话: {phone}")
    print("-----------------------")

    # 这里以后可以添加 Google People API 代码
    if first_name != 'Unknown':
        print("模拟同步成功！")
    else:
        print("未接收到有效数据。")

if __name__ == "__main__":
    main()
