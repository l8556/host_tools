# -*- coding: utf-8 -*-
import psutil
from subprocess import (
    Popen,
    PIPE,
    getoutput as sb_getoutput,
    call as sb_call,
    CompletedProcess,
    TimeoutExpired
)


def get_output(command: str) -> str:
    return sb_getoutput(command)

def call(command: str, shell: bool = True) -> None:
    sb_call(command, shell=shell)

def run(
        command: str,
        timeout: int = None,
        shell: bool = True,
        stdout: bool = True,
        stderr: bool = True,
        kill_children_processes: bool = False
    ) -> CompletedProcess:
    """
    Run a shell command and return a `CompletedProcess` object.

    :param command: The command to run.
    :param timeout: (Optional) The maximum time to wait for the command to finish (in seconds). Defaults to None.
    :param shell: (Optional) If True, the command will be executed through the shell. Defaults to True.
    :param stdout: (Optional) If True, prints the standard output of the command. Defaults to True.
    :param stderr: (Optional) If True, prints the standard error of the command. Defaults to True.
    :param kill_children_processes: (Optional) If True, kill any child processes spawned by the command if it times out. Defaults to False.
    :return: A `CompletedProcess` object representing the result of the command execution.
    """
    with Popen(
        command if shell else command.split(),
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        shell=shell
    ) as process:
        try:
            _stdout, _stderr = process.communicate(timeout=timeout)
            completed_process = CompletedProcess(process.args, process.returncode, _stdout.strip(), _stderr.strip())

        except TimeoutExpired:
            children_processes = psutil.Process(process.pid).children() if kill_children_processes else None
            process.kill()

            if children_processes:
                for _process in children_processes:
                    print(f"Killed children process: {_process.name()}, pid: {_process.pid}") if stdout else None
                    psutil.Process(_process.pid).kill()

            completed_process = CompletedProcess(
                process.args,
                1,
                '',
                f"timeout expired when executing the command: {command}"
            )

        finally:
            print(completed_process.stderr) if stderr and completed_process.stderr else None
            print(completed_process.stdout) if stdout and completed_process.stdout else None
            return completed_process
