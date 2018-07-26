# -*- coding: utf-8 -*-


def _init_config():
    import os
    import sys
    from utils.docker import check_if_inside_docker
    from utils.tools import parse_yaml, merge_configure
    import pprint

    result = None
    conf_dir = os.path.dirname(__file__)

    inside_docker = check_if_inside_docker()
    internal_path = os.path.join(conf_dir, 'config.yml')

    if os.path.exists(internal_path):
        print("Found internal configure file", internal_path)
        result = parse_yaml(internal_path)

        if not result:
            print("Invalid config file.")
            sys.exit(255)
    else:
        print("Basic file %s not found." % internal_path)
        sys.exit(255)

    if inside_docker:
        print('** YOU ARE INSIDE A DOCKER CONTAINER **')
        ext_path = '/fps_config/config.yml'
    else:
        ext_path = os.path.join(conf_dir, 'config.yml.local')

    if os.path.exists(ext_path):
        print('Found external config file %s' % ext_path)
        ext_conf = parse_yaml(ext_path)
        merge_configure(result, ext_conf)

    print("Got user config:")
    pprint.pprint(result)

    return result


locals().update(_init_config())

#######################################################################
#                           internal config                           #
#######################################################################

# api module
HANDLER_PATHES = ['api']

# whether support cross-domain
# ALLOW_CORS = True

# auto reload
DEBUG = False

# parallel limitations
# None: no limit
# 0   : turn off all
MAX_RUNNING_NUM = {
    'seeker': 7,
    'checker': None,
}

# for checker (testing)
CHECK_TIMEOUT = 20
