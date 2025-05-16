from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE
from rich.panel import Panel
from rich.progress import track
from tasks import load_tasks_from_json, Task, save_tasks_to_json
from config import settings
from fetcher import fetch_device_data
from typing import List, Tuple
import os

console = Console()

def show_task_details(task):
    task_table = Table(title=f"Task INFO: {safe_value(task.task_id)}", show_header=False, box=SIMPLE)
    task_table.add_row("[bold blue]Task ID[/]", safe_value(task.task_id))
    task_table.add_row("[bold blue]Device ID[/]", safe_value(task.device_id))
    task_table.add_row("[bold blue]Property Name[/]", safe_value(task.property_name))
    task_table.add_row("[bold blue]Mode[/]", safe_value(task.mode))
    task_table.add_row("[bold blue]Status[/]", safe_value(task.status))
    task_table.add_row("[bold blue]Last Run[/]", safe_value(task.last_run))
    task_table.add_row("[bold blue]Result File[/]", safe_value(task.result_file))
    task_table.add_row("[bold blue]Last Record Timestamp[/]", safe_value(task.last_record_time_stamp))
    task_table.add_row("[bold blue]Record Number[/]", safe_value(task.record_num))

    console.print(Panel(task_table, title="Task Details", expand=False))


def list_tasks_menu(tasks):
    while True:
        choices = [f"{i+1}. {t.device_id} | {t.property_name} | {t.mode}" for i, t in enumerate(tasks)]
        choices.append("Return")
        answer = inquirer.select(
            message="Select a task to view details:",
            choices=choices,
            cycle=True,
            pointer=">",
            instruction="(Use arrow keys, Enter to select)",
        ).execute()

        if answer == "Return":
            break
        else:
            index = choices.index(answer)
            show_task_details(tasks[index])


def safe_value(value):
    """返回字段值或'N/A'"""
    return str(value) if value is not None else "N/A"

def start_crawler():
    tasks = load_tasks_from_json("./tasks.json")
    new_tasks = []
    total_tasks = len(tasks)

    for index, task in enumerate(tasks):
        # 分割线
        console.print(f"\n[bold magenta]{'=' * 50}[/]")

        console.print(f"[bold yellow]🚀 Task Progress: [{index + 1}/{total_tasks}][/]")

        show_task_details(task)

        if task.status == "done":
            console.print(f"[green]✔️ Task {task.task_id} is already done, skipping.[/]")
            continue

        try:
            console.print(f"[bold cyan]🔄 Starting Task {task.task_id}...[/]")
            updated_task = fetch_device_data(task)
            console.print(f"[bold green]✅ Task {task.task_id} completed successfully.[/]")
            new_tasks.append(updated_task)
        except Exception as e:
            console.print(f"[bold red]❌ Task {task.task_id} failed: {e}[/]")
            new_tasks.append(task)

        console.print(f"[bold magenta]{'=' * 50}[/]")

    # 保存更新后的任务列表
    console.print("\n[bold yellow]💾 Saving updated tasks...[/]")
    save_tasks_to_json(new_tasks, "./tasks.json")
    console.print("[bold green]🎉 All tasks processed and saved successfully![/]")
    # press any key to continue
    console.print("[bold blue]Press Enter to return to the main menu...[/]")
    input()


def main_menu():

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        answer = inquirer.select(
            message="Device Data Crawler Menu",
            choices=["List Tasks", "Start Crawler", "Exit"],
            cycle=True,
            pointer=">",
            instruction="(Use arrow keys, Enter to select)",
        ).execute()

        if answer == "List Tasks":
            tasks = load_tasks_from_json("./tasks.json")
            if not tasks:
                console.print("[bold red]No tasks found.[/]")
            else:
                list_tasks_menu(tasks)
        elif answer == "Start Crawler":
            console.print("[yellow]Starting crawler tasks...[/]")
            start_crawler()
            # TODO: call your start_crawler function here
            # Show 进度 of Tasks
        elif answer == "Exit":
            console.print("[bold red]Exiting...[/]")
            # TODO: Handle All Tasks in Running
            break

if __name__ == "__main__":
    main_menu()
