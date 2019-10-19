import logging
import os

from pymongo import MongoClient

log = logging.getLogger(__name__)


class StorageDatabase(object):
    def __init__(
            self,
            mongodb_service_host=os.environ.get("MONGODB_SERVICE_HOST", "localhost"),
            mongodb_service_port=int(os.environ.get("MONGODB_SERVICE_PORT", 27017)),
            mongodb_service_database=os.environ.get("MONGODB_SERVICE_DATABASE", ""),
            mongodb_user=os.environ.get("MONGODB_USER", None),
            mongodb_password=os.environ.get("MONGODB_PASSWORD", None)
    ):
        self._hostname = mongodb_service_host
        self._port = mongodb_service_port
        self._database = mongodb_service_database
        self._user = mongodb_user
        self._password = mongodb_password

    def __enter__(self):
        # Open connection
        self._conn = self._get_client()

        db = self._conn[self._database]
        if self._user:
            db.authenticate(self._user, self._password)

        return db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def test_connectivity(self):
        with self._get_client(serverSelectionTimeoutMS=50) as conn:
            info = conn.server_info()
            log.debug('MongoDB server info:')
            log.debug(info)

    def _get_client(self, **kwargs):
        return MongoClient(host=self._hostname, port=self._port, **kwargs)
