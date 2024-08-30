# coding: utf-8

import logging
import os
import shlex
import subprocess


lg = logging.getLogger('tako.cmd')
result_lg = logging.getLogger('tako.cmd')


def run_cmd(cmd: list|str, shlex_reformat=False, shell=False, inherit_env=False, **kwargs):
    if shlex_reformat and shell:
        raise ValueError('shlex_reformat and shell are mutually exclusive')

    if shell:
        if not isinstance(cmd, str):
            raise ValueError('cmd must be str when shell=True')
        kwargs['shell'] = shell

    # reformat cmd
    if shlex_reformat:
        if isinstance(cmd, list):
            cmd_str = ' '.join(cmd)
        else:
            cmd_str = cmd
        cmd = shlex.split(cmd_str)

    lg.debug('cmd: %s, %s', cmd, kwargs)

    if inherit_env:
        env = os.environ.copy()
        env.update(kwargs.pop('env', {}))
        kwargs['env'] = env

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    out, err = p.communicate()
    out, err = out.decode(), err.decode()

    result_lg.debug('cmd=%s returncode=%s out=%s err=%s', cmd, p.returncode, out, err)
    return p.returncode, out, err
