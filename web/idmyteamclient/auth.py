from idmyteam.helpers import render

from idmyteamclient.helpers import update_global_stats
from web import settings


def stream_handler(request):
    return render(
        request,
        "stream.html",
        {
            "title": "Stream",
            "camera_running": bool(int(settings.settings_yaml["Camera"]["Run"]["val"])),
            "live_stream_on": bool(
                int(settings.settings_yaml["Camera"]["Live Stream"]["val"])
            ),
            "capture_log": settings.CAPTURE_LOG,
        },
    )


def settings_handler(request):
    update_global_stats()

    return render(
        request,
        "settings.html",
        {
            "title": "Settings",
            "settings": settings.settings_yaml,
            "stats": settings.stats,
            "stats_info": settings.STATS_INFO,
        },
    )
