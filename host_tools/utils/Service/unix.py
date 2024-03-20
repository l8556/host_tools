# -*- coding: utf-8 -*-
from subprocess import run, CalledProcessError, check_output, PIPE, CompletedProcess
from rich import print

from .service import Service


class Unix(Service):

    @staticmethod
    def get_all() -> list[dict]:
        try:
            output = check_output(["systemctl", "--all", "--type=service", "--no-pager", "--no-legend"])
            services = []
            for line in output.splitlines():
                service_info = line.split(None, 4)
                if len(service_info) == 5:
                    services.append({
                        'unit': service_info[0].decode(),
                        'load': service_info[1].decode(),
                        'active': service_info[2].decode(),
                        'sub': service_info[3].decode(),
                        'description': service_info[4].decode()
                    })
            return services
        except CalledProcessError as e:
            print("[red]|ERROR| Error: Unable to retrieve service information.")
            return []

    @staticmethod
    def stop(service_name: str) -> None:
        Unix._manage_service('stop', service_name)

    @staticmethod
    def start(service_name: str) -> None:
        Unix._manage_service('start', service_name)

    @staticmethod
    def restart(service_name: str) -> None:
        Unix._manage_service('restart', service_name)

    @staticmethod
    def _manage_service(action: str, service_name: str) -> None:
        try:
            result = run(['systemctl', action, service_name], check=True, stdout=PIPE, stderr=PIPE, text=True)
            print(result.stderr.strip()) if result.stderr else ...
            print(result.stdout.strip()) if result.stdout else ...
            print(f"[green]|INFO| Service '{service_name}' {action}ed successfully.")
        except CalledProcessError as e:
            print(f"[red]|ERROR| Failed to {action} service '{service_name}': {e}")
