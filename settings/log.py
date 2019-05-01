import logging

class LogDBHandler(logging.Handler):
    def __init__(self, conn):
        logging.Handler.__init__(self)
        self.conn = conn

    def emit(self, record):
        if record.name not in ('tornado.access', 'tornado.general'):
            x = self.conn.cursor()
            try:
                x.execute("INSERT INTO `Logs` (message, level) VALUES (%s, %s)", (record.message, record.levelno))
                self.conn.commit()
            except Exception as e:
                print("Unable to write log into DB - IRONIC OR WHAT?! %s", e)
                self.conn.rollback()
