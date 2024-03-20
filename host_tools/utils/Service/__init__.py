# -*- coding: utf-8 -*-
from ...info import HostInfo
if HostInfo().os == 'windows':
    from .windows import Windows as Service
else:
    from .unix import Unix as Service
