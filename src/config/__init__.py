# -*- coding: utf-8 -*-


def _init_config():
    import os
    from utils.docker import check_if_inside_docker
    from utils.tools import parse_yaml, recursive_update
    import pprint

    conf_dir = os.path.dirname(__file__)
    path = os.path.join(conf_dir, 'config.yml')
    result = parse_yaml(path)

    if check_if_inside_docker():
        print('YOU ARE INSIDE A DOCKER CONTAINER')
        ext_path = '/fps_config/config.yml'

        if os.path.exists(ext_path):
            ext_conf = parse_yaml(ext_path)
            recursive_update(result, ext_conf)

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
