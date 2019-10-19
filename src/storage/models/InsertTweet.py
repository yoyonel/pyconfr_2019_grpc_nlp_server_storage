from pydantic import BaseModel


class InsertTweetResponse(BaseModel):
    nb_tweets_received: int = 0
    nb_tweets_stored: int = 0
