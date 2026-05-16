import os, json


def main():
    # GitHub Actions 会把触发时传来的数据存放在这个环境变量中
    event_path = os.getenv('GITHUB_EVENT_PATH')
    
    if not event_path or not os.path.exists(event_path):
        print("⚠️ 未找到 GITHUB_EVENT_PATH，返回空列表。")
        return []
        
    with open(event_path, 'r') as f:
        event_data = json.load(f)
    
    # 1. 提取快捷指令发来的 client_payload
    payload = event_data.get('client_payload', {})
    
    # 2. 从 payload 中获取我们在快捷指令里打包的 'contacts' 列表
    # 如果快捷指令发来的不是批量格式，则默认兼容单人格式包装成列表 [payload]
    contact_list = payload.get('contacts')
    print(contact_list)
    
    if not isinstance(contact_list, list):
        if payload: # 兼容老版本的单人传输格式
            contact_list = [payload]
        else:
            contact_list = []

    fields = ['fname', 'lname', 'phone', 'email', 'address', 'note', 'bday', 'url', 'social']

    print(f"📦 --- 收到批量同步请求，共 {len(contact_list)} 个联系人 ---")
    
    # 3. 循环打印检查每个人的数据
    for index, person in enumerate(contact_list, 1):
        print(f"\n👤 联系人 #{index}:")
        for field in fields:
            value = person.get(field, 'N/A')
            print(f"  {field.capitalize()}: {value}")
            
    print("\n--------------------------------------")
    
    return contact_list # 👈 核心修改：现在返回的是一个列表 [{}, {}, ...]


if __name__ == "__main__":
    main()