# -*- coding: utf-8 -*-


def _init_config():
    import os
    import sys
    from utils.docker import check_if_inside_docker
    from utils.tools import parse_yaml, recursive_update
    import pprint

    result = None
    conf_dir = os.path.dirname(__file__)

    for fname in ('config.yml.local', 'config.yml'):
        path = os.path.join(conf_dir, fname)

        if os.path.exists(path):
            result = parse_yaml(path)
            break

    if check_if_inside_docker():
        print('YOU ARE INSIDE A DOCKER CONTAINER')
        ext_path = '/fps_config/config.yml'

        if os.path.exists(ext_path):
            ext_conf = parse_yaml(ext_path)
            recursive_update(result, ext_conf)

    if not result:
        print("No available config found.")
        sys.exit(255)

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
