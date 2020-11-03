from threading import Lock
import os
import shlex
import tempfile
from shutil import copyfile
from subprocess import Popen, PIPE

import oyaml as oyaml


class YAML:
    def __init__(self, path):
        self._config = self.read(path)
        self._path = path
        self._lock = Lock()

    @classmethod
    def read(cls, file):
        """
        Convert yaml file to dictionary
        :param file:
        :return dictionary:
        """
        with open(file, "r") as f:
            content = oyaml.load(f, oyaml.SafeLoader)
        return content

    @classmethod
    def write(cls, file, config):
        """
        Write dictionary to YAML file
        :param file: path for yaml to be written to
        :param config: dictionary to be written
        :return bool:
        """
        with open(file, "w") as outfile:
            return oyaml.dump(config, outfile, default_flow_style=False)

    def save(self) -> bool:
        with self._lock:
            return self.write(self._path, self._config)

    def get(self, group: str, key: str):
        with self._lock:
            return self._config[group][key]["val"]


class Shell:
    @classmethod
    def run_recognition_script(cls, member_name, score, script_path):
        # run script with arguments
        Popen([script_path, member_name, str(score)])

    @classmethod
    def validate(cls, shell_str, out_file):
        str = shell_str.replace("\r", "")
        tmp_name = cls._write_str_to_tmp_file(str)

        cmd = "shellcheck '{}'".format(tmp_name)

        out, exitcode, _ = cls.run_process(cmd)
        if exitcode == 0:
            # success so copy validated file
            copyfile(tmp_name, out_file)
        os.remove(tmp_name)
        return out

    @classmethod
    def run_process(cls, cmd):
        args = shlex.split(cmd)
        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode
        return out, exitcode, err

    @classmethod
    def _write_str_to_tmp_file(cls, s):
        tmp_file, tmp_name = tempfile.mkstemp()
        os.write(tmp_file, s.encode())
        os.close(tmp_file)
        return tmp_name
