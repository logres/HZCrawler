import requests, json, copy
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from config import settings
from tasks import Task
from urllib.parse import unquote
from rich.console import Console

console = Console()

# 常量：一天的毫秒数 * 4
DAYSUB = 86400000 * 4

def fetch_device_data(task_src: Task) -> Task:
    token = settings.x_access_token
    base_url = settings.base_url

    task = copy.deepcopy(task_src)

    device_id = task.device_id
    property_name = task.property_name
    mode = task.mode
    last_record_time_stamp = task.last_record_time_stamp
    result_file = task.result_file
    record_num = task.record_num

    if mode == "incremental":
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        data_integration = len(existing_data) == record_num
        console.print(f"[bold green]Existing data count:[/] {len(existing_data)}, [bold cyan]Record number:[/] {record_num}")
        
        if data_integration:
            console.print(f"[bold yellow]Data in {result_file} is already integrated, skipping fetch.[/]")
            is_fetch_from_start = False
        else:
            console.print(f"[bold red]Data in {result_file} is not integrated, fetching from start.[/]")
            existing_data = []
            is_fetch_from_start = True
    else:
        console.print(f"[bold blue]Full mode, fetching from start.[/]")
        existing_data = []
        is_fetch_from_start = True

    def parse_timestamp(item):
        return datetime.fromtimestamp(item.get("timestamp") / 1000)
    

    # 确定起始时间戳
    to_ts = int(datetime.now().timestamp() * 1000)
    from_ts = to_ts - DAYSUB  # 向前推进4天
    limit = 0 if is_fetch_from_start else last_record_time_stamp


    data = []
    while to_ts > limit:
        print(f"Fetching data from {datetime.fromtimestamp(from_ts / 1000)} to {datetime.fromtimestamp(to_ts / 1000)}")
        chunk = fetch_data_from_ts(base_url, device_id, property_name, token, from_ts, to_ts)
        chunk = [item for item in chunk if parse_timestamp(item) > datetime.fromtimestamp(limit / 1000)]
        if not chunk:
            break
        # need to filter out the data that is older than limit
        data.extend(chunk)
        to_ts = from_ts
        from_ts = max(0, from_ts - DAYSUB)

    combined = data + existing_data
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print(f"Fetched {len(data)} records saved to {result_file}")
    
    task.last_run = datetime.now()
    if data:
        latest_ts = parse_timestamp(combined[0])
        task.last_record_time_stamp = int(latest_ts.timestamp() * 1000)
        task.record_num = len(combined)
    task.status = "done" if mode == "full" else "pending"

    return task

def fetch_data_from_ts(base_url: str, device_id: str, property_name: str, token: str, from_ts: int, to_ts: int, page_size: int = 1000) -> List[dict]:
    """
    按时间窗口拉取数据，直到没有数据或查询失败。
    """
    page_index = 0
    filtered_data = []

    headers = {
        "X-Access-Token": token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    while True:
        url = f"{base_url}/device-instance/{device_id}/properties/_query"
        params = {
            "pageSize": page_size,
            "pageIndex": page_index,
            "terms[0].column": "property",
            "terms[0].value": property_name,
            "terms[1].column": "timestamp$BTW",
            "terms[1].value[]": [from_ts, to_ts],
            "sorts[0].name": "timestamp",
            "sorts[0].order": "desc"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Failed: {response.status_code} {response.text}")
                break
            data = response.json().get("result", {"data": []}).get("data", [])
            if not data:
                break

            # 过滤并添加数据
            new_records = [record for record in data if "timestamp" in record]
            filtered_data.extend(new_records)

            page_index += 1

            if len(new_records) < page_size:
                break

        except Exception as e:
            print(f"Error during fetching data: {e}")
            break

    return filtered_data
