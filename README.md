# PyConFR 2019 - GRPC NLP

## Instructions

Structure is based on [this article](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure). Source code can be found in the `src` folder, and tests in the `tests` folder.

### Installation

To install the package (development mode):

```bash
➤ make pip-install
Looking in indexes: https://pypi.org/simple, https://test.pypi.org/simple/                                                                               Obtaining file:///home/latty/Prog/__CONFERENCES__/2019_PyConFR_Bordeaux/pyconfr_2019_grpc_nlp_server_storage (from -r requirements.txt (line 1))         
Requirement already satisfied, skipping upgrade: grpcio in /home/latty/.pyenv/versions/3.7.3/envs/py3.7.3_pyconfr_2019_grpc_nlp_server_storage/lib/python
3.7/site-packages (from pyconfr-2019-grpc-nlp-server-storage==0.1.dev3+gf65b511.d20191019->-r requirements.txt (line 1)) (1.24.1)
[...]
Installing collected packages: pyconfr-2019-grpc-nlp-server-storage
  Found existing installation: pyconfr-2019-grpc-nlp-server-storage 0.1.dev3+gf65b511.d20191019
    Uninstalling pyconfr-2019-grpc-nlp-server-storage-0.1.dev3+gf65b511.d20191019:
      Successfully uninstalled pyconfr-2019-grpc-nlp-server-storage-0.1.dev3+gf65b511.d20191019
  Running setup.py develop for pyconfr-2019-grpc-nlp-server-storage
Successfully installed pyconfr-2019-grpc-nlp-server-storage   
```

### Tests

#### Tox
~~We use `tox` for the tests. This ensure a clear separation between the development environment and the test environment.
To launch the tests, run the `tox` command:~~

~~It first starts with a bunch of checks (`flask8` and others) and then launch the tests using python 3.~~

#### Pytest
You can use `pytest` for the tests:
```bash
➤ make pytest           
pytest -v
================================================================== test session starts ==================================================================
platform linux -- Python 3.7.3, pytest-5.2.1, py-1.8.0, pluggy-0.13.0 -- /home/latty/.pyenv/versions/3.7.3/envs/py3.7.3_pyconfr_2019_grpc_nlp_server_storage/bin/python3.7
cachedir: .pytest_cache
metadata: {'Python': '3.7.3', 'Platform': 'Linux-4.15.0-1057-oem-x86_64-with-debian-buster-sid', 'Packages': {'pytest': '5.2.1', 'py': '1.8.0', 'pluggy': '0.13.0'}, 'Plugins': {'cov': '2.8.1', 'html': '2.0.0', 'mock': '1.11.1', 'metadata': '1.8.0'}}
rootdir: /home/latty/Prog/__CONFERENCES__/2019_PyConFR_Bordeaux/pyconfr_2019_grpc_nlp_server_storage, inifile: setup.cfg, testpaths: tests
plugins: cov-2.8.1, html-2.0.0, mock-1.11.1, metadata-1.8.0
collected 1 item                                                                                                                                        

tests/test_rpc_storage.py::test_rpc_store_tweets_stream PASSED                                                                                    [100%]

=================================================================== warnings summary ====================================================================
tests/test_rpc_storage.py::test_rpc_store_tweets_stream
  /home/latty/.pyenv/versions/3.7.3/envs/py3.7.3_pyconfr_2019_grpc_nlp_server_storage/lib/python3.7/site-packages/mongomock/database.py:64: UserWarning: collection_names is deprecated. Use list_collection_names instead.
    warnings.warn('collection_names is deprecated. Use list_collection_names instead.')

-- Docs: https://docs.pytest.org/en/latest/warnings.html
============================================================= 1 passed, 1 warnings in 2.45s =============================================================
```
