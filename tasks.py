from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
import os

@dataclass
class Task:
    task_id: str
    device_id: str
    property_name: str
    mode: str  # 'full' or 'incremental'
    status: Optional[str]  # pending, running, done, etc.
    last_run: Optional[datetime] = None
    result_file: Optional[str] = None
    last_record_time_stamp: Optional[int] = None
    record_num: Optional[int] = None

    def __post_init__(self):
        if not self.result_file:
            filename = f"""{self.device_id}[{self.task_id}]_{self.property_name}_data.json"""
            default_dir = "./data"
            os.makedirs(default_dir, exist_ok=True)
            self.result_file = os.path.join(default_dir, filename)
        if not self.status:
            self.status = "pending"

    @staticmethod
    def from_dict(data: dict) -> "Task":
        last_run = data.get("last_run")
        if last_run:
            last_run = datetime.fromisoformat(last_run)
        return Task(
            task_id=data["task_id"],
            device_id=data["device_id"],
            property_name=data["property_name"],
            mode=data["mode"],
            status=data.get("status"),
            last_run=last_run,
            result_file=data.get("result_file"),
            last_record_time_stamp=data.get("last_record_time_stamp"),
            record_num=data.get("record_num"),
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        if self.last_run:
            data["last_run"] = self.last_run.isoformat()
        else:
            data["last_run"] = None
        return data

import json
from typing import List

def load_tasks_from_json(filepath: str) -> List[Task]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Task.from_dict(item) for item in data]

def save_tasks_to_json(tasks: List[Task], filepath: str):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([task.to_dict() for task in tasks], f, indent=2, ensure_ascii=False)
