# -*- coding: utf-8 -*-
from shutil import rmtree
from os import makedirs, scandir, walk
from os.path import exists, isdir, join
from rich import print


def create(dir_path: "str | tuple", stdout: bool = True, stderr: bool = True) -> None:
    for _dir_path in dir_path if isinstance(dir_path, tuple) else [dir_path]:
        if not isdir(_dir_path):
            makedirs(_dir_path)

            if isdir(_dir_path):
                print(f'[green]|INFO| Folder Created: {_dir_path}') if stdout else ...
                continue
            print(f'[bold red]|WARNING| Create folder warning. Folder not created: {_dir_path}') if stderr else ...
            continue

        print(f'[green]|INFO| Folder exists: {_dir_path}') if stdout else ...

def get_paths(path: str, end_dir: str = None, dir_include: str = None) -> list:
    dir_paths = []

    for root, dirs, files in walk(path):
        for dir_name in dirs:
            if end_dir:
                if dir_name.lower().endswith(end_dir if isinstance(end_dir, tuple) else end_dir.lower()):
                    dir_paths.append(join(root, dir_name))
            elif dir_include:
                if dir_include in dir_name:
                    dir_paths.append(join(root, dir_name))
            else:
                dir_paths.append(join(root, dir_name))

    return dir_paths


def delete(path: "str | tuple", create_dir: bool = False, stdout: bool = True, stderr: bool = True) -> None:
    for _path in path if isinstance(path, tuple) else [path]:
        if not isdir(_path):
            print(f"[bold red]|DELETE WARNING| Directory not exist: {_path}") if stderr else ...
            continue

        rmtree(_path, ignore_errors=True)

        if create_dir:
            create(_path, stdout=False)
            if stderr and any(scandir(_path)):
                return print(f"[bold red]|DELETE WARNING| Not all files are removed from directory: {path}")
            print(f'[green]|INFO| Deleted: {_path}') if stdout else ...
