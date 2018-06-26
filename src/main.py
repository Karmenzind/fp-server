# -*- coding:utf-8 -*-

"""
fp-server
main entry
"""

import os
import sys

from core.context import TornadoContext

# os.environ['PYTHONASYNCIODEBUG'] = '1'


def main():
    """ launch
    """
    context = TornadoContext(setting_module='config')
    context.start()


if __name__ == '__main__':
    src_dir = os.path.dirname(__file__)
    sys.path.insert(0, src_dir)
    main()
