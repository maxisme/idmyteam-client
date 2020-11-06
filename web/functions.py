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
        """
        save _config to file self._path
        :return:
        """
        with self._lock:
            return self.write(self._path, self._config)

    def get(self, group: str, setting: str):
        with self._lock:
            return self._config[group][setting]["val"]

    def set(self, group: str, setting: str, val):
        with self._lock:
            self._config[group][setting]["val"] = val

    def get_all(self):
        return self._config


class Shell:
    @classmethod
    def run_recognition_script(cls, member_name: str, score: float, script_path: str):
        # run script with arguments
        Popen([script_path, member_name, str(score)])

    @classmethod
    def validate(cls, shell_str: str, out_file: str):
        str = shell_str.replace("\r", "")
        tmp_file_path = cls._write_str_to_tmp_file(str)

        cmd = f"shellcheck '{tmp_file_path}'"

        out, exitcode, _ = cls.run_process(cmd)
        if exitcode == 0:
            # success so copy validated file
            copyfile(tmp_file_path, out_file)
        os.remove(tmp_file_path)
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
