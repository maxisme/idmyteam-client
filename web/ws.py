import json
import logging
import os
import time

import websocket
from idmyteam.structs import WSStruct, ClassificationWSStruct, TrainedWSStruct

from functions import Shell
from idmyteamclient.helpers import Image, get_local_IP
from idmyteamclient.models import Member
from web import settings


def start():
    print("Starting ws...")
    while True:
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            settings.WS_URL,
            on_message=on_message,
            on_error=on_error,
            header={
                "username": settings.yaml.get("Credentials", "Id My Team Username"),
                "credentials": settings.yaml.get(
                    "Credentials", "Id My Team Credentials"
                ),
                "local-ip": get_local_IP(),
            },
        )
        ws.run_forever()
        print(settings.WS_URL)
        time.sleep(5)


def on_error(ws, error):
    print(error)


def on_message(ws, msg):
    # decode msg
    try:
        content = json.loads(msg)
        message = content["message"]
        type = content["type"]
    except:
        logging.error(f"Invalid socket message: {msg}")
        return

    if type == WSStruct.Type.ERROR:
        logging.error("Server error: " + message)
    elif type == WSStruct.Type.TRAINED:
        _handle_train(TrainedWSStruct(**content))
    elif type == WSStruct.Type.DELETE_IMAGE:
        image_path = os.path.join(settings.UNCLASSIFIED_PATH, message)
        os.unlink(image_path)
    elif type == WSStruct.Type.DELETED_MODEL:
        pass  # TODO
    elif type == WSStruct.Type.CLASSIFICATION:
        _handle_classification(ClassificationWSStruct(**content))
    elif type == WSStruct.Type.INVALID_CLASSIFICATION:
        _handle_invalid_classification(message)
    elif type == WSStruct.Type.NO_MODEL:
        settings.SOCKET_STATUS = settings.SOCKET_NO_MODEL
    elif type == WSStruct.Type.HAS_MODEL:
        settings.SOCKET_STATUS = settings.SOCKET_CONNECTED


def _handle_train(trained_struct: TrainedWSStruct):
    if settings.SOCKET_STATUS == settings.SOCKET_NO_MODEL:
        # tell camera thread to restart
        settings.RESTART_CAMERA = True

    for member_id, num_trained in trained_struct.num_trained_classes:
        m = Member.objects.get(id=member_id)
        m.is_training = False
        m.num_trained += num_trained
        m.save()


def _handle_invalid_classification(file_name):
    # TODO need to decide what to do with an invalid image
    # [will be very useful for debugging but will take up a lot of storage space]
    # could potentially have option in settings to store invalid images
    # must at least work with background detector as if this ideally should never happen
    # and if it does the settings on the pi must be wrong and the most likely thing to
    # be wrong is the background detector
    image_path = os.path.join(settings.TMP_CLASSIFIED_PATH, file_name)

    if bool(settings.yaml.get("Recognition", "Training Mode")):
        move_img_path = os.path.join(settings.UNCLASSIFIED_PATH, file_name)
        os.rename(image_path, move_img_path)

    logging.info(f"No face was detected in image: {file_name}")


def _handle_classification(classification: ClassificationWSStruct):
    move_img_path = None
    if 0 < classification.score < settings.yaml.get("Recognition", "Id Threshold"):
        member_name = Member.UNKNOWN_NAME
        move_img_path = os.path.join(
            settings.UNCLASSIFIED_PATH, classification.file_name
        )
    else:
        member_name = Member.objects.get(id=classification.member_id).username
        if bool(settings.yaml.get("Recognition", "Training Mode")):
            move_img_path = os.path.join(
                settings.UNCLASSIFIED_PATH,
                f"{classification.member_id}_{classification.file_name}",
            )

    image_path = os.path.join(settings.TMP_CLASSIFIED_PATH, classification.file_name)
    if not os.path.isfile(image_path):
        return False

    # TODO logging.info the output of the bash script
    Shell.run_recognition_script(
        member_name, classification.score, settings.SCRIPT_PATH
    )

    if move_img_path:
        if classification.coordinates:
            # write coords of face into image file as comment
            Image.Comment.write(image_path, json.dumps(classification.coordinates))

        # move image for manual classification
        os.rename(image_path, move_img_path)
