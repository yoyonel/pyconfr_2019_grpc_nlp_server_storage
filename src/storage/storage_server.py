import logging
import os
import sys

import pymongo
import time
from grpc_reflection.v1alpha import reflection  # for gRPC server reflection
from pyconfr_2019.grpc_nlp.tools import rpc_server

from pyconfr_2019.grpc_nlp.protos import StorageService_pb2
from pyconfr_2019.grpc_nlp.protos.StorageService_pb2_grpc import add_StorageServiceServicer_to_server
from storage.dataproviders.storage_db import StorageDatabase
from storage.rpc.storage_service import StorageService

logger = logging.getLogger(__name__)


def serve(block=True, grpc_host_and_port=os.environ.get("TWITTER_ANALYZER_STORAGE_GRPC_HOST_AND_PORT", 'localhost:50052')):
    """
    Start a new instance of the storage service.

    If the server can't be started, a ConnectionError exception is raised

    :param block: If True, block until interrupted.
                  If False, start the server and return directly
    :type block: bool

    :param grpc_host_and_port: Listening address of the server.
                               Defaults to the content of the
                               ``TWITTER_ANALYZER_STORAGE_GRPC_HOST_AND_PORT``
                               environment variable, or ``localhost:50052`` if not set
    :type grpc_host_and_port: str

    :return: If ``block`` is True, return nothing.
             If ``block`` is False, return the server instance
    :rtype: None | grpc.server
    """

    def _add_storage_service_servicer_to_server(server):
        add_StorageServiceServicer_to_server(StorageService(), server)
        # the reflection service will be aware of "StorageService" and "ServerReflection" services.
        service_names = (StorageService_pb2.DESCRIPTOR.services_by_name['StorageService'].full_name, reflection.SERVICE_NAME)
        reflection.enable_server_reflection(service_names, server)
        logger.info("Activate reflection on server for services: {}".format(service_names))

    return rpc_server.serve('storage', _add_storage_service_servicer_to_server, grpc_host_and_port, block=block)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Ensure MongoDB is running and accessible
    max_retries = 5
    current_retry = 0
    while current_retry < max_retries:
        try:
            db = StorageDatabase()
            db.test_connectivity()  # throw in case of error
            break
        except pymongo.errors.ServerSelectionTimeoutError:
            current_retry += 1
            logger.warning(
                "[Attempt {}/{}] Failed to connect to MongoDB instance. "
                "Retrying in 2 second".format(current_retry, max_retries))
            time.sleep(2)

    if current_retry == max_retries:
        logger.fatal(
            'Failed to connect to MongoDB instance. '
            'Please make sure the daemon is running.')
        sys.exit(1)

    try:
        serve(block=True)
    except ConnectionError:
        sys.exit(1)


if __name__ == "__main__":
    main()
