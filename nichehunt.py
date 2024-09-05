import requests
from datetime import datetime

# 设置 Product Hunt API 访问凭证
api_key = 'OStIM3bBspwt6eX1ypLWxY7uVaG8AAu_7S-Z_BTROaQ'

# 设置请求头
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# 获取当日的日期
today = datetime.now().strftime('%Y-%m-%d')

# API 请求 URL
url = f'https://api.producthunt.com/v2/api/graphql'

# GraphQL 查询，获取今日榜单数据
query = """
{
  posts(order: RANKING) {
    edges {
      node {
        name
        tagline
        votesCount
        website
      }
    }
  }
}
"""

# 发起请求
response = requests.post(url, json={'query': query}, headers=headers)

# 检查响应状态码
if response.status_code == 200:
    data = response.json()['data']['posts']['edges']
    print("Today's Top Products on Product Hunt:")
    for product in data:
        name = product['node']['name']
        tagline = product['node']['tagline']
        votes = product['node']['votesCount']
        website = product['node']['website']
        print(f'{name} - {tagline} ({votes} votes)\n{website}\n')
else:
    print(f'Failed to fetch data: {response.status_code} - {response.text}')
