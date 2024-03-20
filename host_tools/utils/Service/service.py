# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class Service(ABC):

    @staticmethod
    @abstractmethod
    def get_all() -> list[dict]: ...

    @staticmethod
    @abstractmethod
    def stop(service_name: str): ...

    @staticmethod
    @abstractmethod
    def start(service_name: str): ...

    @staticmethod
    @abstractmethod
    def restart(service_name: str): ...
