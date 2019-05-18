import re

from settings import functions, config

TABLE = "idmyteam"
conn = functions.DB.conn(config.DB["username"], config.DB["password"], config.DB["db"])

x = conn.cursor()
x.execute(
    "SELECT table_name FROM information_schema.tables where table_schema='idmyteam';"
)
results = x.fetchall()
x.close()


x = conn.cursor()
schema = "SET FOREIGN_KEY_CHECKS=0;"
for result in results:
    x.execute("show create table " + result[0])
    schema += (
        "DROP TABLE IF EXISTS `" + result[0] + "`;\n" + x.fetchall()[0][1] + "; \n"
    )
schema += "SET FOREIGN_KEY_CHECKS=1;"

schema = re.sub(r"AUTO_INCREMENT=\d+", "", schema)  # remove AUTO_INCREMENT
print(schema)
