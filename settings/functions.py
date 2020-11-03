# common functions used in multiple scripts
import datetime
import json
import logging
import shlex
import shutil
import socket
import tempfile
from shutil import copyfile

import re
import oyaml
import os
import zmq
from subprocess import Popen, PIPE
import MySQLdb
import tornado.escape
import bcrypt


class YAML:
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


def create_local_socket(port, pull=False):
    # TODO handle case where the port is not open and sends hang
    context = zmq.Context()
    if pull:
        # for receiving socket messages
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://127.0.0.1:%d" % port)
    else:
        # for sending socket messages
        socket = context.socket(zmq.PUSH)
        socket.connect("tcp://127.0.0.1:%d" % port)
    socket.setsockopt(zmq.LINGER, 0)
    return socket, context


def num_files_in_dir(dir):
    return sum([len(files) for r, d, files in os.walk(dir)])


class DB:
    @classmethod
    def conn(cls, u, p, db):
        p = "" if p is None else p
        return MySQLdb.connect(host="127.0.0.1", user=u, passwd=p, db=db)

    @classmethod
    def execute_sql_in_file(cls, conn, file):
        x = conn.cursor()
        if not os.path.isfile(file):
            raise Exception("No such file %s", file)
        sql = open(file, "r").read()
        try:
            x.execute(sql)
        except Exception:
            print(sql)
        finally:
            x.close()


def path_in_dir(path, dir):
    return path[: len(dir)] == dir


def get_local_IP():
    """
    :return: local IP (192.168...) of raspberry pi on network
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip


def incorrect_classification(conn, ws, capture_time, tmp_dir, unclassified_dir):
    # remove all DB activity stats in interval
    x = conn.cursor()
    try:
        x.execute(
            "DELETE FROM `Activity` WHERE `time` >= NOW() - interval %s second",
            capture_time,
        )
        conn.commit()
    except MySQLdb.Error as e:
        logging.warning("Unable to TRUNCATE activity %s", e)
        conn.rollback()
        return False

    # move all images taken in the time frame to be manually classified
    shutil.copytree(tmp_dir, unclassified_dir)
    logging.info("Removed")

    # send message to server to delete 'incremental learning' data
    ws.send({"purge_seconds": capture_time})


def escape(dict):
    return tornado.escape.url_escape(json.dumps(dict))


def unescape(str):
    if str:
        return json.loads(tornado.escape.url_unescape(str))
    return {}


def to_GB(val):
    return round(float(float(float(val / 1024) / 1024) / 1024), 2)


def get_cpu_temp():
    # write cpu temperature
    cmd = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
    return re.search(r"\d+\.\d+", cmd).group(0)  # extract only the number from cmd


class Member:
    UNKNOWN_NAME = "UNKNOWN"
    UNKNOWN_ID = 0
    INVALID_NAME = "INVALID"
    INVALID_ID = -1

    @classmethod
    def get_all(cls, conn):
        x = conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            x.execute(
                "SELECT * FROM Members where id != 1"
            )  # all members apart from root
            return x.fetchall()
        except Exception as e:
            logging.error("Unable to get all members %s", e)
            return None

    @classmethod
    def get_by_name(cls, conn, name):
        x = conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            x.execute("SELECT * FROM Members WHERE name = %s", (name,))
            return x.fetchall()[0]
        except Exception as e:
            logging.error("Unable to get name %s %s", (name, str(e)))
            return None

    @classmethod
    def get_by_member_id(cls, conn, id):
        x = conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            x.execute("SELECT * FROM Members WHERE id = %s", (id,))
            return x.fetchall()[0]
        except Exception:
            return None

    @classmethod
    def add(cls, conn, name, password, perm):
        password = cls._hash_password(password)

        x = conn.cursor()
        try:
            x.execute(
                "INSERT INTO `Members` (name, password, perm) VALUES (%s, %s, %s);",
                (name.title(), password, perm),
            )
            conn.commit()
        except MySQLdb.Error as e:
            logging.error("Couldn't sign up: " + str(e))
            conn.rollback()
            return False
        finally:
            x.close()
        return x.lastrowid

    @classmethod
    def login(cls, user, password):
        user_password = user.pop("password", None)
        return cls._check_password_hash(password, user_password)

    @classmethod
    def _hash_password(cls, s):
        return bcrypt.hashpw(str.encode(s), bcrypt.gensalt()).decode("utf-8")

    @classmethod
    def _check_password_hash(cls, s, h):
        """
        :param s: string to compare with a hash
        :param h: a hash
        :return: matching
        """
        return str.encode(h) == bcrypt.hashpw(str.encode(s), str.encode(h))

    @classmethod
    def remove(cls, conn, member_id, classified_dir):
        x = conn.cursor()
        try:
            x.execute("DELETE FROM `Members` WHERE id = %s", (member_id,))
            conn.commit()
        except MySQLdb.Error as e:
            logging.error("Couldn't delete member: " + str(e))
            conn.rollback()
            return False
        finally:
            x.close()

        # remove all classified images
        try:
            shutil.rmtree(classified_dir + member_id + "/")
        except FileNotFoundError as e:
            logging.warning(e)

    @classmethod
    def set_permission(cls, conn, member_id, perm):
        x = conn.cursor()
        try:
            x.execute("UPDATE `Members` SET perm = %s WHERE id = %s", (perm, member_id))
            conn.commit()
        except MySQLdb.Error as e:
            logging.error("Couldn't set member permission: " + str(e))
            conn.rollback()
            return False
        finally:
            x.close()
        return True

    @classmethod
    def set_pw(cls, conn, member_id, password):
        password = cls._hash_password(password)
        x = conn.cursor()
        try:
            x.execute(
                "UPDATE `Members` SET password = %s WHERE id = %s",
                (password, member_id),
            )
            conn.commit()
        except MySQLdb.Error as e:
            logging.error("Couldn't set member password: " + str(e))
            conn.rollback()
            return False
        finally:
            x.close()
        return True

    @classmethod
    def get_num_trained(cls, conn, member_id):
        x = conn.cursor()
        try:
            x.execute(
                """SELECT num FROM Activity 
            WHERE member_id = %s 
            AND type = 'TRAINED' 
            ORDER BY id DESC LIMIT 1""",
                (member_id,),
            )
            return x.fetchall()[0][0]
        except Exception:
            return 0

    @classmethod
    def get_activity(cls, conn, member_id):
        x = conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            x.execute(
                """SELECT `score`, `type`
            FROM Activity 
            WHERE `member_id` = %s""",
                (member_id,),
            )
            return x.fetchall()
        except Exception as e:
            logging.error("Unable to get recognition score %s", e)
            return None

    @classmethod
    def id_to_name(cls, conn, member_id):
        if int(member_id) == cls.INVALID_ID:
            return cls.INVALID_NAME
        elif int(member_id) == cls.UNKNOWN_ID:
            return cls.UNKNOWN_NAME
        else:
            x = conn.cursor()
            x.execute("SELECT `name` FROM `Members` WHERE `id` = %s", (member_id,))
            try:
                return x.fetchall()[0][0]
            except:
                return cls.UNKNOWN_NAME

    @classmethod
    def name_to_id(cls, conn, name):
        if name == cls.INVALID_NAME:
            return cls.INVALID_ID
        elif name == cls.UNKNOWN_NAME:
            return cls.UNKNOWN_ID
        else:
            x = conn.cursor()
            x.execute("SELECT `id` FROM `Members` WHERE `name` = %s", (name,))
            try:
                return x.fetchall()[0][0]
            except:
                return cls.UNKNOWN_ID

    @classmethod
    def allowed_recognition(cls, conn, member_id, allowed_seconds):
        """
        If allowed to recognise the individual due to it being out of the re recognition rate
        :param conn: database connection
        :param member_id: the member that has been recognised by ID My Team
        :param int allowed_seconds: the number of seconds (specified by user) before the
        user should be allowed to be recognised again
        :return bool:
        """
        if member_id == cls.UNKNOWN_ID:
            return True
        elif member_id == cls.INVALID_ID:
            return False

        # CHECK IF RECOGNITION HAS OCCURRED AGAIN WITHIN `allowed_seconds`
        x = conn.cursor()
        x.execute(
            "SELECT `time` FROM `Activity` WHERE `member_id` = %s ORDER BY `id` DESC LIMIT 1",
            (member_id,),
        )

        try:
            last_recognised_time = x.fetchall()[0][0]
        except:
            # exception when member has never been recognised before
            return True

        recognition_grace = last_recognised_time + datetime.timedelta(
            0, allowed_seconds
        )

        if datetime.datetime.now() > recognition_grace:
            return True
        return False

    @classmethod
    def toggle_training(cls, conn, member_id, is_training=True):
        """
        Mark a member as being training or not
        :param conn: database connection
        :param member_id: a team members ID
        :param bool is_training: whether the member is being trained or not
        :return:
        """
        x = conn.cursor()
        try:
            x.execute(
                "UPDATE `Members` SET training = %s WHERE id = %s",
                (is_training * 1, member_id),
            )
            conn.commit()
        except MySQLdb.Error as e:
            logging.error("Unable to write member as trained into DB " + str(e))
            conn.rollback()
        finally:
            x.close()

    class Activity:
        @classmethod
        def trained(cls, conn, member_id, num):
            """
            Log the number of times a member has been trained
            :param conn: database connection
            :param member_id:
            :param num:
            :return:
            """
            x = conn.cursor()
            try:
                x.execute(
                    "INSERT INTO `Activity` (`member_id`, `type`, `num`) VALUES (%s, 'TRAINED', %s)",
                    (member_id, num),
                )
                conn.commit()
            except MySQLdb.Error as e:
                logging.error("Unable to write TRAINED into DB " + str(e))
                conn.rollback()
            finally:
                x.close()

        @classmethod
        def recognised(cls, conn, member_id, score, process_speed):
            x = conn.cursor()
            try:
                x.execute(
                    """INSERT INTO `Activity` (`member_id`, `type`, `score`, `speed`)
                    VALUES (%s, 'RECOGNISED', %s, %s)""",
                    (member_id, score, process_speed),
                )
                conn.commit()
            except MySQLdb.Error as e:
                logging.error("Unable to write RECOGNISED into DB " + str(e))
                conn.rollback()
            finally:
                x.close()

        @classmethod
        def purge(cls, conn):
            """
            Delete all activity from database
            :param conn: database connection
            """
            x = conn.cursor()
            try:
                x.execute("TRUNCATE TABLE `Activity`")
                conn.commit()
            except MySQLdb.Error as e:
                logging.error("Unable to TRUNCATE activity " + str(e))
                conn.rollback()
            finally:
                x.close()

            cls._stop_team_training(conn)

        @classmethod
        def _stop_team_training(cls, conn):
            """
            Set all members as not training anymore.
            :param conn: database connection
            """
            x = conn.cursor()
            try:
                x.execute("UPDATE `Members` SET `training` = 0")
                conn.commit()
            except MySQLdb.Error as e:
                logging.error("Unable to _stop_team_training DB" + str(e))
                conn.rollback()
            finally:
                x.close()


class Logs:
    @classmethod
    def get_logs(cls, conn, page, page_size, level):
        """
        :param page: which page
        :param page_size: how many logs per page
        :param level: min warning level (i.e 'info', 'warn', etc...)
        :return: database logs
        """
        x = conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            x.execute(
                """SELECT *
            FROM Logs
            WHERE level >= %s
            ORDER BY `id` DESC
            LIMIT %s, %s""",
                (level, (page - 1) * page_size, page_size),
            )
            return x.fetchall()
        except Exception as e:
            logging.error("Unable to fetch logs %s", e)
            return None

    @classmethod
    def purge(cls, conn):
        x = conn.cursor()
        x.execute("TRUNCATE `Logs`")


class Shell:
    @classmethod
    def run_recognition_script(cls, name, score, script_path):
        # run script with arguments
        Popen([script_path, name, str(score)])

    @classmethod
    def validate(cls, shell_str, out_file):
        str = shell_str.replace("\r", "")
        tmp_name = cls._write_str_to_tmp_file(str)

        cmd = "shellcheck '{}'".format(tmp_name)

        out, exitcode, _ = cls.run_process(cmd)
        if exitcode == 0:
            # success so copy validated file
            copyfile(tmp_name, out_file)
        else:
            logging.error(out)
            print(out)
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
        os.write(tmp_file, str.encode(s))
        os.close(tmp_file)
        return tmp_name
