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
