# -*- coding: utf-8 -*-
from re import search as re_search
import string
from random import choice


def delete_last_slash(path: str) -> str:
    return path.rstrip(path[-1]) if path[-1] in ['/', '\\'] else path

def get_random(chars=string.ascii_uppercase + string.digits, num_chars=50) -> str:
    return ''.join(choice(chars).lower() for _ in range(int(num_chars)))

def find_by_key(text: str, key: str, split_by: str = '\n', separator: str = ':') -> "str | None":
    for line in text.split(split_by):
        if separator in line:
            _key, value = line.strip().split(separator, 1)
            if _key.lower() == key.lower():
                return value.strip()

def search(text: str, pattern: str, group_num: int = 0) -> 'str | None':
    try:
        return re_search(pattern, text).group(group_num)
    except (IndexError, AttributeError):
        return None
