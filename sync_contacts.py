import datetime
import json
import os
import pycountry
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/contacts']


raw_payload = {
    'address': 'TestStreet1\nTestStreet2\nPOSTCODE TestCity\nAustria',
    'bday': 'Aug 14, 2006 at 00:00',
    'email': 'test@gmail.com\ntest2@gmail.com',
    'fname': 'Robin',
    'lname': 'Cai',
    'note': 'Test notes',
    'phone': '1001001000\n(200) 200-2000',
    'social': '',
    'url': 'http://test/url\nhttp://test2/url'
}




def parse_multiline_field(field_value):
    """split \n to lists, removing spaces and empty values"""
    if not field_value: return []
    return [item.strip() for item in field_value.split('\n') if item.strip()]




def get_country_code(country_name):
    """根据国家名称获取 ISO 3166-1 alpha-2 代码"""
    if not country_name:
        return ""
    try:
        # 模糊搜索国家
        # 例如 "Austria" 会返回对应的国家对象，其 alpha_2 属性为 "AT"
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2
    except (LookupError, AttributeError):
        # 如果找不到匹配项，打印提示并返回空
        print(f"⚠️ 无法找到国家代码: {country_name}")
        return ""


def parse_address(address_str):
    """精细化解析地址，支持多行街道和国家识别"""
    lines = [item.strip() for item in address_str.split('\n') if item.strip()]
    if not lines:
        return {}
    
    addr_obj = {
        "streetAddress": "",
        "extendedAddress": "",
        "city": "",
        "postalCode": "",
        "country": "",
        "countryCode": ""
    }
    
    # 1. 识别国家 (最后一行)
    if len(lines) >= 1:
        country_name = lines[-1]
        addr_obj["country"] = country_name
        addr_obj["countryCode"] = get_country_code(country_name)
    
    # 2. 识别邮编和城市 (倒数第二行)
    # 格式通常为 "POSTCODE City"
    if len(lines) >= 2:
        city_line = lines[-2]
        parts = city_line.split(' ', 1)
        if len(parts) == 2:
            addr_obj["postalCode"] = parts[0]
            addr_obj["city"] = parts[1]
        else:
            addr_obj["city"] = city_line
            
    # 3. 街道与扩展地址分配逻辑

    street_parts = lines[:-2] if len(lines) >= 2 else lines[:-1] if len(lines) == 1 else []
    if len(street_parts) == 1:
        # 只有一行：写进 streetAddress
        addr_obj["streetAddress"] = street_parts[0]
    elif len(street_parts) >= 2:
        # 第一行写进 streetAddress
        addr_obj["streetAddress"] = street_parts[0]
        # 第二行及其余所有行合并进 extendedAddress
        addr_obj["extendedAddress"] = "\n".join(street_parts[1:])
        
    return addr_obj



def find_existing_contact_by_name(service, fname, lname):
    """根据姓名搜索联系人"""
    # 组合姓名进行搜索，例如 "Test Fname Test Lname"
    full_name = f"{fname} {lname}".strip()
    
    resource_name = None
    etag = None
    
    if full_name:
        try:
            results = service.people().searchContacts(
                query=full_name,
                # 必须包含 names 才能在结果中获取 etag 和进一步信息
                readMask="names,phoneNumbers" 
            ).execute()
            
            # searchContacts 返回的是一个包装在 'results' 里的列表
            search_results = results.get('results', [])
            
            if search_results:
                # 获取匹配度最高的第一个人
                person = search_results[0].get('person')
                resource_name = person.get('resourceName')
                etag = person.get('etag')
                print(f"🔍 找到现有联系人: {full_name} ({resource_name})")
        except Exception as e:
            print(f"搜索姓名时出错: {e}")
            
    return resource_name, etag




def upsert_contact(service, data):
    # --- 1. 解析基础多值字段 ---
    phones = parse_multiline_field(data.get('phone', ''))
    emails = [{"value": e} for e in parse_multiline_field(data.get('email', ''))]
    urls = [{"value": u} for u in parse_multiline_field(data.get('url', ''))]
    
    # --- 2. 解析地址 ---
    parsed_addr = parse_address(data.get('address', ''))
    
    # --- 3. 处理生日和年份为 1 的逻辑 ---
    birthday_obj = None
    bday_str = data.get('bday', '')
    if bday_str and " at " in bday_str:
        try:
            # 提取日期部分: "May 12, 2001" 或 "May 12, 1"
            date_part = bday_str.split(' at ')[0]
            
            # 手动处理年份为 1 的情况以防 strptime 报错
            month_day, year_str = date_part.rsplit(', ', 1)
            year_val = int(year_str)
            
            # 解析月和日
            dt = datetime.datetime.strptime(month_day, "%b %d")
            
            date_data = {"month": dt.month, "day": dt.day}
            # 如果年份不为 1，则添加年份
            if year_val > 1:
                date_data["year"] = year_val
            
            birthday_obj = [{"date": date_data}]
        except Exception as e:
            print(f"生日解析失败: {e}")

    # --- 4. 构建 Body ---
    body = {
        "names": [{"givenName": data.get('fname', ''), "familyName": data.get('lname', '')}],
        "phoneNumbers": [{"value": p} for p in phones],
        "emailAddresses": emails,
        "urls": urls,
        "biographies": [{"value": data.get('note', '')}],
        "addresses": [parsed_addr]
    }
    if birthday_obj:
        body["birthdays"] = birthday_obj


    # find existing contact by name
    fname = data.get('fname', '')
    lname = data.get('lname', '')
    resource_name, etag = find_existing_contact_by_name(service, fname, lname)

    update_fields = "names,emailAddresses,phoneNumbers,urls,biographies,addresses,birthdays"


    try:
        if resource_name:
            body['etag'] = etag
            contact = service.people().updateContact(
                resourceName=resource_name,
                updatePersonFields=update_fields,
                body=body
            ).execute()
            print(f"🔄 successfully updated contacts: {contact.get('resourceName')}")
        else:
            contact = service.people().createContact(body=body).execute()
            print(f"✅ successfully created contacts: {contact.get('resourceName')}")
    except Exception as e:
        print(f"❌ something went wrong: {e}")



def get_service_from_env(env_var_name):
    # get token from GitHub Secrets
    # token_data = json.loads(os.environ.get(env_var_name))
    # creds = Credentials.from_authorized_user_info(token_data)
    creds = Credentials.from_authorized_user_file(f'{env_var_name}.json', SCOPES)
    return build('people', 'v1', credentials=creds)



def main(payload):
    # start service
    # service_a = get_service_from_env('GMAIL_TOKEN_A')
    # service_b = get_service_from_env('GMAIL_TOKEN_B')
    service_a = get_service_from_env('token_a')
    service_b = get_service_from_env('token_b')
    
    # create or update contact
    upsert_contact(service_a, payload)
    upsert_contact(service_b, payload)


if __name__ == '__main__':
    main(raw_payload)
