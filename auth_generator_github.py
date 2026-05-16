from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json
import sys

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
        auth_code = auth_code.strip()
        print(f"🔄 正在向 Google 换取 Token，验证码长度: {len(auth_code)}...")
        
        try:
            # 显式关闭或不提供 verifier，因为我们在第一步停用了 PKCE
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            
            print("\n" + "="*60)
            print("🎉 成功生成 Token！请复制下方全部内容存入 GitHub Secrets:")
            print("="*60 + "\n")
            print(creds.to_json())
            print("\n" + "="*60)
        except Exception as e:
            print(f"❌ 交换 Token 失败: {e}")
            
    # 如果没有验证码，执行【第一步】：生成并打印授权链接
    else:
        # 💡 【关键修改点】: 显式设置 code_challenge=None 来关闭 PKCE 验证
        # 这样可以防止 Google 在跨环境（GitHub Action 第二次运行）时索要 code_verifier
        auth_url, _ = flow.authorization_url(
            prompt='consent', 
            access_type='offline',
            code_challenge=None 
        )
        
        print("\n" + "="*60)
        print("👉 第一步：请在浏览器中打开以下链接进行授权：")
        print("-" * 60)
        print(auth_url)
        print("-" * 60)
        print("\n👉 第二步：授权后，Google 会给你一串验证码（Authorization Code）。")
        print("请再次触发 GitHub Actions，并将验证码粘贴进输入框中。")
        print("="*60 + "\n")
        sys.exit(1)

if __name__ == '__main__':
    main()