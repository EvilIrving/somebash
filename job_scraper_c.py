import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# 获取职位详情的函数
def get_job_details(job_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0',
    }
    response = requests.get(job_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # 提取公司名称
    company_name = soup.select_one('.job-detail-company_custompage').text.strip()
    # 提取公司人数范围
    # company_size = soup.select_one('.info-primary p').text.split(" ")[1].strip()
    # 提取领域
    # industry_field = soup.select_one('.icon-industry p').text.split(" ")[0].strip()
    # 提取薪资范围
    salary_range = soup.select_one('.info-primary .salary').text.strip()
    # 提取年限要求
    experience_required = soup.select_one('.text-experiece').text.split(" ")[2].strip()
    # 提取城市
    city = soup.select_one('.text-city').text.strip()
    # 提取学历要求
    education_required = soup.select_one('.text-degree').text.split("/")[1].strip()
    # 提取岗位描述
    job_description = soup.select_one('.job-sec-text').text.strip()

    return {
        "company_name": company_name,
        # "company_size": company_size,
        # "industry_field": industry_field,
        "salary_range": salary_range,
        "experience_required": experience_required,
        "city": city,
        "education_required": education_required,
        "job_description": job_description
    }

# 主函数
def main():
    job_url = "https://www.zhipin.com/job_detail/134f79f3cdbfc73c1Hx42Nm-FFNQ.html?lid=4Gx0I7MHAg7.search.1&securityId=rQZSTc8FYeD1J-b1mCi4Ny457r4RgvzyPBPaC8sS-SE1biDSmE2zXLsNKcHLW65fnujSgSAUkTUsMSCQOXljXc1FRqZ8zG2K40rnRmZzL5gJwA-SCLd46GZowZit5ft28uBCxczQLbcGIw~~&sessionId="
    job_details = get_job_details(job_url)

    # 导出为 JSON 文件
    with open('job_details.json', 'w', encoding='utf-8') as json_file:
        json.dump(job_details, json_file, ensure_ascii=False, indent=4)

    # 使用 pandas 导出为 Excel 文件
    df = pd.DataFrame([job_details])
    df.to_excel('job_details.xlsx', index=False)

if __name__ == '__main__':
    main()
