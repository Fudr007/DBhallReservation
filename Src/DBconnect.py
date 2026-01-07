import threading
import cx_Oracle

class DBconnect:
    _lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DBconnect, cls).__new__(cls)
        return cls._instance

    def __init__(self, user, passwd, dsn, encoding="UTF-8"):
        if getattr(self, "_initialized", False):
            return

        self.user = user
        self.passwd = passwd
        self.dsn = dsn
        self.encoding = encoding
        self.connection = None

    def connect(self):
        self.connection = cx_Oracle.connect(user=self.user, password=self.passwd, dsn=self.dsn, encoding=self.encoding)
        return self.connection

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None