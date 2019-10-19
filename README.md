# PyConFR 2019 - GRPC NLP

## Instructions

Structure is based on [this article](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure). Source code can be found in the `src` folder, and tests in the `tests` folder.

### Installation

To install the package (development mode):

```bash
➤ pip install -e ".[develop]"
```
(can be long, because of gRPC installation/building)

Need to 'build' the proto(buf) files and generate codes/modules (serializer/parser/...):
```bash
➤ make 
Build proto modules ...
running build_proto_modules
➤ tree src/pyconfr_2019/grpc_nlp/protos 
src/pyconfr_2019/grpc_nlp/protos
src/pyconfr_2019/grpc_nlp/protos
├── __init__.py
├── Sentiment_pb2_grpc.py
├── Sentiment_pb2.py
├── Sentiment_pb2.pyi
├── Sentiment.proto
├── StorageService_pb2_grpc.py
├── StorageService_pb2.py
├── StorageService_pb2.pyi
├── StorageService.proto
├── Timeline_pb2_grpc.py
├── Timeline_pb2.py
├── Timeline_pb2.pyi
├── Timeline.proto
├── TweetFeaturesService_pb2_grpc.py
├── TweetFeaturesService_pb2.py
├── TweetFeaturesService_pb2.pyi
├── TweetFeaturesService.proto
├── Tweet_pb2_grpc.py
├── Tweet_pb2.py
├── Tweet_pb2.pyi
└── Tweet.proto
```

### Tests

#### Tox
We use `tox` for the tests. This ensure a clear separation between the development environment and the test environment.
To launch the tests, run the `tox` command:

It first starts with a bunch of checks (`flask8` and others) and then launch the tests using python 3.

#### Pytest
You can use `pytest` for the tests:
```bash
➤ pytest
```
