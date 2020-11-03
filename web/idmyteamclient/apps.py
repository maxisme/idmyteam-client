from threading import Thread

from django.apps import AppConfig


class IdmyteamclientConfig(AppConfig):
    name = "idmyteamclient"

    def ready(self):
        import ws
        from web import settings

        # start ws
        # daemon = True means the thread will be closed when the parent thread is
        settings.WS_THREAD = Thread(target=ws.start, daemon=True)
        settings.WS_THREAD.start()
