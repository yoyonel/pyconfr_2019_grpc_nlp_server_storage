from pyconfr_2019.grpc_nlp.protos import StorageService_pb2, Tweet_pb2
from pyconfr_2019.grpc_nlp.tools.timestamps import parse_to_timestamp

from storage.rpc.storage_imp import prepare_mongodb_data_from_tweet


def test_rpc_store_tweets_stream(mocked_storage_rpc_server, storage_rpc_stub, mongodb, tweets_json):
    # Prepare mongo database
    db = mongodb.get_db()

    # Start storage server
    mocked_storage_rpc_server.start(db)

    sent_messages = []

    def _stream_fake_tweets():
        for tweet_json in tweets_json:
            msg = StorageService_pb2.StoreTweetsRequest(
                tweet=Tweet_pb2.Tweet(
                    created_at=parse_to_timestamp(tweet_json['created_at']),
                    text=tweet_json['text'],
                    user_id=tweet_json['user']['id'],
                    lang=tweet_json['lang'],
                    tweet_id=tweet_json['id'],
                )
            )
            data = prepare_mongodb_data_from_tweet(msg.tweet)
            sent_messages.append(data)
            yield msg

    # using gRPC service for storing tweets
    storage_rpc_stub.StoreTweetsStream(_stream_fake_tweets())

    # TODO: use `clean_json_tweets` utility
    # assert list(db.tweets.find({}, {'_id': False})) == sent_messages

    set_tweet_id_sent_messages = set([msg['tweet_id'] for msg in sent_messages])
    set_tweet_id_from_db = set([tweet['tweet_id'] for tweet in list(db.tweets.find({}, {'_id': False}))])

    # source JSON tweets not valid in term of key/indexes unicity
    assert set_tweet_id_sent_messages.difference(set_tweet_id_from_db) == set()
