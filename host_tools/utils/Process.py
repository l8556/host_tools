# -*- coding: utf-8 -*-
import psutil
from rich import print

def terminate(names: "list | str") -> None:
    names = {names.lower()} if isinstance(names, str) else {name.lower() for name in names}

    for process in psutil.process_iter():
        if get_name(process) in names:
            try:
                process.kill()
            except psutil.NoSuchProcess:
                print(f"[bold red]|ERROR| Exception when terminating process {process.name()}")

def get_name(process: psutil.Process) -> str:
    try:
        return process.name()
    except (psutil.NoSuchProcess, TypeError) as e:
        print(f"[bold red]|ERROR| Error while retrieving process name: {e}")
        return ''

def get_running() -> list[dict]:
    running_processes = []

    for proc in psutil.process_iter():
        try:
            if proc.status().lower() == 'running':
                running_processes.append({
                    "pid": proc.pid,
                    "name": proc.name(),
                    "create_time": proc.create_time()
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return running_processes

def get_all() -> list[dict]:
    processes = []

    for proc in psutil.process_iter():
        try:
            processes.append(proc.as_dict(attrs=['pid', 'name', 'username']))
        except psutil.NoSuchProcess:
            pass

    return processes

def get_info(process_name: str) -> dict:
    for process in psutil.process_iter():
        if get_name(process) == process_name:
            return process.as_dict()
