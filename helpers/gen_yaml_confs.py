import os

import functions
import collections


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


template = functions.YAML.read("../conf/template.yaml")
overide_dir = "../conf/overide/"
for filename in os.listdir(overide_dir):
    t_yaml = functions.YAML.read(overide_dir + filename)
    new_yaml = update(template, t_yaml)

    functions.YAML.write("../conf/" + filename, new_yaml)
