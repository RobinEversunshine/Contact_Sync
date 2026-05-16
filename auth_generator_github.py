from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json
import sys

SCOPES = ['https://www.googleapis.com/auth/contacts']

def main():
    # 1. 获取 JSON 字符串
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS')
    
    if not creds_json_str:
        raise ValueError("环境变量 GOOGLE_CREDENTIALS 为空")

    # 2. 将字符串解析为 Python 字典
    client_config = json.loads(creds_json_str)

    # 3. 初始化 Flow
    flow = InstalledAppFlow.from_client_config(
        client_config, 
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    # 4. 判断是否通过命令行传入了 Authorization Code
    # 检查运行命令时有没有带参数，例如: python auth.py 4/0AfgeX...
    if len(sys.argv) > 1:
        auth_code = sys.argv[1]
        print("\n🔄 正在向 Google 换取 Token，请稍候...")
        try:
            # 关键的后半段：用代码交换凭证
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            
            print("\n" + "="*60)
            print("🎉 成功生成 Token！请复制下方全部内容存入 GitHub Secrets:")
            print("="*60 + "\n")
            print(creds.to_json())
            print("\n" + "="*60)
        except Exception as e:
            print(f"❌ 交换 Token 失败，可能是代码过期或不正确: {e}")
            
    else:
        # 5. 如果没有传参数，则执行第一步：打印授权链接
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        
        print("\n" + "="*60)
        print("👉 第一步：请在浏览器中打开以下链接进行授权：")
        print("-" * 60)
        print(auth_url)
        print("-" * 60)
        print("\n👉 第二步：授权后，Google 会给你一串验证码（Authorization Code）。")
        print("请再次触发 GitHub Actions，并将验证码粘贴进输入框中。")
        print("="*60 + "\n")

if __name__ == '__main__':
    main()