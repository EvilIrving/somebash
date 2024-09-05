import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import random
import json


# 设备型号池
device_pool = [
    "iPhone10,3",
    "iPhone10,6",
    "iPhone11,8",
    "iPhone12,1",
    "iPhone12,5",
    "Mi 10",
    "SM-G960F",
    "Pixel 3"
]

 # 添加 cookies
cookies = {
    "lastCity": "101190100",
    "__zp_seo_uuid__": "7c5c89be-33ec-430f-b07c-09933057ffc3",
    "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a": "1723879805,1724768681",
    "HMACCOUNT": "157D52602E554B39",
    "__g": "-",
    "Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a": "1725092041",
    "__c": "1724768682",
    "__l": "r=https%3A%2F%2Fwww.google.com%2F&l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjob-recommend&s=3&friend_source=0&s=3&friend_source=0",
    "__a": "78004063.1723879805.1723879805.1724768682.75.2.41.75",
    "__zp_stoken__": "de83fNDbDlcKzwrfCtUEwHB0DHxBOJUk2PRVNNDo1SkE0Nk9ITzQ2Nyo1JHDDj8OresOmYcOewolIJzZPS0g0QE9KSxc2M8K0SDM8wojDisOtZsOkVMODaigDw6bCsxlOwrUSw5bCtQV6w48lOsSJwrNOM01Jw7HDgcOrw4zCmcK0w5bDjsKFwrbDr8KzMzXDk8K1w7TDjj01Hx5oBzU3W0RqB1lXQ2BhXRxcXlI5Tk43NMOvb8OzMTYDEgcZBRwZEBIeBh8aGx8bGh8RHQYfGhgEPk%2FCq8K1wp3EpsSYxY3EgcSTwqjCocK5RcOLXsKXwpbDi1fCmFnDtsOMwpjCvcKnwqfCo21iwonCosK2wrxuUWVewoxmWcK3amR%2BW3RFRmLCjMOKYB8QwoxsazUfwoU4w4Q%3D; __c=1724768682"
}

def get_job_list(query, city, page, page_size=30):
    session = requests.Session()
    retries = Retry(total=2, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    print("开始爬取招聘信息")
    base_url = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json"
    params = {
        "scene": 1,
        "query": query,
        "city": city,
        "page": page,
        "pageSize": page_size
    }
    
     # 随机选择一个设备型号
    device = random.choice(device_pool)
    headers = {
        "User-Agent": f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(base_url, params=params,headers=headers,cookies=cookies,  timeout=10)
        response.raise_for_status()  # 将抛出HTTPError，如果状态不是200
        print(f"请求成功: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def get_job_details(security_id, lid, session_id):
    base_url = "https://www.zhipin.com/wapi/zpgeek/job/card.json"
    params = {
        "securityId": security_id,
        "lid": lid,
        "sessionId": session_id
    }
    headers = {
        "User-Agent": f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    try:
        response = requests.get(base_url, params=params,headers=headers,cookies=cookies, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def process_job_data(job, job_details):
    return {
        "jobName": job.get("jobName"),
        "salaryDesc": job.get("salaryDesc"),
        "skills": job.get("skills"),
        "jobExperience": job.get("jobExperience"),
        "jobDegree": job.get("jobDegree"),
        "cityName": job.get("cityName"),
        "areaDistrict": job.get("areaDistrict"),
        "businessDistrict": job.get("businessDistrict"),
        "city": job.get("city"),
        "brandName": job.get("brandName"),
        "brandLogo": job.get("brandLogo"),
        "brandStageName": job.get("brandStageName"),
        "brandIndustry": job.get("brandIndustry"),
        "brandScaleName": job.get("brandScaleName"),
        "welfareList": job.get("welfareList"),
        "postDescription": job_details.get("postDescription"),
        "jobLabels": job_details.get("jobLabels"),
        "address": job_details.get("address"),
        "brandName_detail": job_details.get("brandName")
    }

def save_to_json(data, filename='jobs.json'):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main():
    
    query = '前端开发工程师'
    # 南京 101190100 上海 101020100 深圳 101280100
    # 北京 101010100 广州 101280600 杭州 101210100
    city = '100010000'
    max_pages = 10
    jobs_data = []

    for page in range(1, max_pages + 1):
        job_list_response = get_job_list(query, city, page)
        if job_list_response and job_list_response.get('code') == 0:
            job_list = job_list_response.get('zpData', {}).get('jobList', [])
            print(f"第{page}页共{len(job_list)}条招聘信息")
            for job in job_list:
                job_details_response = get_job_details(job.get('securityId'), job.get('lid'), '')
                if job_details_response and job_details_response.get('code') == 0:
                    print(f"正在处理{job.get('jobName')}的详细信息")
                    job_details = job_details_response.get('zpData', {}).get('jobCard', {})
                    combined_job = process_job_data(job, job_details)
                    jobs_data.append(combined_job)
                else:
                    print(f"无法获取{job.get('jobName')}的详细信息")
                # 在处理每个职位详情后添加随机延时
                time.sleep(random.randint(3, 6))
        else:
            print(f"第{page}页没有获取到数据或服务端返回错误")
            break
        # 在每一页请求结束后添加随机延时
        time.sleep(random.randint(3, 6))

    save_to_json(jobs_data)

if __name__ == "__main__":
    main()