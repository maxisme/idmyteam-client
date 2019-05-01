import logging
import RPi.GPIO as GPIO
import time
from settings import config, functions

logging.getLogger('')


def run():
    # On button click all images taken after a recognition in the last x seconds
    # will be moved to the unclassified directory to be classified
    PIN = 2
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.IN)


    while True:
        input_state = GPIO.input(PIN)
        if not input_state:
            conn = functions.connect(config.DB["username"], config.DB["password"], config.DB["db"])
            capture_time = int(config.settings["Retract Recognition"]['Time']['val'])
            functions.incorrect_classification(
                conn=conn,
                ws=config.ws,
                capture_time=capture_time,
                tmp_dir=config.TMP_DETECTED_DIR,
                unclassified_dir=config.UNCLASSIFIED_PATH
            )
            conn.close()

            # prevents button being pressed again
            time.sleep(capture_time)
