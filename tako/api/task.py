import shlex
import sys
from pathlib import Path

from ..settings import Env
from ..utils.cmd import run_cmd


script_dir = Path(Env.SCRIPTS_DIR)


class ScriptRunResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.result = (returncode, stdout, stderr)


def task_runner(script_name, script_args: str|None =None):
    script_path = script_dir / script_name
    cmd = [
        sys.executable,
        '-u',
        script_path,
    ]
    if script_args:
        cmd.extend(shlex.split(script_args))

    rc, out, err = run_cmd(cmd, shell=False)
    return ScriptRunResult(rc, out, err)
