# -*- coding: utf-8 -*-
import win32service
import winerror
import psutil
import win32serviceutil

from .service import Service

class Windows(Service):

    @staticmethod
    def get_all() -> list[dict]:
        return [
            {
                'name': service.name(),
                'display_name': service.display_name(),
                'status': service.status()
            }
            for service in psutil.win_service_iter()
        ]

    @staticmethod
    def stop(service_name: str):
        Windows._execute_operation(service_name, "stopped", win32serviceutil.StopService)

    @staticmethod
    def start(service_name: str):
        Windows._execute_operation(service_name, "started", win32serviceutil.StartService)

    @staticmethod
    def restart(service_name: str):
        Windows._execute_operation(service_name, "restarted", win32serviceutil.RestartService)

    @staticmethod
    def _execute_operation(service_name: str, operation: str, action_func):
        try:
            action_func(service_name)
            print(f"Service '{service_name}' {operation} successfully.")
        except Exception as e:
            Windows._handle_error(service_name, operation, e)

    @staticmethod
    def _handle_error(service_name: str, operation: str, error: Exception):
        if isinstance(error, PermissionError):
            print(f"[red]|ERROR| Permission denied to {operation} service '{service_name}': {error}")
        elif isinstance(error, win32service.error) and error.winerror == winerror.ERROR_ACCESS_DENIED:
            print("[red]|ERROR| Error: Access Denied")
        else:
            print(f"[red]|ERROR| An error occurred while {operation} service '{service_name}': {error}")
