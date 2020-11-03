import datetime

from idmyteamclient.helpers import random_file_name, Image
from web import settings

try:
    import picamera as pc
    from picamera.array import PiRGBArray
except ModuleNotFoundError:
    pass  # for tests

import logging
import multiprocessing
from multiprocessing import Pool

import cv2
import requests
import time


class Camera(object):
    def __init__(self):
        self.camera = pc.PiCamera()
        self.camera.resolution = tuple(
            map(int, settings.yaml["Camera"]["Resolution"]["val"].split(" x "))
        )
        self.camera.vflip = bool(int(settings.yaml["Camera"]["Flip Vertically"]["val"]))

        framerate = int(settings.yaml["Camera"]["Shutter Speed"]["val"])
        if framerate:
            self.camera.framerate = framerate
        shutter = int(settings.yaml["Camera"]["Framerate"]["val"])
        if shutter:
            self.camera.shutter_speed = shutter

    def getRaw(self):
        return PiRGBArray(self.camera, size=self.camera.resolution)


async def classify(img, should_store_features: bool, is_secure: bool):
    """
    :param img: img to be uploaded to be recognised
    :param bool should_store_features: whether to store the predicted images features for constant learning.
    :param bool is_secure: whether to use http or https
    :return bool: whether image was uploaded successfully
    """
    upload_path = random_file_name(settings.TMP_CLASSIFIED_PATH, settings.IMG_TYPE)

    # write image to file for future handling
    cv2.imwrite(upload_path, img)

    protocol = "https" if is_secure else "http"
    with open(upload_path, "rb") as file:
        r = requests.post(
            protocol + "://idmy.team/upload",
            files={"file": file},
            data={
                "username": settings.yaml["Credentials"]["Id My Team Username"]["val"],
                "credentials": settings.yaml["Credentials"]["Id My Team Credentials"][
                    "val"
                ],
                "store-features": should_store_features * 1,
                "file-name": upload_path.replace(settings.TMP_CLASSIFIED_PATH, ""),
            },
        )

    if r.status_code != 200:
        logging.error(r.reason)
        return False
    return True


process_pool = Pool()


async def run():

    # background extractor
    bg_model = Image.BackgroundExtractor.model(
        int(settings.yaml.get("Camera", "Mask Threshold"))
    )

    # init camera
    cam = Camera()
    raw = cam.getRaw()

    logging.info("Started camera...")

    i = 0
    upload_cnt = 0
    fps_start_time = time.time()
    for frame in cam.camera.capture_continuous(raw, format="bgr", use_video_port=True):
        if settings.RESTART_CAMERA:
            logging.info("Restarting camera...")
            cam.camera.close()
            config.RESTART_CAMERA = False
            raw.truncate(0)
            return run()

        if bool(int(config.yaml["Camera"]["Run"]["val"])):
            SHOW_LIVE = bool(int(config.yaml["Camera"]["Live Stream"]["val"]))
            ONLY_IMAGE = bool(int(config.yaml["Camera"]["Silent Mode"]["val"]))
            SHOW_MASK = bool(int(config.yaml["Camera"]["Mask"]["val"]))
            MASK_THRESH = int(config.yaml["Camera"]["Mask Threshold"]["val"])
            UPLOAD_CROP = bool(int(config.yaml["Recognition"]["Upload Cropped"]["val"]))
            IS_SECURE = bool(config.yaml["Recognition"]["Secure Upload"]["val"])
            MOVEMENT_THRESH = float(
                config.yaml["Recognition"]["Movement Percentage"]["val"]
            )
            STORE_FEATURES = bool(config.yaml["Training"]["Store Features"]["val"])

            img = frame.array
            has_uploaded = False
            if not ONLY_IMAGE and config.SOCKET_STATUS == config.SOCKET_CONNECTED:
                t = time.time()
                (
                    x,
                    y,
                    w,
                    h,
                    mask,
                    diff,
                ) = functions.Image.BackgroundExtractor.get_movement(
                    img,
                    bg_model,
                    MOVEMENT_THRESH,
                    img.shape[1],
                    img.shape[0],
                    config.BG_IMG_REDUCTION,
                )
                bg_t = time.time() - t

                if diff > config.MAJOR_BG_CHANGE_THRESH:
                    # restart training if bg diff too large
                    i = 0
                    bg_model = functions.Image.BackgroundExtractor.model(MASK_THRESH)

                if x and diff > float(MOVEMENT_THRESH):
                    ##################################
                    # movement in image above thresh #
                    ##################################

                    # if too many consistent uploads retrain bg
                    upload_cnt = upload_cnt + 1
                    if upload_cnt > config.UPLOAD_RETRY_LIMIT:
                        i = 0
                        upload_cnt = 0
                        bg_model = functions.Image.BackgroundExtractor.model(
                            MASK_THRESH
                        )
                    else:
                        # this image will be deleted or moved after classification
                        if UPLOAD_CROP:
                            # crop image to area of interest in bg extractor
                            upload_img = img[y : y + h, x : x + w]
                        else:
                            upload_img = img

                        ########
                        # UPLOAD IMAGE FOR CLASSIFICATION
                        ########
                        process_pool.apply(
                            classify, args=(upload_img, STORE_FEATURES, IS_SECURE)
                        )
                        has_uploaded = True
                else:
                    upload_cnt = 0

                if SHOW_LIVE:
                    # write image for live stream
                    if SHOW_MASK and mask.any():  # not training and there is a mask
                        # show mask image
                        img = mask

                    # log how much movement and status
                    img_text = "...."
                    img_text = img_text[: (i % 4)]
                    if x:
                        if has_uploaded:
                            img_text = "Uploading Image"
                        img_text += " - " + str("%.3f" % round(diff, 3))

                        # log contour
                        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)

                    functions.Image.write_text(img, img_text)

                if has_uploaded:
                    now = datetime.datetime.now()
                    time_str = (
                        str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
                    )
                    if time_str not in config.CAPTURE_LOG:
                        config.CAPTURE_LOG[time_str] = 1
                    else:
                        config.CAPTURE_LOG[time_str] += 1

                # delete all expired images
                multiprocessing.Process(
                    target=functions.Image.delete_expired,
                    args=(
                        config.TMP_DETECTED_DIR,
                        int(config.yaml["Retract Recognition"]["Time"]["val"]),
                    ),
                ).start()

            # write live stream image
            functions.Image.write_stream(
                img, "tmp_img" + config.IMG_TYPE, config.TMP_IMG_PATH
            )

            #######################
            # LOG STATS (in memory)
            ######################
            if i % config.LOG_STAT_EVERY == 0:

                # calculate FPS
                FPS = float(
                    1 / ((time.time() - fps_start_time) / config.LOG_STAT_EVERY)
                )
                fps_start_time = time.time()
                config.stats[config.STAT_FPS] = round(FPS, 2)

                if bg_t:
                    config.stats[config.STAT_BG_EXTRACTOR_SPEED] = round(bg_t, 2)

        raw.truncate(0)
        i = i + 1
