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

    fields = ['fname', 'lname', 'phone', 'email', 'address', 'note', 'bday', 'url', 'social']
    
    print("--- sync contact request ---")
    for field in fields:
        value = payload.get(field, 'N/A')
        print(f"{field.capitalize()}: {value}")
    print("-----------------------")

    # 这里以后可以添加 Google People API 代码
    if first_name != 'Unknown':
        print("sync success")
    else:
        print("sync failed")

if __name__ == "__main__":
    main()
