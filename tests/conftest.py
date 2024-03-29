import codecs
import functools
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

import grpc
import mongomock
import pytest
from bson import json_util
from pyconfr_2019.grpc_nlp.protos import StorageService_pb2_grpc
from pyconfr_2019.grpc_nlp.tools.find_free_port import find_free_port

from storage.storage_server import serve

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(funcName)s - %(levelname)s - %(message)s')


@dataclass
class MongoDBCache:
    # Code highly inspired from pytest-mongodb
    # https://github.com/mdomke/pytest-mongodb/blob/develop/pytest_mongodb/plugin.py
    cache: Optional[dict] = None
    server_instance: Optional[grpc.Server] = None


@pytest.fixture(autouse=True, scope="session")
def mongodb_cache() -> MongoDBCache:
    return MongoDBCache()


@pytest.fixture(autouse=True)
def setup_doctest_logger(log_level: int = logging.DEBUG):
    if is_pycharm_running():
        logger_add_streamhandler_to_sys_stdout()
    logger.setLevel(log_level)


def is_pycharm_running() -> bool:
    if ('docrunner.py' in sys.argv[0]) or ('pytest_runner.py' in sys.argv[0]):
        return True
    else:
        return False


def logger_add_streamhandler_to_sys_stdout():
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(stream_handler)


@pytest.fixture(scope="session")
def data_dir() -> Path:
    p = Path(__file__).parent / 'data'
    assert p.exists() and p.is_dir()
    return p


@pytest.fixture(scope="session")
def tweets_json(data_dir) -> Iterable[Dict]:
    return json.load((data_dir / 'tweets.clean.json').open('r'))


@pytest.fixture(scope='module')
def free_port_for_grpc_server():
    return find_free_port()


@pytest.fixture(scope='function')
def mongodb(pytestconfig, mongodb_cache):
    def make_mongo_client():
        return mongomock.MongoClient()

    @dataclass
    class MongoWrapper:
        def get_db(self, fixture_name: str = None, db_name: str = 'pyconfr_2019_grpc_nlp'):
            client = make_mongo_client()
            db = client[db_name]
            self.clean_database(db)
            if fixture_name is not None:
                self.load_fixtures(db, fixture_name)
            return db

        @staticmethod
        def load_fixtures(db: mongomock.Database, fixture_name: str):
            basedir = (pytestconfig.getoption('mongodb_fixture_dir')
                       or pytestconfig.getini('mongodb_fixture_dir'))
            fixture_path = os.path.join(pytestconfig.rootdir, basedir,
                                        '{}.json'.format(fixture_name))

            if not os.path.exists(fixture_path):
                raise FileNotFoundError(fixture_path)

            loader = functools.partial(json.load,
                                       object_hook=json_util.object_hook)
            try:
                collections = mongodb_cache.cache[fixture_path]
            except KeyError:
                with codecs.open(fixture_path, encoding='utf-8') as fp:
                    mongodb_cache.cache[fixture_path] = collections = loader(fp)

            for collection, docs in collections.items():
                mongo_collection = db[collection]  # type: mongomock.Collection
                mongo_collection.insert_many(docs)

        @staticmethod
        def clean_database(db):
            for name in db.collection_names(include_system_collections=False):
                db.drop_collection(name)

    return MongoWrapper()


@pytest.fixture(scope='session', autouse=True)
def close_storage_server(request, mongodb_cache):
    def stop_server():
        if mongodb_cache.server_instance:
            mongodb_cache.server_instance.stop(0)
            mongodb_cache.server_instance = None

    request.addfinalizer(stop_server)


@pytest.fixture(scope='function')
def mocked_storage_rpc_server(mocker, free_port_for_grpc_server, mongodb_cache):
    """
    Spawn an instance of the storage service, only if one is not already available

    Args:
        mocker:
        free_port_for_grpc_server:
        mongodb_cache:

    Returns:

    """

    class Wrapper(object):
        @staticmethod
        def start(database=None):
            # Mock the database first
            mock_storage = mocker.patch('storage.rpc.storage_service.StorageDatabase')

            if database:
                # Mock methods
                mock_storage.return_value.__enter__.return_value = database

            if mongodb_cache.server_instance is None:
                mongodb_cache.server_instance = serve(block=False,
                                                      grpc_host_and_port='localhost:{}'.format(free_port_for_grpc_server))

            assert mongodb_cache.server_instance is not None

    return Wrapper()


@pytest.fixture
def storage_rpc_stub(free_port_for_grpc_server):
    """
    Create a new storage rpc stub and connect to the server

    Args:
        free_port_for_grpc_server:

    Returns:

    """
    channel = grpc.insecure_channel('localhost:{}'.format(free_port_for_grpc_server))
    stub = StorageService_pb2_grpc.StorageServiceStub(channel)
    return stub
