# -*- coding: utf-8 -*-
from psutil import process_iter
from rich import print


def terminate(names: list) -> None:
    for process in process_iter():
        for terminateProcess in names:
            if terminateProcess in process.name():
                try:
                    process.terminate()
                except Exception as e:
                    print(f'[bold red]|Warning| Exception when terminate process {terminateProcess}: {e}')
