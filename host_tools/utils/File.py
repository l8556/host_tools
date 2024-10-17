# -*- coding: utf-8 -*-
import json
import hashlib

from codecs import open as codecs_open
from io import open as io_open
from typing import Optional

from requests.structures import CaseInsensitiveDict

from host_tools.utils import Dir, Shell, Str
from random import randint
from shutil import move, copyfile
from os import remove, walk, listdir, scandir, chmod
from os.path import exists, isfile, isdir, join, getctime, basename, getsize, relpath, dirname
from tempfile import gettempdir
from platform import system
from requests import get, head
from zipfile import ZipFile
from py7zr import SevenZipFile
from rich import print
from rich.progress import track


class File:
    EXCEPTIONS = ['.DS_Store']

    @staticmethod
    def get_sha256(file_path: str, block_size=65536) -> str:
        """
        Calculate the SHA-256 hash of a file.

        :param file_path: The path to the file for which to calculate the SHA-256 hash.
        :param block_size: (Optional) The block size (in bytes) for reading the file. Defaults to 65536.
        :return: The SHA-256 hash of the file as a hexadecimal string.
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as file:
            for block in iter(lambda: file.read(block_size), b''):
                sha256.update(block)

        return sha256.hexdigest()

    @staticmethod
    def get_headers(url: str, stderr: bool = False) -> Optional[CaseInsensitiveDict[str]]:
        """
        Retrieve headers from a given URL.

        :param url: The URL from which to retrieve headers.
        :param stderr: (Optional) If True, prints a warning message when unable to retrieve headers. Defaults to False.
        :return: A dictionary containing the headers if the request is successful, None otherwise.
        """
        status = head(url)

        if status.status_code == 200:
            return status.headers

        print(f"[bold red]|WARNING| Can't get headers\nURL:{url}\nResponse: {status.status_code}") if stderr else None
        return None

    @staticmethod
    def download(
            url: str,
            dir_path: str,
            name: str = None,
            process_bar: bool = True,
            stdout: bool = True,
            stderr: bool = True,
            chunk_size: int = 1024 * 1024
    ) -> None:
        """
        :param chunk_size:
        :param url: download link
        :param dir_path: download folder
        :param name: download filename
        :param process_bar: Enables/disables the file upload status bar display,
        only 1 status bar can be displayed at a time.
        :param stdout: Enable/disable display of successful download messages
        :param stderr: Enable/disable display of error messages
        """

        Dir.create(dir_path, stdout=False)

        _name = name if name else basename(url)
        _path = join(dir_path, _name)

        with get(url, stream=True) as request:
            request.raise_for_status()
            with open(_path, 'wb') as file:
                _iter = request.iter_content(chunk_size=chunk_size)
                for chunk in track(_iter, description=f'[red] Downloading: {_name}') if process_bar else _iter:
                    if chunk:
                        file.write(chunk)

        if stdout:
            print(f"[bold green]|INFO| File Saved to: {_path}" if isfile(_path) else f"[red]|WARNING| Not exist")

        if stderr and int(getsize(_path)) != int(request.headers['Content-Length']):
            print(f"[red]|WARNING| Size different\nFile:{getsize(_path)}\nServer:{request.headers['Content-Length']}")

    @staticmethod
    def read(file_path: str, mode: str = 'r', encoding='utf-8') -> str:
        with io_open(file_path, mode, encoding=encoding) as file:
            return file.read()

    @staticmethod
    def write(
            file_path: str,
            text: str,
            mode: str = 'w',
            newline: str = None,
            encoding: str = None,
            errors: str = None
    ) -> None:
        """
        Write text to a file.

        :param file_path: The path to the file where the text will be written.
        :param text: The text to be written to the file.
        :param mode: (Optional) The mode in which the file will be opened. Defaults to 'w' (write).
        :param newline: (Optional) The newline character(s) to use. Defaults to None.
        :param encoding: (Optional) The encoding to be used when writing the text to the file. Defaults to None.
        :param errors: (Optional) The errors is an optional string that specifies how encoding errors are to
        be handled---this argument should not be used in binary mode. Pass
        'strict' to raise a ValueError exception if there is an encoding error
        (the default of None has the same effect), or pass 'ignore' to ignore
        errors. (Note that ignoring encoding errors can lead to data loss.)
        See the documentation for codecs.register or run 'help(codecs.Codec)'
        for a list of the permitted encoding error strings.
        """
        with open(file_path, mode, newline=newline, encoding=encoding, errors=errors) as file:
            file.write(text)

    @staticmethod
    def change_access(path: str, mode: str = '+x') -> None:
        """
        Only for Unix.
        """
        if system().lower() == 'windows':
            return

        if isdir(path):
            path = f'{Str.delete_last_slash(path)}/*'

        Shell.run(f'chmod {mode} {path}')


    @staticmethod
    def delete(
            path: "str | tuple | list",
            stdout: bool = True,
            stderr: bool = True,
            full_access: bool = False
    ) -> None:
        """
        Delete files or directories with optional full access permission.

        :param path: A single path as a string, or multiple paths as a tuple or list.
        :param stdout: Whether to print informational messages to stdout. Defaults to True.
        :param stderr: Whether to print error messages to stderr. Defaults to True.
        :param full_access: If True, sets full access permissions (0o777) before deletion. Defaults to False.
        """
        if not path:
            return print(f"[red]|DELETE ERROR| Path should be string, tuple or list not {path}") if stderr else None

        for _path in [path] if isinstance(path, str) else path:
            object_path = _path.rstrip("*")
            if not exists(object_path):
                print(f"[bold red]|DELETE WARNING| File not exist: {object_path}") if stderr else ...
                continue

            chmod(path, 0o777) if full_access else None

            if isdir(object_path):
                Dir.delete(object_path, clear_dir=_path.endswith("*"), stdout=stdout, stderr=stderr)
            else:
                remove(object_path)

            if stderr and exists(object_path):
                print(f"[bold red]|DELETE WARNING| Is not deleted: {_path}")
            else:
                print(f'[green]|INFO| Deleted: {_path}') if stdout else ...

    @staticmethod
    def compress(
            path: str,
            archive_path: str = None,
            delete: bool = False,
            compress_type: int = 8,
            stdout: bool = False,
            stderr: bool = True,
            progress_bar: bool = True
    ) -> None:
        """
        :param stdout:
        :param stderr:
        :param progress_bar:
        :param compress_type: ZIP_STORED = 0, ZIP_DEFLATED = 8, ZIP_BZIP2 = 12, ZIP_LZMA = 14
        :param path: Path to compression files.
        :param archive_path: Path to the archive file.
        :param delete:  Deleting files after compression.
        """
        _name = basename(Str.delete_last_slash(path))
        _archive_path = archive_path or join(dirname(path) if isfile(path) else path, f"{_name}.zip")

        if not exists(path):
            return print(f'[red]|COMPRESS WARNING| Path for compression does not exist: {path}') if stderr else None

        Dir.create(dirname(_archive_path), stdout=False)

        with ZipFile(_archive_path, 'w') as _zip:
            if isdir(path):
                print(f'[green]|INFO| Compressing dir: {path}') if stdout else None

                files = File.get_paths(path, exceptions_files=File.EXCEPTIONS + [f"{basename(_archive_path)}"])
                _iter = track(files, description=f"[green]|INFO| Compressing dir: {_name}") if progress_bar else files

                for file in _iter:
                    _zip.write(file, relpath(file, path), compress_type=compress_type)

                if delete:
                    _archive_name = basename(_archive_path)
                    File.delete([join(path, obj) for obj in listdir(path) if obj != _archive_name], stdout=False)

            else:
                print(f'[green]|INFO| Compressing file: {path}') if stdout else None
                _zip.write(path, _name, compress_type=compress_type)
                File.delete(path, stdout=False) if delete else None

        if stderr and not exists(_archive_path) or getsize(_archive_path) == 0:
            return print(f"[ERROR] Archive not exists: {_archive_path}")

        print(f"[green]|INFO| Success compressed: {_archive_path}") if stdout else None


    @staticmethod
    def read_json(path_to_json: str, encoding: str = "utf_8_sig") -> json:
        with codecs_open(path_to_json, mode="r", encoding=encoding) as file:
            return json.load(file)

    @staticmethod
    def write_json(
            path: str,
            data: "dict | list",
            mode: str = 'w',
            indent: int = 2,
            ensure_ascii: bool = True,
            encoding: str = 'utf-8',
            ends_with_blank_line: bool = False
    ) -> None:
        Dir.create(dirname(path), stdout=False)
        with open(path, mode, encoding=encoding) as file:
            json.dump(data, file, ensure_ascii=ensure_ascii, indent=indent)
            if ends_with_blank_line:
                file.write('\n')

    @staticmethod
    def unpacking(archive_path: str, execute_path: str, delete_archive: bool = False, stdout: bool = True) -> None:
        if archive_path.endswith('.7z'):
            File.unpacking_7z(
                archive_path=archive_path,
                execute_path=execute_path,
                delete_archive=delete_archive,
                stdout=stdout
            )
        else:
            File.unpacking_zip(
                archive_path=archive_path,
                execute_path=execute_path,
                delete_archive=delete_archive,
                stdout=stdout
            )

    @staticmethod
    def unpacking_7z(archive_path: str, execute_path: str, delete_archive: bool = False, stdout: bool = False) -> None:
        print(f'[green]|INFO| Unpacking via SevenZip: {basename(archive_path)}.') if stdout else None

        with SevenZipFile(archive_path, 'r') as archive:
            archive.extractall(path=execute_path)

        print(f'[green]|INFO| Unpack Completed to: {execute_path}') if stdout else None
        File.delete(archive_path, stdout=False) if delete_archive else ...

    @staticmethod
    def unpacking_zip(archive_path: str, execute_path: str, delete_archive: bool = False, stdout: bool = False) -> None:
        print(f'[green]|INFO| Unpacking via ZipFile: {basename(archive_path)}.') if stdout else None

        with ZipFile(archive_path) as archive:
            archive.extractall(execute_path)

        print(f'[green]|INFO| Unpack Completed to: {execute_path}') if stdout else None
        File.delete(archive_path, stdout=stdout) if delete_archive else ...

    @staticmethod
    def make_tmp(file_path: str, tmp_dir: str = gettempdir()) -> str:
        """
        Create a temporary copy of a file.

        :param file_path: The path to the file to create a temporary copy of.
        :param tmp_dir: (Optional) The directory in which to create the temporary copy. Defaults to the system temporary directory.
        :return: The path to the temporary copy of the file.
        """
        Dir.create(tmp_dir, stdout=False) if not isdir(tmp_dir) else ...
        tmp_file_path = File.unique_name(tmp_dir, file_path.split(".")[-1])
        if exists(file_path):
            File.copy(file_path, tmp_file_path, stdout=False)
            return tmp_file_path
        print(f"[red]|ERROR| Can't create tmp file.\nThe source file does not exist: {file_path}")

    @staticmethod
    def unique_name(path: str, extension: str = None) -> str:
        """
        Generate a unique filename in a given directory.

        :param path: The directory path in which to generate the unique filename.
        :param extension: (Optional) The extension for the filename. If provided, it should not contain a leading period.
        :return: A unique filename with an optional extension.
        """
        _ext = extension.replace(".", "") if extension else None
        while True:
            random_path = join(path, f"{randint(500, 50000)}{('.' + _ext) if _ext else ''}".strip())
            if not exists(random_path):
                return random_path

    @staticmethod
    def last_modified(dir_path: str) -> str:
        """
        Get the path of the last modified file in a directory.

        :param dir_path: The path to the directory to search for files.
        :return: The path of the last modified file in the directory.
        If no files are found in the directory, prints a warning message.
        """
        files = File.get_paths(dir_path, exceptions_files=File.EXCEPTIONS)
        return max(files, key=getctime) if files else print('[red]|WARNING| Last modified file not found')

    @staticmethod
    def copy(
            path_from: str,
            path_to: str,
            stdout: bool = True,
            stderr: bool = True,
            dir_overwrite: bool = False
    ) -> None:
        if not exists(path_from):
            return print(f"[red]|WARNING| Path not exist: {path_from}") if stderr else None

        if isdir(path_from):
            Dir.copy(path_from, path_to, stdout=stdout, stderr=stderr, overwrite=dir_overwrite)
        else:
            copyfile(path_from, path_to)

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
            path_include: str = None,
            dir_include: str = None,
            name_include: str = None,
            name_starts_with: str = None
    ) -> list:
        """
        Retrieve file paths under a given directory based on specified criteria.

        :param path: The directory path to search for files.
        :param extension: (Optional) The extension(s) of the files to include. Can be a string or a tuple of strings. Defaults to None.
        :param names: (Optional) A list of specific filenames to include. Defaults to None.
        :param exceptions_files: (Optional) A list of filenames to exclude from the results. Defaults to None.
        :param exceptions_dirs: (Optional) A list of directory names to exclude from the search. Defaults to None.
        :param path_include: (Optional) Include only files containing this substring in the directory path. Default is set to No.
        :param dir_include: (Optional) Only include directories containing this substring in their name. Defaults to None.
        :param name_include: (Optional) Only include files containing this substring in their name. Defaults to None.
        :param name_starts_with: (Optional) Only include files whose names start with this substring. Defaults to None.

        :return: A list of file paths matching the specified criteria.
        """

        if exceptions_dirs:
            exceptions_dirs = {join(path, dir_name) for dir_name in (exceptions_dirs or set())}

        if extension:
            extension = tuple(ext.lower() for ext in extension) if isinstance(extension, tuple) else extension.lower()

        file_paths = []

        for root, dirs, files in walk(path):
            if exceptions_dirs and any(ext_path in root for ext_path in exceptions_dirs):
                continue

            if dir_include and dir_include not in basename(root):
                continue

            if path_include and path_include not in root:
                continue

            for filename in files:
                if exceptions_files and filename in exceptions_files:
                    continue

                if name_include and name_include not in filename:
                    continue

                if name_starts_with and not filename.startswith(name_starts_with):
                    continue

                if names and filename not in names:
                    continue

                if extension and not filename.lower().endswith(extension):
                    continue

                file_paths.append(join(root, filename))

        return file_paths
