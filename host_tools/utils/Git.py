# -*- coding: utf-8 -*-
import Shell


def clone(repo: str, branch: str = None, path: str = None) -> None:
    branch = f"{('-b ' + branch + ' ') if branch else ''}"
    Shell.call(f"git clone {branch}{repo} {path or ''}".strip())
