# -*- coding:utf-8 -*-


import uuid

import yaml


def get_uuid1():
    """ make a UUID based on the host ID and current time
    """
    s = uuid.uuid1()

    return str(s)


def get_uuid3(str_in):
    """ make a UUID using an MD5 hash of a namespace UUID and a name
    @param str_in 输入字符串
    """
    s = uuid.uuid3(uuid.NAMESPACE_DNS, str_in)

    return str(s)


def get_uuid4():
    """ make a random UUID
    """
    s = uuid.uuid4()

    return str(s)


def get_uuid5(str_in):
    """ make a UUID using a SHA-1 hash of a namespace UUID and a name
    @param str_in 输入字符串
    """
    s = uuid.uuid5(uuid.NAMESPACE_DNS, str_in)

    return str(s)


def parse_yaml(path):
    with open(path) as f:
        return yaml.load(f)


def recursive_update(old, new):
    """
    :old: to be updated
    :new:
    """

    for key, value in new.items():
        if key in old:
            old_value = old[key]
            # if type(old_value) != type(value):
            #     raise AssertionError("New value's type must"
            #                          "be the same as the old's")

            if isinstance(value, dict):
                old[key].update(value)
            elif isinstance(value, list):
                old[key] = old_value + value
            elif isinstance(value, tuple):
                old[key] = tuple(list(old_value) + list(value))
            else:
                old[key] = value
        else:
            old[key] = value


def str_rot13(txt):
    rot13 = str.maketrans(
        "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
        "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"
    )

    return str.translate(txt, rot13)
