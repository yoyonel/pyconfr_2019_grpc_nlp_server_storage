import logging
from typing import Iterator

import pymongo
from google.protobuf.json_format import MessageToDict
from pyconfr_2019.grpc_nlp.protos import Tweet_pb2
from pyconfr_2019.grpc_nlp.tools.timestamps import unix_timestamp_ms_to_datetime
from pymongo.errors import BulkWriteError

from storage.models.InsertTweet import InsertTweetResponse

logger = logging.getLogger('twitter_analyzer.storage.server.impl')
MONGODB_INSERT_THRESHOLD = 256


def prepare_mongodb_data_from_tweet(message: Tweet_pb2.Tweet) -> dict:
    """
    Convert a gRPC message into a representation suitable for mongodb

    Args:
        message:

    Returns:

    """
    data = MessageToDict(message, including_default_value_fields=True,
                         preserving_proto_field_name=True)
    data['created_at'] = unix_timestamp_ms_to_datetime(int(data['created_at']))

    return data


def insert_tweets(
        db,
        tweets_iterator: Iterator[Tweet_pb2.Tweet],
) -> InsertTweetResponse:
    """

    :param db:
    :param tweets_iterator:
    :return:
    """
    collection = db.tweets  # type: pymongo.collection.Collection

    # Create indexes
    collection.create_index(
        [
            ('created_at', pymongo.ASCENDING),
            ('user_id', pymongo.ASCENDING),
            ('tweet_id', pymongo.ASCENDING)
        ],
        unique=True,
    )

    all_data = []

    def insert_data_if_needed(_data, insert_tweet_response: InsertTweetResponse, force=False):
        def _search_error_and_continue():
            # test if all data in chunks are already stored in database
            tweets_ids = [mongodb_tweet['tweet_id'] for mongodb_tweet in _data]
            from_mongodb_tweets = list(db.tweets.find({"tweet_id": {"$in": tweets_ids}}))
            nb_data_already_in_db = len(from_mongodb_tweets)
            if nb_data_already_in_db == len(_data):
                logger.warning(f"All data (len={len(_data)}) already in DB.")
                return []
            # find data not inserted in database
            _data_not_already_insert = [
                mongodb_tweet
                for mongodb_tweet in _data
                if mongodb_tweet['tweet_id'] not in {
                    from_mongodb_tweet['tweet_id']
                    for from_mongodb_tweet in from_mongodb_tweets
                }
            ]
            # relaunch insertion with the rest of data
            return insert_data_if_needed(_data_not_already_insert, insert_tweet_response, force=force)

        # Insert data into MongoDB at soon as we have enough entries
        len_data = len(_data)
        if force or len_data >= MONGODB_INSERT_THRESHOLD:
            try:
                collection.insert_many(_data)
            except TypeError:
                logger.error(
                    "No data to insert into the `tweets` collection")
            except BulkWriteError as bwe:
                logger.error("bwe.details: {}".format(bwe.details))
                # you can also take this component and do more analysis
                # werrors = bwe.details['writeErrors']
                # raise bwe
                return _search_error_and_continue()
            except pymongo.errors.DuplicateKeyError:
                logger.warning(f"Duplicate key error in chunk (len(data)={len_data}) !")
                return _search_error_and_continue()
            except:  # noqa
                logger.error("Unexpected exception occurred!", exc_info=True)

            return []

        return _data

    nb_tweets_in_db_before_insert = db.tweets.estimated_document_count()

    stats = InsertTweetResponse()
    for stats.nb_tweets_received, tweet in enumerate(tweets_iterator):
        data = prepare_mongodb_data_from_tweet(tweet)
        all_data.append(data)
        all_data = insert_data_if_needed(all_data, stats)
    # insert last rows remaining
    insert_data_if_needed(all_data, stats, force=True)

    stats.nb_tweets_received += 1
    stats.nb_tweets_stored = db.tweets.estimated_document_count() - nb_tweets_in_db_before_insert

    return stats
