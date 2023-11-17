# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE, getoutput as sb_getoutput, call as sb_call


def get_output(command: str) -> str:
    return sb_getoutput(command)

def call(command: str):
    sb_call(command, shell=True)

def run(command: str) -> "tuple[str, str]":
    popen = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = popen.communicate()
    popen.wait()
    stdout = stdout.strip().decode('utf-8', errors='ignore')
    stderr = stderr.strip().decode('utf-8', errors='ignore')
    popen.stdout.close(), popen.stderr.close()
    return stdout, stderr
