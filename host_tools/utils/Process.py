# -*- coding: utf-8 -*-
import psutil
from psutil import process_iter
from rich import print


def terminate(names: list) -> None:
    for process in process_iter():
        for terminateProcess in names:
            if terminateProcess in get_name(process):
                try:
                    process.terminate()
                except Exception as e:
                    print(f'[bold red]|Warning| Exception when terminate process {terminateProcess}: {e}')

def get_name(process: psutil.Process) -> str:
    try:
        return process.name()
    except (psutil.NoSuchProcess, TypeError) as e:
        print(f"[bold red]|ERROR| Error while retrieving process name: {e}")
        return ''

def get_running() -> list[dict]:
    running_processes = []

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            running_processes.append({"id": proc.info['pid'], "name": proc.info['name']})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return running_processes

def get_all() -> list[dict]:
    processes = []

    for proc in psutil.process_iter():
        try:
            process_info = proc.as_dict(attrs=['pid', 'name', 'username'])
            processes.append(process_info)
        except psutil.NoSuchProcess:
            pass

    return processes
