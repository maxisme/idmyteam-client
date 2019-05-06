import os
import time

import pytest
from PIL import Image

from settings import functions, config
ROOT_DIR = config.ROOT_DIR
MEMBER_ID = '1'


@pytest.mark.incremental
class TestYAML(object):
    test_path = 'test.yaml'
    dic = {'hello': [{'test': 'foo'}, {'test2': 'baz'}]}

    def test_write_YAML(self):
        print(os.environ)
        functions.YAML.write(self.test_path, self.dic)

    def test_open_YAML(self):
        out_dic = functions.YAML.read(self.test_path)
        assert out_dic['hello'] == self.dic['hellod']

        # clean_up
        os.remove(self.test_path)


class MySQLHelper(object):
    def __init__(self):
        self.conn = functions.connect(config.DB["username"], config.DB["password"], config.DB["db"])
        if not self.conn:
            print('Error with db connection')
            quit()

    def execute_sql_in_file(self, file):
        x = self.conn.cursor()
        sql = open(file, 'r').read()
        x.execute(sql)
        x.close()

    def init_schema(self):
        print(ROOT_DIR + "/db/schema.sql")
        self.execute_sql_in_file(ROOT_DIR + "/db/schema.sql")
            
######################### end #########################

@pytest.mark.parametrize('retry_time,allowed_seconds,expected',[
    (1, 2, False),
    (2, 1, True),
])
def test_limit_recognition(retry_time, allowed_seconds, expected):
    sql_helper = MySQLHelper()
    sql_helper.init_schema()
    sql_helper.execute_sql_in_file(ROOT_DIR + '/db/create_user.sql')

    functions.Member.Activity.recognised(sql_helper.conn, MEMBER_ID, 1, 1)

    time.sleep(retry_time)

    assert functions.Member.allowed_recognition(sql_helper.conn, MEMBER_ID, allowed_seconds) == expected


@pytest.mark.parametrize('message', [
    'hello',
    'a' * 5000,
    '{"hello": "max"}'
])
def test_image_comment(message):
    img_path = 'test_img.jpg'
    img = Image.new('RGB', (1, 1), color='red')
    img.save(img_path)

    functions.Image.Comment.write(img_path, message)
    assert functions.Image.Comment.read(img_path).decode() == message
    os.remove(img_path)


@pytest.mark.rpi
def test_num_files_in_dir():
    assert functions.num_files_in_dir(ROOT_DIR + '/tests/files') == 2


def test_toGB():
    assert functions.to_GB(2147483648) == 2


@pytest.mark.rpi
@pytest.mark.parametrize('shell_str,output', [
    ('dfsdf=sdfs', False),
    ('''#!/bin/bash
    foo='1'
    echo $foo
    ''', True)
])
def test_shell_script(shell_str, output):
    file_name = 'foo'
    functions.Shell.validate(shell_str, file_name)

    assert bool(os.path.isfile(file_name)) == bool(output)

    # clean up
    if os.path.isfile(file_name):
        os.remove(file_name)



