from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from concurrent.futures import ThreadPoolExecutor
import random

def get_job_details(driver, url):
    try:
        driver.get(url)
        time.sleep(2)  # 等待页面加载和JavaScript渲染
            
        # 使用显式等待确保元素加载
        wait = WebDriverWait(driver, 10)
        company_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'boss-info-attr')))
        company = company_element.text.strip()

        company_info = driver.find_elements(By.CLASS_NAME, 'sider-company').find_elements(By.TAG_NAME, 'p')
        size = company_info[1].text.strip()
        industry = company_info[2].text.strip()
        
        job_primary = driver.find_element(By.CLASS_NAME, 'job-primary')
        salary = job_primary.find_element(By.CLASS_NAME, 'salary').text.strip()
        job_info = job_primary.find_element(By.CLASS_NAME, 'info-primary').find_elements(By.TAG_NAME, 'p')
        city = job_primary.find_element(By.CLASS_NAME, 'text-city').text.strip()
        experience = job_primary.find_element(By.CLASS_NAME, 'text-experience').text.strip()
        education = job_primary.find_element(By.CLASS_NAME, 'text-degree').text.strip()
        
        description = driver.find_element(By.CLASS_NAME, 'job-sec-text').text.strip()

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
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def scrape_jobs(keyword):
    base_url = 'https://www.zhipin.com/web/geek/job'
    jobs = []
    page = 1
    
    options = Options()
    # options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    
    while True:
        if page == 2:
            break  # 当 page 等于 2 时退出循环

        params = {
            'query': keyword,
            'city': 100010000,  # 确保这是正确的城市代码
            'page': page
        }
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        print(f"{query_string} - {page}")
        driver.get(f"{base_url}?{query_string}")
        time.sleep(2)  # 等待页面加载和JavaScript渲染
        
        job_cards = driver.find_elements(By.CLASS_NAME, 'job-card-wrapper')
        
        print(f"Scraping {len(job_cards)} jobs...")
        if not job_cards:
            break
        
        job_urls = [job.find_element(By.TAG_NAME, 'a').get_attribute('href') for job in job_cards]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            job_details = list(executor.map(lambda url: get_job_details(driver, url), job_urls))
        
        jobs.extend([job for job in job_details if job])
        page += 1
        
        time.sleep(random.uniform(1, 4))  # 随机延迟1-4秒
    
    driver.quit()
    return jobs

def main():
    keyword = "前端开发工程师"
    jobs = scrape_jobs(keyword)
    
    # 输出为JSON
    with open('frontend_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()