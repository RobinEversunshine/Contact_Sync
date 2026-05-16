import os, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from sync_contacts import main as push_to_gmails
from get_contact_info import main as get_contact


def get_service_from_env(env_var_name):
    """Retrieve Google People service using credentials from file or environment"""
    # Get token from GitHub Secrets/Environment Variables
    token_str = os.environ.get(env_var_name)
    if not token_str:
        raise ValueError(f"❌ cannot find env variable: {env_var_name}")
        
    token_data = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(token_data, ['https://www.googleapis.com/auth/contacts'])
    return build('people', 'v1', credentials=creds)



def main():
    # 1. 获取解析出来的联系人列表
    contact_list = get_contact()

    if not contact_list:
        print("💡 No contacts need to sync, process end")
        return

    # 2. 初始化两个 Gmail 账号的 API Service（在循环外只初始化一次，节约资源）
    try:
        service_a = get_service_from_env('GMAIL_TOKEN_A')
        service_b = get_service_from_env('GMAIL_TOKEN_B')
    except Exception as e:
        print(f"❌ 初始化 Google 服务的 Token 失败: {e}")
        return

    # 3. 循环遍历列表，逐个推送到 Gmail 
    success_count = 0
    for person_payload in contact_list:
        name = f"{person_payload.get('fname', '')} {person_payload.get('lname', '')}".strip() or "未命名"
        print(f"🔄 正在同步: {name}...")
        
        try:
            # 调用你写好的同步逻辑
            push_to_gmails(person_payload, service_a, service_b)
            print(f"✅ {name} 同步成功！")
            success_count += 1
        except Exception as e:
            # 单个联系人失败捕获，允许循环继续
            print(f"❌ {name} 同步失败，错误原因: {e}")

    print(f"\n📊 同步报告: 成功 {success_count}/{len(contact_list)}")


if __name__ == "__main__":
    main()