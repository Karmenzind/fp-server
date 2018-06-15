# coding: utf-8

import os


def check_if_inside_docker():
    """ check if current env is
    incide a docker container
    :return bool
    """
    result = False
    cgroup_path = '/proc/1/cgroup'

    if os.path.exists(cgroup_path):
        with open(cgroup_path) as _f:
            result = 'docker' in _f.read()

    return result
