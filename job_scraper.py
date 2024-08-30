import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_job_details(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        company = soup.find('div', class_='boss-info-attr').text.strip()
        company_info = soup.find('div', class_='sider-company').find_all('p')
        size = company_info[1].text.strip()
        industry = company_info[2].text.strip()
        
        job_primary = soup.find('div', class_='job-primary')
        salary = job_primary.find('span', class_='salary').text.strip()
        job_info = job_primary.find('div', class_='info-primary').find_all('p')
        city = job_primary.find('a',class_='text-city').text.strip()
        experience = job_primary.find('span',class_='text-experiece').text.strip()
        education = job_primary.find('span',class_='text-degree').text.strip()
        
        description = soup.find('div', class_='job-sec-text').text.strip()

        print(f"Scraped {company} - {city} - {salary}")
        
        return {
            'company': company,
            'size': size,
            'industry': industry,
            'salary': salary,
            'experience': experience,
            'education': education,
            'city': city,
            'description': description
        }
    except AttributeError as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def scrape_jobs(keyword):
    base_url = 'https://www.zhipin.com/web/geek/job'
    jobs = []
    page = 1
    
    while True:
        params = {
            'query': keyword,
            'city':100010000,
            'page': page
        }
        response = requests.get(base_url, params=params, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_list = soup.find_all('div', class_='job-card-wrapper')
        
        if not job_list:
            break
        
        job_urls = ['https://www.zhipin.com' + job.find('a')['href'] for job in job_list]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            job_details = list(executor.map(get_job_details, job_urls))
        
        jobs.extend([job for job in job_details if job])
        page += 1
        
        time.sleep(random.uniform(1, 3))  # 随机延迟1-3秒
    
    return jobs

def main():
    keyword = "前端开发工程师"
    jobs = scrape_jobs(keyword)
    
    # 输出为JSON
    with open('frontend_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    # 输出为Excel
    # df = pd.DataFrame(jobs)
    # df.to_excel('frontend_jobs.xlsx', index=False)

if __name__ == "__main__":
    main()
