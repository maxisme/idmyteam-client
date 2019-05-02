
try:
    import picamera as pc
    from picamera.array import PiRGBArray
except ModuleNotFoundError:
    # keep a pytest working
    pass

import logging
import multiprocessing
from multiprocessing import Pool

import cv2
import requests
import time

from settings import functions, config

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Camera(object):
    def __init__(self):
        VFLIP = bool(int(config.settings["Camera"]['Flip Vertically']['val']))
        SHUTTER = int(config.settings["Camera"]['Framerate']['val'])
        FRAMERATE = int(config.settings["Camera"]['Shutter Speed']['val'])
        RES = tuple(map(int, config.settings["Camera"]['Resolution']['val'].split(' x ')))

        self.camera = pc.PiCamera()
        self.camera.resolution = RES
        self.camera.vflip = VFLIP
        if FRAMERATE:
            self.camera.framerate = FRAMERATE
        if SHUTTER:
            self.camera.shutter_speed = SHUTTER

        time.sleep(2)

    def getRaw(self):
        return PiRGBArray(self.camera, size=self.camera.resolution)



def classify(img, store_features, secure):
    """
    :param img: img to be uploaded to be recognised
    :param store_features: whether to store the predicted images features for constant learning.
    :param bool secure: whether to use http or https
    :return bool: whether image was uploaded successfully
    """

    start_t = time.time()

    upload_path = functions.random_file_name(config.TMP_DETECTED_DIR, config.IMG_TYPE)

    # write image to file for future handling
    cv2.imwrite(upload_path, img)

    protocol = "https" if secure else "http"
    r = requests.post(protocol + "://idmy.team/upload", files={
        'img_file': open(upload_path, 'rb')
    }, data={
        'username': config.username,
        'credentials': config.credentials,
        'store-features': store_features * 1,
        'file-name': upload_path.replace(config.TMP_DETECTED_DIR, '')
    })

    logging.info('Took %s seconds to upload image', time.time() - start_t)

    if r.status_code != 200:
        # upload is being rate limited
        logging.error(r.reason)
        return False
    return True


process_pool = Pool(processes=4)


def run():
    # check if connected to socket
    if config.SOCKET_STATUS != config.SOCKET_CONNECTED:
        if config.SOCKET_STATUS == config.SOCKET_NOT_TRAINED:
            logging.error("You must train a minimum of two members before starting the recognition system.")
        else:
            logging.critical("Not connected to the ID My Team Socket!")

    # initialise timing logs
    bg_t, write_t = False, False

    # background extractor
    bg_model = functions.Image.BackgroundExtractor.model(int(config.settings["Camera"]['Mask Threshold']['val']))

    # init camera
    cam = Camera()
    raw = cam.getRaw()

    logging.info("Started camera...")

    i = 0
    upload_cnt = 0
    fps_start_time = time.time()
    for frame in cam.camera.capture_continuous(raw, format="bgr", use_video_port=True):
        if config.RESTART_CAMERA:
            logging.info("Restarting camera...")
            cam.camera.close()
            config.RESTART_CAMERA = False
            raw.truncate(0)
            return run()

        if bool(int(config.settings["Camera"]['Run']['val'])):
            SHOW_LIVE = bool(int(config.settings["Camera"]['Live Stream']['val']))
            ONLY_IMAGE = bool(int(config.settings["Camera"]['Silent Mode']['val']))
            SHOW_MASK = bool(int(config.settings["Camera"]['Mask']['val']))
            MASK_THRESH = int(config.settings["Camera"]['Mask Threshold']['val'])
            UPLOAD_CROP = bool(int(config.settings["Recognition"]['Upload Cropped']['val']))
            IS_SECURE = bool(config.settings["Recognition"]["Secure Upload"]["val"])
            MOVEMENT_THRESH = float(config.settings["Recognition"]['Movement Percentage']['val'])
            STORE_FEATURES = bool(config.settings["Training"]["Store Features"]["val"])

            img = frame.array
            has_uploaded = False
            if not ONLY_IMAGE and config.SOCKET_STATUS == config.SOCKET_CONNECTED:
                t = time.time()
                x, y, w, h, mask, diff = functions.Image.BackgroundExtractor.get_movement(
                    img, bg_model, MOVEMENT_THRESH, img.shape[1], img.shape[0], config.BG_IMG_REDUCTION)
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
                        bg_model = functions.Image.BackgroundExtractor.model(MASK_THRESH)
                    else:
                        # this image will be deleted or moved after classification
                        if UPLOAD_CROP:
                            # crop image to area of interest in bg extractor
                            upload_img = img[y:y + h, x:x + w]
                        else:
                            upload_img = img

                        ########
                        # UPLOAD IMAGE FOR CLASSIFICATION
                        ########
                        process_pool.apply(classify, args=(upload_img, STORE_FEATURES, IS_SECURE))
                        has_uploaded = True
                else:
                    upload_cnt = 0

                if SHOW_LIVE:
                    # write image for live stream
                    if SHOW_MASK and mask.any():  # not training and there is a mask
                        # show mask image
                        img = mask

                    # log how much movement and status
                    img_text = "Training BG"
                    if x:
                        if has_uploaded:
                            img_text = "Uploading Image"
                        img_text += " - " + str('%.3f' % round(diff, 3))

                        # log contour
                        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)

                    functions.Image.write_text(img, img_text)

                # delete all expired images
                multiprocessing.Process(
                    target=functions.Image.delete_expired,
                    args=(config.TMP_DETECTED_DIR, int(config.settings["Retract Recognition"]['Time']['val']))
                ).start()

            # write live stream image
            functions.Image.write_stream(img, "tmp_img" + config.IMG_TYPE, config.TMP_IMG_PATH)

            #######################
            # LOG STATS (in memory)
            ######################
            if i % config.LOG_STAT_EVERY == 0:

                # calculate FPS
                FPS = float(1 / ((time.time() - fps_start_time) / config.LOG_STAT_EVERY))
                fps_start_time = time.time()
                config.stats[config.STAT_FPS] = round(FPS, 2)

                if bg_t:
                    config.stats[config.STAT_BG_EXTRACTOR_SPEED] = round(bg_t, 2)

        raw.truncate(0)
        i = i + 1
