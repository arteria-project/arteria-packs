#!/usr/bin/python

import os
import json
import sys

path_to_search = sys.argv[1]
directory_list = [ name for name in os.listdir(path_to_search) if os.path.isdir(os.path.join(path_to_search, name)) ]

print(json.dumps(directory_list))
