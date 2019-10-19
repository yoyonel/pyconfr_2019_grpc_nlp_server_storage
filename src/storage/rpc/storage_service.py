from typing import Iterator

from pyconfr_2019.grpc_nlp.protos.StorageService_pb2 import StoreTweetsRequest, StoreTweetsResponse
from pyconfr_2019.grpc_nlp.protos.StorageService_pb2_grpc import StorageServiceServicer

from storage.dataproviders.storage_db import StorageDatabase
from storage.rpc.storage_imp import insert_tweets

try:
    import grpc
except ImportError:
    raise ModuleNotFoundError("grpc is needed in order to "
                              "launch RPC server (`pip install .[grpc]`)")


class StorageService(StorageServiceServicer):

    def __init__(self):
        pass

    def StoreTweetsStream(
            self,
            request_iterator: Iterator[StoreTweetsRequest],
            context: grpc.ServicerContext
    ) -> StoreTweetsResponse:
        """

        Args:
            request_iterator:
            context:

        Returns:

        """
        with StorageDatabase() as db:
            response = insert_tweets(db, map(lambda request: request.tweet, request_iterator))

        return StoreTweetsResponse(**response.dict())
