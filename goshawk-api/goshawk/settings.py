from goshawk.defaults import *

import sys, os
__conf_dir = os.path.abspath(os.environ['GOSHAWK_CONF_DIR'])

if not os.path.isdir(__conf_dir):
    print("Path does not exists: {}".format(__conf_dir))
    sys.exit(1)

__config_file = os.path.join(__conf_dir, 'goshawk.conf.py')
if not os.path.isfile(__config_file):
    print("Configuration does not exists: {}".format(__config_file))
    sys.exit(1)

# sys.path.insert(0, __conf_dir)

__config = None
with open(__config_file, 'r') as f:
    __config = f.read()

exec(__config)

