# -*- coding: utf-8 -*-
from .utils import Dir, Str, Shell, File, Process
from .host_info import HostInfo
from .singleton import singleton

if HostInfo().os == 'windows':
    from .windows_handler import Window
