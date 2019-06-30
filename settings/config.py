# settings for the whole local system.
import os, sys
import functions

SETTINGS_FILE = os.environ.get("SETTINGS_FILE", os.environ.get("LOCAL_DIR"))

settings = functions.YAML.read(SETTINGS_FILE)

ROOT = settings["Global"]["Root"]

######
# ws #
######
ws = None

#########
# stats #
#########
stats = {}
LOG_STAT_EVERY = 60  # logs to `STATS_FILE` every x frames
STAT_FPS = "FPS"
STAT_STORAGE = "Storage"
STAT_NUM_CLASSIFIED = "Number Of Classified Images"
STAT_NUM_UNCLASSIFIED = "Number Of Unclassified Images"
STAT_BG_EXTRACTOR_SPEED = "Background Extractor Speed"
STAT_SCRIPT_SPEED = "Script Speed"
STAT_CPU_TEMP = "CPU Temperature"

STATS_INFO = {
    STAT_FPS: "The number of frames per second the camera is taking",
    STAT_STORAGE: "How much storage is left on the device",
    STAT_NUM_CLASSIFIED: "The number of images that have been classified and will be sent for training",
    STAT_NUM_UNCLASSIFIED: """The number of images that are waiting for a user to assign which 
                                        member the face in the image is of.""",
    STAT_BG_EXTRACTOR_SPEED: "The time the background extractor takes to process an image (effects the FPS) in seconds",
    STAT_SCRIPT_SPEED: "The time the custom script takes to run.",
    STAT_CPU_TEMP: "The temperature of the CPU.",
}

###########
# camera.py
###########
CAMERA_THREAD = None
RESTART_CAMERA = False
CAMERA_RESTART_SETTINGS = [
    "Resolution",
    "Flip Vertically",
    "Framerate",
    "Shutter Speed",
]
IMG_TYPE = settings["Global"]["Image File Type"]
UPLOAD_RETRY_LIMIT = 20
MAJOR_BG_CHANGE_THRESH = 50
BG_IMG_REDUCTION = 0.5

###########
# run.py
###########
# paths
TMP_IMG_PATH = ROOT + settings["File Location"]["Live Image"]["val"]
TMP_DETECTED_DIR = ROOT + settings["File Location"]["Temporary Detected Images"]["val"]
TMP_CLASSIFIED_PATH = (
    ROOT + settings["File Location"]["Temporary Classified Images"]["val"]
)
CLASSIFIED_PATH = ROOT + settings["File Location"]["Classified Images"]["val"]
UNCLASSIFIED_PATH = ROOT + settings["File Location"]["Unclassified Images"]["val"]

# background extractor
NUM_BG_TRAIN = settings["Global"]["Training"]["Number"]

###########
# idmy.team
###########
username = settings["Credentials"]["Id My Team Username"]["val"]
credentials = settings["Credentials"]["Id My Team Credentials"]["val"]

###########
# Database
###########
DB = {
    "username": settings["Credentials"]["Database Username"]["val"],
    "password": settings["Credentials"]["Database Password"]["val"],
    "db": settings["Credentials"]["Database Name"]["val"],
}

########
# web
########
SOCKET_CLOSED = 0
SOCKET_CONNECTED = 1
SOCKET_NOT_TRAINED = 2
SOCKET_STATUS = SOCKET_CLOSED

COOKIE_SECRET = settings["Credentials"]["Cookie"]["val"]
SCRIPT_PATH = ROOT + settings["File Location"]["Bash Script"]["val"]
MIN_TRAINING_IMAGES_PER_MEMBER = 10  # TODO get from server
NO_PERM = "none"
PERMISSIONS = {
    NO_PERM: {"level": 0, "description": "Only to be recognised."},
    "low": {
        "level": 1,
        "description": "Allowed access to classify team members and view team members.",
    },
    "medium": {
        "level": 2,
        "description": "Allowed access to all the low permissions, adding members, deleting classification images, watching the live stream and editing the script.",
    },
    "high": {
        "level": 3,
        "description": "Allowed access to all the medium permissions, choosing member permissions, deleting team members, viewing the logs and changing the settings.",
    },
}
