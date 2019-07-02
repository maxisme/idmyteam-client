import json
import os
import sys
import time

from settings import functions, config
import logging
from tornado import gen
from tornado.websocket import websocket_connect

logging.getLogger("")


class SocketClient(object):
    def __init__(self, url, is_reconnect):
        self.url = url
        self.ws = None
        self.is_reconnect = is_reconnect

    @gen.coroutine
    def connect(self):
        config.SOCKET_STATUS = config.SOCKET_CLOSED
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception as e:
            if not self.is_reconnect:
                logging.error("Socket error: %s", e)
        else:
            config.SOCKET_STATUS = config.SOCKET_CONNECTED
            logging.info("Connected to remote socket.")
            self.run()

    def close(self):
        config.SOCKET_STATUS = config.SOCKET_CLOSED
        self.ws = None
        logging.warning("Socket connection closed")

    @gen.coroutine
    def run(self):
        while config.SOCKET_STATUS != config.SOCKET_CLOSED:
            msg = yield self.ws.read_message()
            if msg is None:
                self.close()
            else:
                # INCOMING MESSAGE
                try:
                    try:
                        message = json.loads(str(msg))
                    except:
                        logging.warning(
                            'Received invalid message from server "%s"', msg
                        )
                        self.close()
                        return

                    if "id" in message:
                        self.ws.write_message(
                            str(message["id"])
                        )  # verify that the message has been received
                        message = message["message"]

                    SCRIPT_PATH = (
                        config.ROOT
                        + config.settings["File Location"]["Bash Script"]["val"]
                    )
                    ID_THRESHOLD = float(
                        config.settings["Recognition"]["Id Threshold"]["val"]
                    )
                    RE_RECOGNITION_RATE = int(
                        config.settings["Recognition"]["Re Recognition"]["val"]
                    )
                    TRAINING_MODE = bool(
                        int(config.settings["Recognition"]["Training Mode"]["val"])
                    )

                    conn = functions.DB.conn(
                        config.DB["username"], config.DB["password"], config.DB["db"]
                    )
                    if message == "ping":
                        self.ws.write_message(
                            "pong"
                        )  # keep connection with server alive

                    elif message == "delete-model":
                        logging.info("Deleted Model!")
                        functions.Member.Activity.purge(conn)
                        self.connect()  # force a reconnect

                    elif message["type"] == "no_model":
                        logging.info("No Team Model")
                        functions.Member.Activity.purge(
                            conn
                        )  # kill any team activity as there shouldn't be any, anyway.
                        config.SOCKET_STATUS = config.SOCKET_NOT_TRAINED

                    elif message["type"] == "invalid_credentials":
                        logging.error("Invalid Id My Team Credentials!")

                        # remove credentials from settings so that user is forced to refill them
                        config.settings["Credentials"]["Id My Team Credentials"][
                            "val"
                        ] = ""
                        functions.YAML.write(config.SETTINGS_FILE, config.settings)

                    elif message["type"] == "classification":
                        # detection
                        coords = message["coords"]
                        recognition_score = float(message["recognition_score"])
                        member_id = int(message["member_id"])

                        if 0 < recognition_score < ID_THRESHOLD:
                            member_id = functions.Member.UNKNOWN_ID
                            name = functions.Member.UNKNOWN_NAME
                        else:
                            name = functions.Member.id_to_name(conn, member_id)

                        file_name = message["file_id"]
                        image_path = config.TMP_DETECTED_DIR + file_name

                        if os.path.isfile(image_path):
                            if name == "INVALID":
                                logging.info("No face was detected in image upload")
                                # TODO need to decide what to do with an invalid image
                                # [will be very useful for debugging but will take up a lot of storage space]
                                # could potentially have option in settings to store invalid images
                                # must at least work with background detector as if this ideally should never happen
                                # and if it does the settings on the pi must be wrong and the most likely thing to
                                # be wrong is the background detector
                                pass
                            else:
                                # run script
                                move_img_path = None
                                t = time.time()

                                # time since file was created
                                recognition_speed = str(
                                    t - os.path.getmtime(image_path)
                                )

                                if name:
                                    if functions.Member.allowed_recognition(
                                        conn, member_id, RE_RECOGNITION_RATE
                                    ):
                                        execution_start = (
                                            time.time()
                                        )  # speed of recognition script
                                        functions.Shell.run_recognition_script(
                                            name, recognition_score, SCRIPT_PATH
                                        )
                                        config.stats[config.STAT_SCRIPT_SPEED] = str(
                                            time.time() - execution_start
                                        )
                                    else:
                                        logging.info("Not allowed to recognise " + name)

                                    if member_id > functions.Member.UNKNOWN_ID:
                                        functions.Member.Activity.recognised(
                                            conn,
                                            member_id,
                                            recognition_score,
                                            recognition_speed,
                                        )
                                        config.stats[config.STAT_RECOGNITION_SPEED] = recognition_speed

                                        if TRAINING_MODE:
                                            # move all classified images to classified page
                                            move_img_path = (
                                                config.UNCLASSIFIED_PATH
                                                + str(member_id)
                                                + "_"
                                                + file_name
                                            )

                                    elif member_id == functions.Member.UNKNOWN_ID:
                                        logging.info("Unknown individual")
                                        move_img_path = (
                                            config.UNCLASSIFIED_PATH + file_name
                                        )

                                if move_img_path:
                                    if coords:
                                        # write coords of face into image file
                                        functions.Image.Comment.write(
                                            image_path, coords
                                        )

                                    # move uploaded image for manual classification
                                    os.rename(image_path, move_img_path)

                    elif message["type"] == "trained":
                        # when a team gets their first model restart the camera and socket
                        if config.SOCKET_STATUS == config.SOCKET_NOT_TRAINED:
                            # tell camera thread to restart
                            config.RESTART_CAMERA = True

                            # close socket to be restarted by periodic callback in web.py
                            self.close()

                        for member in json.loads(message["trained_members"]):
                            member_id = int(member[0])
                            num_trained = int(member[1])

                            functions.Member.Activity.trained(
                                conn, member_id, num_trained
                            )
                            functions.Member.toggle_training(
                                conn, member_id, is_training=False
                            )

                    elif message["type"] == "delete_trained_image":
                        file = config.CLASSIFIED_PATH + message["img_path"]
                        os.unlink(file)

                    elif message["type"] == "error":
                        # log error message
                        logging.warning(message["mess"])

                except Exception as e:
                    error_str = (
                        "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                        type(e).__name__,
                        e,
                    )
                    logging.error("%s msg: %s", error_str, msg)
