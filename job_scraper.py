from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def get_job_descriptions(base_url, query, city, pages=10):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    jobs_data = []

    for page in range(1, pages + 1):
        url = f"{base_url}?query={query}&city={city}&page={page}"
        driver.get(url)
        
        if page < 2:
            time.sleep(35)  # 等待页面加载
        else:
            time.sleep(5)  # 等待页面加载

        job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-card-wrapper')
        for job in job_cards:
            job_data = {}
            job_data['job_title'] = job.find_element(By.CSS_SELECTOR, '.job-title .job-name').text
            job_data['area'] = job.find_element(By.CSS_SELECTOR, '.job-area-wrapper .job-area').text
            job_data['salary'] = job.find_element(By.CSS_SELECTOR, '.salary').text.strip() if job.find_elements(By.CSS_SELECTOR, '.salary') else "Not specified"
            
            job_data['experience'] = job.find_element(By.CSS_SELECTOR, '.job-info .tag-list li:nth-of-type(1)').text if job.find_elements(By.CSS_SELECTOR, '.job-info .tag-list li:nth-of-type(1)') else "Not specified"
            job_data['education'] = job.find_element(By.CSS_SELECTOR, '.job-info .tag-list li:nth-of-type(2)').text if job.find_elements(By.CSS_SELECTOR, '.job-info .tag-list li:nth-of-type(2)') else "Not specified"
            
            job_data['company_name'] = job.find_element(By.CSS_SELECTOR, '.company-name a').text.strip() if job.find_elements(By.CSS_SELECTOR, '.company-name a') else "Not specified"
          
            job_data['company_industry'] = job.find_element(By.CSS_SELECTOR, '.company-tag-list li:nth-of-type(1)').text.strip() if job.find_elements(By.CSS_SELECTOR, '.company-tag-list li:nth-of-type(1)') else "Not specified"
            job_data['funding_status'] = job.find_element(By.CSS_SELECTOR, '.company-tag-list li:nth-of-type(2)').text.strip() if job.find_elements(By.CSS_SELECTOR, '.company-tag-list li:nth-of-type(2)') else "Not specified"
            job_data['company_size'] = job.find_element(By.CSS_SELECTOR, '.company-tag-list li:nth-of-type(3)').text.strip() if job.find_elements(By.CSS_SELECTOR, '.company-tag-list li:nth-of-type(3)') else "Not specified"
            job_data['company_logo_url'] = job.find_element(By.CSS_SELECTOR, '.company-logo img').get_attribute('src') if job.find_elements(By.CSS_SELECTOR, '.company-logo img') else "Not specified"  
            
            job_data['tech_keywords'] = ','.join([li.text for li in job.find_elements(By.CSS_SELECTOR, '.job-card-footer .tag-list li')])
            job_data['benefits'] = job.find_element(By.CSS_SELECTOR, '.info-desc').text.strip() if job.find_elements(By.CSS_SELECTOR, '.info-desc') else "Not specified"

            hover = ActionChains(driver).move_to_element(job.find_element(By.CSS_SELECTOR, '.job-title'))
            hover.perform()
            time.sleep(2)  # 等待悬停效果出现

            try:
                description_element = job.find_element(By.CSS_SELECTOR, '.job-detail-body .desc')
                job_data['description'] = description_element.text
            except:
                job_data['description'] = "No description available"

         
            jobs_data.append(job_data)

        # 尝试点击下一页
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '.options-pages a:last-child')
            next_button.click()
            time.sleep(5)  # 等待页面加载
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            break

    driver.quit()
    return jobs_data

def save_to_json(data, filename='jobs_data.json'):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

base_url = 'https://www.zhipin.com/web/geek/job' 
query = '前端开发工程师'
city = '100010000'
jobs_data = get_job_descriptions(base_url, query, city) 
save_to_json(jobs_data)