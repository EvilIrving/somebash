import os
import json

# 确保目录存在
output_dir = "."
jobs_data = [1, 2, 3, 4, 5]  # 修正缩进

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file_path = os.path.join(output_dir, 'jobs_data.json')
with open(output_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(jobs_data, json_file, ensure_ascii=False, indent=4)