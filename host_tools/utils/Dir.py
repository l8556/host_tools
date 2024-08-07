# -*- coding: utf-8 -*-
from shutil import rmtree, copytree
from os import makedirs, scandir, walk, chmod
from os.path import isdir, join
from rich import print


def copy(path_from: str, path_to: str, stdout: bool = True, stderr: bool = True, overwrite: bool = False) -> None:
    if not isdir(path_from):
        return print(f"[bold red]|COPY WARNING| Path from not is folder: {path_from}")

    _path_to = path_to

    if not overwrite:
        num = 0
        while isdir(_path_to):
            _path_to = path_to + f"({num})"
            num += 1

    copytree(path_from, _path_to, dirs_exist_ok=overwrite)

    if isdir(path_to):
        return print(f'[green]|INFO| Copied to: {path_to}') if stdout else None
    return print(f'[bold red]|COPY WARNING| Dir not copied: {path_to}') if stderr else None

def create(dir_path: "str | tuple | list", stdout: bool = True, stderr: bool = True) -> None:
    for _dir_path in [dir_path] if isinstance(dir_path, str) else dir_path:
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


def delete(
        path: "str | tuple | list",
        clear_dir: bool = False,
        stdout: bool = True,
        stderr: bool = True,
        full_access: bool = False
) -> None:
    """
    Delete files or directories specified by the path(s). Optionally clear directory contents and change permissions before deletion.

    :param path: A single path, tuple of paths, or list of paths to delete.
    :param clear_dir: If True, re-create directories after deletion to ensure they are empty. Defaults to False.
    :param stdout: If True, print information messages to standard output. Defaults to True.
    :param stderr: If True, print warning messages to standard error. Defaults to True.
    :param full_access: If True, sets full access permissions (0o777) before deletion. Defaults to False.
    on 0o777(full access). Defaults to False.
    """
    for _path in [path] if isinstance(path, str) else path:
        if not isdir(_path):
            print(f"[bold red]|DELETE WARNING| Directory not exist: {_path}") if stderr else ...
            continue

        chmod(path, 0o777) if full_access else None
        rmtree(_path, ignore_errors=True)

        if clear_dir:
            create(_path, stdout=False)
            if stderr and any(scandir(_path)):
                print(f"[bold red]|DELETE WARNING| Not all files are removed from directory: {path}")
                continue

        print(f'[green]|INFO| Deleted: {_path}') if stdout and not isdir(_path) else ...
