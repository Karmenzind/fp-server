import time


def current_timestamp(_int=True):
    res = time.time()
    if _int:
        res = int(res)
    return res
