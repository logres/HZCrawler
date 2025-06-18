import os
import json
import numpy as np
from scipy.io import savemat
from datetime import datetime
from collections import defaultdict

def process_json_files(data_folder, output_folder="matData"):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(data_folder):
        if filename.endswith("_data.json"):
            file_path = os.path.join(data_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    records = json.load(f)
                except Exception as e:
                    print(f"读取失败 {filename}: {e}")
                    continue

            # 提取任务名和property字段
            try:
                file_stem = filename[:-5]  # 去掉 .json 后缀
                task_name = filename.split('[')[1].split(']')[0]
                property_name = filename.split(']_')[1].split('_data')[0]
            except IndexError:
                print(f"文件命名不规范: {filename}")
                continue

            data_by_month = defaultdict(list)

            for item in records:
                value = float(item.get("value", 0))
                timestamp = item.get("timestamp")
                if not timestamp:
                    continue
                dt = datetime.fromtimestamp(timestamp / 1000)
                year_month = dt.strftime("%Y_%m")
                time_str = dt.strftime("%Y-%m-%d %H:%M")

                key = f"{task_name}_{property_name}_{year_month}"
                data_by_month[key].append((value, time_str))

            sub_output_folder = os.path.join(output_folder, file_stem)
            os.makedirs(sub_output_folder, exist_ok=True)

            for key, values in data_by_month.items():
                values_array = np.array([v for v, _ in values], dtype=np.float64).reshape(-1, 1)
                
                times_array = [t for _, t in values]

                mat_data = {
                    key: values_array,
                    f"{key}_time": times_array
                }

                out_file = os.path.join(sub_output_folder, f"{key}.mat")
                savemat(out_file, mat_data, do_compression=False)
                print(f"✅ 生成: {out_file}")

# 运行
process_json_files("data")
