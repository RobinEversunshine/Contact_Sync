from google_auth_oauthlib.flow import InstalledAppFlow
import json
import sys

SCOPES = ['https://www.googleapis.com/auth/contacts']

def main():
    # 确保你的仓库里有 credentials.json
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob' # 告诉 Google 我们是手动复制代码
    )

    # 1. 生成并打印授权链接
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print("\n" + "="*60)
    print("👉 第一步：请在浏览器中打开以下链接进行授权：")
    print("-" * 60)
    print(auth_url)
    print("-" * 60)
    
    # 在 GitHub Actions 中，我们需要一种方式让程序停下来等待我们输入
    # 但 GitHub Actions 不支持交互式输入，所以我们需要分两步走，
    # 或者利用 GitHub Actions 的 'input' 功能（见下文 YAML 配置）。
    print("\n👉 第二步：授权后，Google 会给你一串代码（Authorization Code）。")
    print("请将其作为参数重新运行，或在本地完成最后一步。")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()