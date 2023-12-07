# -*- coding: utf-8 -*-
import json

from codecs import open as codecs_open
from io import open as io_open
from host_tools.utils import Dir, Shell, Str
from random import randint
from shutil import move, copyfile
from os import remove, walk, listdir, scandir
from os.path import exists, isfile, isdir, join, getctime, basename, getsize, relpath, dirname
from tempfile import gettempdir
from platform import system
from requests import get, head
from zipfile import ZipFile, ZIP_DEFLATED
from py7zr import SevenZipFile
from rich import print
from rich.progress import track


class File:
    EXCEPTIONS = ['.DS_Store']

    @staticmethod
    def get_headers(url: str):
        status = head(url)
        if status.status_code == 200:
            return status.headers
        print(f"[bold red]|WARNING| Can't get headers\nURL:{url}\nResponse: {status.status_code}")
        return False

    @staticmethod
    def download(url: str, dir_path: str, name: str = None) -> None:
        Dir.create(dir_path, stdout=False)

        _name = name if name else basename(url)
        _path = join(dir_path, _name)

        with get(url, stream=True) as r:
            r.raise_for_status()
            with open(_path, 'wb') as file:
                for chunk in track(r.iter_content(chunk_size=1024 * 1024), description=f'[red] Downloading: {_name}'):
                    if chunk:
                        file.write(chunk)
        print(f"[bold green]|INFO| File Saved to: {_path}" if isfile(_path) else f"[red]|WARNING| Not exist")

        if int(getsize(_path)) != int(r.headers['Content-Length']):
            print(f"[red]|WARNING| Size different\nFile:{getsize(_path)}\nOn server:{r.headers['Content-Length']}")

    @staticmethod
    def read(file_path: str, mode: str = 'r', encoding='utf-8') -> str:
        with io_open(file_path, mode, encoding=encoding) as file:
            return file.read()

    @staticmethod
    def write(file_path: str, text: str, mode: str = 'w') -> None:
        with open(file_path, mode) as file:
            file.write(text)

    @staticmethod
    def change_access(dir_path: str, mode: str = '+x') -> None:
        if system().lower() == 'windows':
            return print("[bold red]|WARNING| Can't change access on windows")
        Shell.run(f'chmod {mode} {join(Str.delete_last_slash(dir_path))}/*')

    @staticmethod
    def delete(path: "str | tuple | list", stdout: bool = True, stderr: bool = True) -> None:
        if not path:
            return print(f"[red]|DELETE ERROR| Path should be string, tuple or list not {path}") if stderr else None

        for _path in [path] if isinstance(path, str) else path:
            object_path = _path.rstrip("*")
            if not exists(object_path):
                print(f"[bold red]|DELETE WARNING| File not exist: {object_path}") if stderr else ...
                continue

            if isdir(object_path):
                Dir.delete(object_path, clear_dir=_path.endswith("*"), stdout=stdout, stderr=stderr)
            else:
                remove(object_path)

            if exists(object_path):
                print(f"[bold red]|DELETE WARNING| Is not deleted: {_path}") if stderr else ...
                continue
            print(f'[green]|INFO| Deleted: {_path}') if stdout else ...

    @staticmethod
    def compress(path: str, archive_path: str = None, delete: bool = False) -> None:
        """
        :param path: Path to compression files.
        :param archive_path: Path to the archive file.
        :param delete:  Deleting files after compression.
        """
        _name = basename(Str.delete_last_slash(path))
        _archive_path = archive_path if archive_path else join(dirname(path) if isfile(path) else path, f"{_name}.zip")

        if not exists(path):
            return print(f'[bold red]|COMPRESS WARNING| Path for compression does not exist: {path}')

        Dir.create(dirname(_archive_path), stdout=False)
        with ZipFile(_archive_path, 'w') as _zip:
            if isdir(path):
                exceptions = File.EXCEPTIONS + [f"{basename(_archive_path)}"]
                for file in track(File.get_paths(path), description=f"[green]|INFO| Compressing dir: {_name}"):
                    if basename(file) not in exceptions:
                        _zip.write(file, relpath(file, path), compress_type=ZIP_DEFLATED)
                if delete:
                    _archive_name = basename(_archive_path)
                    File.delete([join(path, obj) for obj in listdir(path) if obj != _archive_name], stdout=False)
            else:
                print(f'[green]|INFO| Compressing file: {path}')
                _zip.write(path, _name, compress_type=ZIP_DEFLATED)
                File.delete(path, stdout=False) if delete else ...

        if exists(_archive_path) and getsize(_archive_path) != 0:
            return print(f"[green]|INFO| Success compressed: {_archive_path}")
        print(f"[WARNING] Archive not exists: {_archive_path}")

    @staticmethod
    def read_json(path_to_json: str, encoding: str = "utf_8_sig") -> json:
        with codecs_open(path_to_json, mode="r", encoding=encoding) as file:
            return json.load(file)

    @staticmethod
    def write_json(path: str, data: "dict | list", mode: str = 'w', indent: int = 2) -> None:
        Dir.create(dirname(path))
        with open(path, mode) as file:
            json.dump(data, file, indent=indent)

    @staticmethod
    def unpacking(archive_path: str, execute_path: str, delete_archive: bool = False) -> None:
        if archive_path.endswith('.7z'):
            File.unpacking_7z(archive_path=archive_path, execute_path=execute_path, delete_archive=delete_archive)
        else:
            File.unpacking_zip(archive_path=archive_path, execute_path=execute_path, delete_archive=delete_archive)

    @staticmethod
    def unpacking_7z(archive_path: str, execute_path: str, delete_archive: bool = False) -> None:
        print(f'[green]|INFO| Unpacking {basename(archive_path)}.')
        with SevenZipFile(archive_path, 'r') as archive:
            archive.extractall(path=execute_path)
            print(f'[green]|INFO| Unpack Completed to: {execute_path}')
        File.delete(archive_path, stdout=False) if delete_archive else ...

    @staticmethod
    def unpacking_zip(archive_path: str, execute_path: str, delete_archive: bool = False) -> None:
        with ZipFile(archive_path) as archive:
            archive.extractall(execute_path)
        File.delete(archive_path) if delete_archive else ...

    @staticmethod
    def make_tmp(file_path: str, tmp_dir: str = gettempdir()) -> str:
        Dir.create(tmp_dir, stdout=False) if not isdir(tmp_dir) else ...
        tmp_file_path = File.unique_name(tmp_dir, file_path.split(".")[-1])
        if exists(file_path):
            File.copy(file_path, tmp_file_path, stdout=False)
            return tmp_file_path
        print(f"[red]|ERROR| Can't create tmp file.\nThe source file does not exist: {file_path}")

    @staticmethod
    def unique_name(path: str, extension: str = None) -> str:
        _ext = extension.replace(".", "") if extension else None
        while True:
            random_path = join(path, f"{randint(500, 50000)}{('.' + _ext) if _ext else ''}".strip())
            if not exists(random_path):
                return random_path

    @staticmethod
    def last_modified(dir_path: str) -> str:
        files = File.get_paths(dir_path, exceptions_files=File.EXCEPTIONS)
        return max(files, key=getctime) if files else print('[bold red]|WARNING| Last modified file_name not found')

    @staticmethod
    def copy(
            path_from: str,
            path_to: str,
            stdout: bool = True,
            stderr: bool = True,
            dir_overwrite: bool = False
    ) -> None:
        if not exists(path_from):
            return print(f"[bold red]|COPY WARNING| Path from not exist: {path_from}")

        if isdir(path_from):
            Dir.copy(path_from, path_to, stdout=stdout, stderr=stderr, overwrite=dir_overwrite)
        elif isfile(path_from):
            copyfile(path_from, path_to)
        else:
            print(f"[bold red]|COPY WARNING| Can't verify object: {path_from}")

        if exists(path_to):
            return print(f'[green]|INFO| Copied to: {path_to}') if stdout else None
        return print(f'[bold red]|COPY WARNING| File not copied: {path_to}') if stderr else None

    @staticmethod
    def move(path_from: str, path_to: str, stdout: bool = True, stderr: bool = True) -> None:
        if exists(path_from):
            move(path_from, path_to)
            return print("[bold red]|MOVE WARNING| File not moved") if not exists(path_to) and stderr else None
        return print(f"[bold red]|MOVE WARNING| File not exist: {path_from}") if stdout else None

    @staticmethod
    def fix_double_dir(dir_path: str):
        path = join(dir_path, basename(dir_path))
        if isdir(path):

            for file in listdir(path):
                File.move(join(path, file), join(dir_path, file))

            if not any(scandir(path)):
                print("[green]|INFO| Fixed double folder")
                return File.delete(path)

            print("[red]|WARNING| Not all objects are moved")

    @staticmethod
    def get_paths(
            path: str,
            extension: "tuple | str" = None,
            names: list = None,
            exceptions_files: list = None,
            exceptions_dirs: list = None,
            dir_include: str = None,
            name_include: str = None,
            name_starts_with: str = None
    ) -> list:
        ext_dirs = [join(path, ext_path) for ext_path in exceptions_dirs] if exceptions_dirs else []

        file_paths = []

        for root, dirs, files in walk(path):
            for filename in files:
                if (
                    exceptions_files and filename in exceptions_files
                    or exceptions_dirs and [path for path in ext_dirs if path in root]
                    or dir_include and (dir_include not in basename(root))
                    or name_include and (name_include not in filename)
                    or name_starts_with and not filename.startswith(name_starts_with)
                ):
                    continue
                if names:
                    file_paths.append(join(root, filename)) if filename in names else ...
                elif extension:
                    if filename.lower().endswith(extension if isinstance(extension, tuple) else extension.lower()):
                        file_paths.append(join(root, filename))
                else:
                    file_paths.append(join(root, filename))

        return file_paths
