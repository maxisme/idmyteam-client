# script to ZIP and upload all images in the classified directory to be trained by ID My Team
import json
import zipfile, requests
from io import BytesIO
from collections import defaultdict
from glob import glob
from settings import functions, config


def allowed():
    """

    :return: message, whether upload is allowed, list of members images
    """
    # get classified images and members
    members = defaultdict(list)
    for member_dir in glob(config.CLASSIFIED_PATH + "[0-9]*"):
        member_id = member_dir.replace(config.CLASSIFIED_PATH, "")
        for image in glob(member_dir + "/*.jpg"):
            members[member_id].append(image)

    valid_members = {}
    for key in members:
        if (
            config.SOCKET_STATUS == config.SOCKET_CONNECTED
            or len(members[key]) >= config.MIN_TRAINING_IMAGES_PER_MEMBER
        ):
            # If first time training team there must be at least MIN_TRAINING_IMAGES_PER_MEMBER
            valid_members[key] = members[key]

    if config.SOCKET_STATUS == config.SOCKET_NOT_TRAINED:
        # for the initial training there must be more than the min_training_images classified
        # for a minimum of two members
        if len(valid_members) < 2:
            return (
                """You must have more than {} training images for each member and a minimum of 2 members 
                to start your teams recognition model!""".format(
                    config.MIN_TRAINING_IMAGES_PER_MEMBER
                ),
                False,
                [],
            )
    elif config.SOCKET_STATUS == config.SOCKET_CLOSED:
        return (
            "You are not connected to the ID My Team Socket. Please try again later!",
            True,
            [],
        )

    return "", True, valid_members


def upload(conn):
    """
    :param conn: database connection
    :return: message, whether it was a successful upload
    """
    message, success, members = allowed()
    if not success:
        return message, success

    # zip images
    file_buff = BytesIO()
    zip = zipfile.ZipFile(file_buff, mode="w")
    for m in members:
        functions.Member.toggle_training(conn, m)
        for image in members[m]:
            zip.write(
                image, image.replace(config.CLASSIFIED_PATH, "/"), zipfile.ZIP_DEFLATED
            )
    zip.close()

    # upload zip of classsified images to idmy.team
    r = requests.post(
        "https://idmy.team/upload",
        files={"ZIP": file_buff.getvalue()},
        data={"username": config.username, "credentials": config.credentials},
    )

    if r.status_code != 200:
        # FAILED TO UPLOAD
        for m in members:
            functions.Member.toggle_training(conn, m, is_training=False)
        message = json.loads(r.reason)
        return message["message"], False
    else:
        return "Uploaded all classification images for training!", True
