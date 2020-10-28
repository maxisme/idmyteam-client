import os
import re

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
        os.path.join(settings.BASE_DIR, settings.settings_yaml["File Location"]["Classified Images"]["val"])
    )

    # number of unclassified
    settings.stats[settings.STAT_NUM_UNCLASSIFIED] = num_files_in_dir(
        os.path.join(settings.BASE_DIR, settings.settings_yaml["File Location"]["Unclassified Images"]["val"])
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