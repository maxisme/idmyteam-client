import os
from pathlib import Path

import functions

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "a8r(%ir&!=7rc0ycu(=fwks1qc$#lsr34_5p7v+dbif7kh%1pn"
)
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "idmyteam",
    "idmyteamclient.apps.IdmyteamclientConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTH_USER_MODEL = "idmyteamclient.Member"

ROOT_URLCONF = "web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "web.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

#########################################
# id my team client specific settings
#########################################

WS_URL = os.environ.get("WS_URL", "ws://127.0.0.1:8000/ws")
WS_THREAD = None

SETTINGS_FILE = os.environ.get("SETTINGS_FILE", os.path.join(BASE_DIR, "settings.yaml"))

yaml = functions.YAML(SETTINGS_FILE)

SCRIPT_PATH = os.path.join(BASE_DIR, "recognition.sh")

# image directories
UNCLASSIFIED_PATH = os.path.join(BASE_DIR, "images/unclassified/")
CLASSIFIED_PATH = os.path.join(BASE_DIR, "images/classified/")
TMP_CLASSIFIED_PATH = os.path.join(BASE_DIR, "images/tmp/")

#########
# stats #
#########
stats = {}
LOG_STAT_EVERY = 60
STAT_FPS = "FPS"
STAT_STORAGE = "Storage"
STAT_NUM_CLASSIFIED = "Number Of Classified Images"
STAT_NUM_UNCLASSIFIED = "Number Of Unclassified Images"
STAT_BG_EXTRACTOR_SPEED = "Background Extractor Speed"
STAT_SCRIPT_SPEED = "Script Speed"
STAT_CPU_TEMP = "CPU Temperature"
STAT_RECOGNITION_SPEED = "Recognition Speed"

STATS_INFO = {
    STAT_FPS: "The number of frames per second the camera is taking",
    STAT_STORAGE: "How much storage is left on the device",
    STAT_NUM_CLASSIFIED: "The number of images that have been classified and will be sent for training",
    STAT_NUM_UNCLASSIFIED: """The number of images that are waiting for a user to assign which 
    member the face in the image is of.""",
    STAT_BG_EXTRACTOR_SPEED: """The amount of time the background extractor takes to process an image 
    (effects the FPS) in seconds""",
    STAT_SCRIPT_SPEED: "The amount of  time the custom script takes to run.",
    STAT_RECOGNITION_SPEED: "The amount of time the last recognition took to recognise a member.",
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
UPLOAD_RETRY_LIMIT = 10
CAPTURE_LIMIT = 10
CAPTURE_LOG = {}
MAJOR_BG_CHANGE_THRESH = 50
BG_IMG_REDUCTION = 0.5
IMG_TYPE = ".jpg"

########
# web
########
NUM_LOGS_PER_PAGE = 30
NUM_UNCLASSIFIED_PER_PAGE = 30

SOCKET_CLOSED = 0
SOCKET_CONNECTED = 1
SOCKET_NO_MODEL = 2
SOCKET_STATUS = SOCKET_CLOSED

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
