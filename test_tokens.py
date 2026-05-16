import os
import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/contacts']

def test_google_service(env_var_name):
    print(f"=========================================")
    print(f"🔍 正在测试检查环境变量: {env_var_name} ...")
    print(f"=========================================")
    
    token_json_str = os.environ.get(env_var_name)
    
    if not token_json_str:
        print(f"❌ 错误：未在环境中找到 {env_var_name} 的数据。请检查 GitHub Secrets 配置！")
        return False

    try:
        token_data = json.loads(token_json_str)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        service = build('people', 'v1', credentials=creds)
        
        # 发起一个极其轻量级的请求：获取联系人分组列表，最大返回1个
        # 只要这个请求没有抛出 401/403 异常，就说明 Token 是完全有效的
        response = service.contactGroups().list(pageSize=1).execute()
        
        print(f"✅ 【成功】{env_var_name} 有效！Google API 连接测试通过。")
        # 顺便检查一下是否包含 refresh_token 从而能自动续命
        if 'refresh_token' in token_data:
            print("💡 检查：包含 refresh_token，该凭证在云端可自动刷新续期。")
        else:
            print("⚠️ 警告：未找到 refresh_token，该 Token 可能会在 1 小时后过期，建议重新生成！")
        return True
        
    except json.JSONDecodeError:
        print(f"❌ 错误：{env_var_name} 的内容不是合法的 JSON 格式。")
        return False
    except Exception as e:
        print(f"❌ 错误：{env_var_name} 验证失败。Google 报错信息:\n   {e}")
        return False

def main():
    success_a = test_google_service('GMAIL_TOKEN_A')
    success_b = test_google_service('GMAIL_TOKEN_B')
    
    # 如果任意一个 Token 测试失败，让整个 Workflow 以错误状态退出，触发 GitHub 的红叉报警
    if not (success_a and success_b):
        print("\n🚨 结果：部分或全部 Token 验证失败，请排查上方错误。")
        sys.exit(1)
    else:
        print("\n🎉 结果：恭喜！两个账户的 Token 全部验证通过，均处于健康可用状态。")

if __name__ == '__main__':
    main()