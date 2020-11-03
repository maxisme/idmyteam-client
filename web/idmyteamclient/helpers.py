import base64
import datetime
import os
import re
import socket
from collections import OrderedDict
from glob import glob
from random import randint

import cv2
from PIL import Image

from functions import Shell
from idmyteamclient.models import Member
from idmyteamclient.structs import ClassifiedImage
from web import settings


def update_global_stats():
    # storage
    st = os.statvfs("/")
    total_storage = to_GB(st.f_bsize * st.f_blocks)
    storage_left = to_GB(st.f_bavail * st.f_frsize)
    settings.stats[settings.STAT_STORAGE] = (
        str(storage_left) + "/" + str(total_storage) + " GB"
    )

    # number of classified
    settings.stats[settings.STAT_NUM_CLASSIFIED] = num_files_in_dir(
        os.path.join(
            settings.BASE_DIR,
            settings.yaml["File Location"]["Classified Images"]["val"],
        )
    )

    # number of unclassified
    settings.stats[settings.STAT_NUM_UNCLASSIFIED] = num_files_in_dir(
        os.path.join(
            settings.BASE_DIR,
            settings.yaml["File Location"]["Unclassified Images"]["val"],
        )
    )

    settings.stats[settings.STAT_CPU_TEMP] = get_cpu_temp()


def to_GB(val):
    return round(float(float(float(val / 1024) / 1024) / 1024), 2)


def get_cpu_temp():
    # write cpu temperature
    cmd = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
    if cmd:
        return re.search(r"\d+\.\d+", cmd).group(0)  # extract only the number from cmd
    return "N/A"


def num_files_in_dir(dir):
    return sum([len(files) for r, d, files in os.walk(dir)])


class Image:
    @classmethod
    def write_stream(cls, img, tmp, live):
        """
        Write img that can be read safely
        :param img: image data to be written
        :param tmp: temporary file to be written
        :param live: output file that is being read
        :return:
        """
        cv2.imwrite(tmp, img)  # ~0.038 seconds - even after overclocking SD
        os.rename(tmp, live)  # does not impact write speed

    @classmethod
    def write_text(cls, img, text):
        cv2.putText(img, text, (0, 30), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (255, 255, 255))

    class Comment:
        @classmethod
        def write(cls, img_path, comment):
            cmd = "convert '{img_path}' -set comment '{comment}' '{img_path}'".format(
                img_path=img_path, comment=comment
            )
            out, _, _ = Shell.run_process(cmd)
            return out

        @classmethod
        def read(cls, img_path):
            return Image.open(img_path).app["COM"]

    class BackgroundExtractor:
        INITIAL_RESIZE = 1.0

        @classmethod
        def get_movement(
            cls, img, fgbg, diff_threshold, img_w, img_h, resize_prop=INITIAL_RESIZE
        ):
            """
            get border contour around movement area from an image
            :param array img:
            :param class fgbg: foreground background image model
            :param float diff_threshold: amount of movement for the model to pay attention to
            :param int img_w: img width
            :param int img_h: img height
            :param float resize_prop: proportion to resize image to
            :return x, y, w, h contour of movement (max area to fit mask) and the mask
            """

            x, y, w, h = 0, 0, 0, 0

            num_img_pixels = float(img_w * img_h) * resize_prop

            if resize_prop != cls.INITIAL_RESIZE:
                img = cv2.resize(
                    img, (int(img_w * resize_prop), int(img_h * resize_prop))
                )

            mask = ret_mask = fgbg.apply(
                img, 0
            )  # apply background extractor model without training

            if resize_prop != cls.INITIAL_RESIZE:
                ret_mask = cv2.resize(mask, (img_w, img_h))  # mask to return

            # check the amount of change in the image
            num_changed_pixels = float(np.count_nonzero(mask))
            image_diff = (
                100 - ((num_img_pixels - num_changed_pixels) / num_img_pixels) * 100
            )

            if image_diff > float(diff_threshold):
                # Acquire contours from the background extractor
                # https://docs.opencv.org/4.0.0/d4/d73/tutorial_py_contours_begin.html
                # https://docs.opencv.org/4.0.0/d9/d8b/tutorial_py_contours_hierarchy.html
                cnts, _ = cv2.findContours(
                    mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                # get the single largest contour rectangle
                largest_contour = 0
                for c in cnts:
                    ca = cv2.contourArea(c)
                    if ca > largest_contour:
                        largest_contour = ca
                        (x, y, w, h) = cv2.boundingRect(c)

                if largest_contour:
                    x = int(x / resize_prop)
                    y = int(y / resize_prop)
                    w = int(w / resize_prop)
                    h = int(h / resize_prop)
            else:
                # train model from smaller background changes
                fgbg.apply(img, -1)

            return x, y, w, h, ret_mask, float(image_diff)

        @classmethod
        def model(cls, mask_thresh):
            return cv2.createBackgroundSubtractorMOG2(
                history=1000, varThreshold=mask_thresh, detectShadows=False
            )
            # return cv2.bgsegm.createBackgroundSubtractorCNT(useHistory=False)

    @classmethod
    def delete_expired(cls, dir, capture_time):
        for f in os.listdir(dir):
            file = os.path.join(dir, f)
            if os.path.isfile(file):
                try:
                    end_time = datetime.datetime.fromtimestamp(
                        os.stat(file).st_mtime
                    ) + datetime.timedelta(0, capture_time)
                    if end_time < datetime.datetime.now():
                        os.unlink(file)  # delete file
                except:
                    if file:
                        os.unlink(file)  # delete file

    @classmethod
    def base_64_html_src(cls, file_path):
        with open(file_path, "r") as file:
            return "data:image/jpeg; base64," + base64.b64encode(file).decode("utf-8")

    @classmethod
    def get_stored_images(
        cls,
        face_coordinates: dict,
        page=None,
        page_size=None,
        classifying=False,
        img_paths=False,
    ) -> OrderedDict:
        """
        :param dict face_coordinates:
        :param int page_size: max number of images to return on a page
        :param int page: the page to return
        :param bool classifying: whether to also select classified images
        :param list img_paths: optional selected file paths
        :return:
        """
        if not img_paths:
            # file paths
            img_paths = glob(settings.UNCLASSIFIED_PATH + "*" + settings.IMG_TYPE)
            if not classifying:
                img_paths.extend(
                    glob(settings.CLASSIFIED_PATH + "*" + settings.IMG_TYPE)
                )

        # sort image paths by creation date TODO measure the performance of this
        img_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # crop image paths to page
        if page_size and page:
            img_paths = img_paths[page_size * (page - 1) : page_size * page]

        images = OrderedDict()
        for img_path in img_paths:
            if face_coordinates and img_path in face_coordinates:
                coordinate = face_coordinates[img_path]
            else:
                coordinate = Image.Comment.read(img_path)

            try:
                coordinate = coordinate.decode()
            except AttributeError:
                pass

            images[img_path] = ClassifiedImage(
                id=os.path.basename(img_path).replace(settings.IMG_TYPE, ""),
                img=Image.base_64_html_src(img_path),
                coordinates=coordinate,
                is_classified=False
                if settings.TMP_CLASSIFIED_PATH in img_path
                else True,
                member=cls._image_path_to_member(img_path),
            ).dict()

        return images

    @classmethod
    def _image_path_to_member(cls, path: str) -> Member:
        if "_" not in path:
            return None
        try:
            member_id = int(os.path.basename(path).split("_")[0])
        except ValueError:
            return None

        return Member.objects.get(id=member_id)


def random_file_name(dir: str, type: str):
    while True:
        file_id = randint(1, int(1e10))
        ran_file = f"{dir}{file_id}{type}"
        if not os.path.isfile(ran_file):
            break
    return ran_file


def get_local_IP() -> str:
    """
    :return: local IP (192.168...) of raspberry pi on network
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip
