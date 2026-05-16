from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json

SCOPES = ['https://www.googleapis.com/auth/contacts']

def main():
    # 1. 获取 Google Credentials JSON 字符串
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json_str:
        raise ValueError("❌ 错误：环境变量 GOOGLE_CREDENTIALS 为空")

    # 2. 将字符串解析为 Python 字典
    client_config = json.loads(creds_json_str)

    # 3. 初始化 Flow
    flow = InstalledAppFlow.from_client_config(
        client_config, 
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    # 4. 读取从 GitHub Actions 传进来的验证码环境变量
    auth_code = os.environ.get('INPUT_AUTH_CODE')

    # 如果有验证码，执行【第二步】：向 Google 换取 Token
    if auth_code:
        # 使用 .strip() 彻底清除可能存在的首尾空格和换行符
        auth_code = auth_code.strip()
        print(f"🔄 正在向 Google 换取 Token，验证码长度: {len(auth_code)}...")
        
        try:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            
            print("\n" + "="*60)
            print("🎉 成功生成 Token！请复制下方全部内容存入 GitHub Secrets:")
            print("="*60 + "\n")
            print(creds.to_json())
            print("\n" + "="*60)
        except Exception as e:
            print(f"❌ 交换 Token 失败: {e}")
            print("💡 提示：如果依然报错，请检查 Google Cloud 凭据类型是否为 Desktop App (桌面应用)。")
            
    # 如果没有验证码，执行【第一步】：生成并打印授权链接
    else:
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        
        print("\n" + "="*60)
        print("👉 第一步：请在浏览器中打开以下链接进行授权：")
        print("-" * 60)
        print(auth_url)
        print("-" * 60)
        print("\n👉 第二步：授权后，Google 会给你一串验证码（Authorization Code）。")
        print("请再次触发 GitHub Actions，并将验证码粘贴进输入框中。")
        print("="*60 + "\n")
        # 抛出异常中断当前流程，提醒用户需要进行第二步
        exit(1)

if __name__ == '__main__':
    main()