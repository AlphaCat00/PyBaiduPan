import argparse
import json
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(description=' a Python client for Baidu Pan.', formatter_class=RawTextHelpFormatter)
parser.add_argument('action', choices=['list', 'download', 'upload', 'sync', 'logout'], metavar='action',
                    default='list', nargs='?',
                    help='available actions: list, download, upload, sync, logout. (default: "list")\n\
list\t\tlist files and directories in the pan_path.\n\
download\tdownload all files and directories in the pan_path to local_path.\n\
upload\t\tupload all files and directories in the local_path to pan_path.\n\
sync\t\tlocal_path and pan_path sync to each other.\n\
logout\t\tdelete all credentials.\n')
parser.add_argument('pan_path', help='absolute path in Baidu Pan, which can be file or directory.', nargs='?')
parser.add_argument('local_path', help='local path, which can be file or directory.', nargs='?')
parser.add_argument('-p', '--local-path', help='an alias of local_path. (default: ".")', type=str)
parser.add_argument('-b', '--pan-path', help='an alias of pan_path. (default: "/")', type=str)
parser.add_argument('-c', '--conf', help='the path of config file.', default='config.json')
parser.add_argument('-s', '--session', help='the path to save session information.', type=str)
parser.add_argument('-u', '--username', help='baidu username, only needed once for authorization.', type=str)
parser.add_argument('-P', '--password', help="baidu password, only needed once for authorization. \
Warning: for security reason, don't save this in config file.", type=str)
parser.add_argument('-a', '--app-id', help='baidu app id. recommended IDs: 498065, 309847, 778750, 250528(official), \
265486, 266719. Some of them can bypass 50M download limitation.', type=int)
parser.add_argument('-o', '--overwrite', choices=['none', 'mtime', 'force'], default='none', help="none\tnever \
overwrite\nmtime\toverwrite when a newer version of file(base on last modify time) is found.\nforce\talways overwrite.")
parser.add_argument('-l', '--log-file', help='specify where to save log.', type=str)
parser.add_argument('-d', '--delete-extra', action='store_true', help='delete all extra files and directories in dst_\
path. do NOT use this option unless you know exactly what you are doing. ')

DEFAULT_CONFIG = {'session': "~/.BdPan/session.pkl", 'username': '', 'password': '', 'app_id': 778750,
                  'local_path': '.', 'pan_path': '/', "overwrite": False, 'log_file': '', "delete_extra": False}


def get_config():
    config = DEFAULT_CONFIG
    args = parser.parse_args()
    conf_f = {}
    try:
        with open(args.conf) as f:
            conf_f = json.load(f)
    except FileNotFoundError:
        pass

    for i in (conf_f.items(), vars(args).items()):
        for k, v in i:
            if v:
                config[k] = v
    return config


if __name__ == '__main__':
    print(get_config())
