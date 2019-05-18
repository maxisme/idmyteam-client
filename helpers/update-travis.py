import functions

CONFIG_PATH = "/conf/test_local.yaml"
s = functions.YAML.read(".." + CONFIG_PATH)
content = open("../.travis-edit.yml", "r").read()
content = content.replace("DB_NAME", s["Credentials"]["Database Name"]["val"])
content = content.replace("DB_USER", s["Credentials"]["Database Username"]["val"])
content = content.replace("DB_PASS", s["Credentials"]["Database Password"]["val"])
content = content.replace("CONFIG_PATH", CONFIG_PATH)


f = open("../.travis.yml", "w")
f.write(content)
f.close()
