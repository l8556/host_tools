# -*- coding: utf-8 -*-
from .utils import Dir, Str, Shell, File, Process
from .info import HostInfo
from .singleton import singleton

if HostInfo().os == 'windows':
    from .windows_handler import Window
