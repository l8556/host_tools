# -*- coding: utf-8 -*-
from distro import name, version, id
from ..singleton import singleton


@singleton
class Unix:
    def __init__(self):
        self._name = None
        self._version = None
        self._id = None
        self._pretty_name = None

    @property
    def pretty_name(self) -> str:
        if self._pretty_name is None:
            self._pretty_name = name(pretty=True)
        return self._pretty_name

    @property
    def id(self) -> str:
        if self._id is None:
            self._id = id()
        return self._id

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = name()
        return self._name

    @property
    def version(self) -> str:
        if self._version is None:
            self._version = version()
        return self._version
