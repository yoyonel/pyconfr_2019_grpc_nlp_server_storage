#!/usr/bin/env python
"""The setup script."""
from distutils.command.build_py import build_py as _build_py
from distutils.command.sdist import sdist as _sdist
from itertools import chain
from pathlib import Path
from typing import Dict, List

import setuptools
from setuptools import find_packages
from setuptools import setup
from setuptools.command.develop import develop as _develop

# Parse requirements files
REQS = {
    pip_name: pip_lines
    for pip_name, pip_lines in map(
        lambda p: (p.stem.upper(), p.open().read().splitlines()),
        Path().glob(pattern="requirements/*.pip"),
    )
}  # type: Dict[str, List[str]]
# TODO: perform more complex substitution/eval (regexp, jinja, ...)
# https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
# https://stackoverflow.com/a/952952
# https://docs.python.org/2/library/itertools.html#itertools.chain.from_iterable
REQS["BASE_ALL"] = list(
    chain.from_iterable([REQS[k] for k in filter(lambda k: "BASE" in k, REQS)])
)

path_dependency_links = Path("requirements/dependency_links")
DEPENDENCY_LINKS = path_dependency_links.open().read().splitlines() if path_dependency_links.exists() else []

long_description = Path("README.md").read_text()

# Find if user has grpc available
try:
    from grpc_tools import command

    GRPC_INSTALLED = True
except ImportError:
    GRPC_INSTALLED = False


class BuildPackageProtos(setuptools.Command):
    """Command to generate project *_pb2.py modules from proto files."""

    description = "build grpc protobuf modules"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            # python 3.4+ should use builtin unittest.mock not mock package
            from unittest.mock import patch
        except ImportError:
            from mock import patch
        import grpc_tools
        import os
        import sys
        from grpc_tools.protoc import main as grpc_tools_protoc_main

        if GRPC_INSTALLED:
            def _mock_main(command_arguments):
                # insert arguments for mypy_protobuf
                # https://github.com/dropbox/mypy-protobuf
                mypy_out = os.path.abspath(self.distribution.package_dir[""])
                command_arguments.insert(len(command_arguments) - 1, "--mypy_out={}{}".format("quiet:", mypy_out))
                # "On windows, provide the bat file"
                if os.name == 'nt':
                    path_to_protoc_gen_mypy = Path(sys.executable).parent / "protoc_gen_mypy.bat"
                    if not path_to_protoc_gen_mypy.exists():
                        raise FileNotFoundError("Can't found {} !".format(path_to_protoc_gen_mypy.parent))
                    command_arguments.insert(1, "--plugin=protoc-gen-mypy={}".format(str(path_to_protoc_gen_mypy)))

                return grpc_tools_protoc_main(command_arguments)

            with patch.object(grpc_tools.protoc, "main", _mock_main):
                command.build_package_protos(self.distribution.package_dir[""])
        else:
            raise ModuleNotFoundError("grpcio-tools is needed in order to generate the proto classes")


class BuildPyCommand(_build_py):
    """Custom build command."""

    def run(self):
        self.run_command("build_proto_modules")
        _build_py.run(self)


class DevelopCommand(_develop):
    """Custom develop command."""

    def run(self):
        self.run_command("build_proto_modules")
        _develop.run(self)


class SDistCommand(_sdist):
    """Custom sdist command."""

    def run(self):
        self.run_command("build_proto_modules")
        _sdist.run(self)


setup(
    name="pyconfr_2019_grpc_nlp_server_storage",
    author="Lionel ATTY",
    author_email="yoyonel@hotmail.com",
    url="https://github.com/yoyonel/pyconfr_2019_grpc_nlp_server_storage.git",
    use_scm_version=True,
    description="",
    # https://packaging.python.org/guides/making-a-pypi-friendly-readme/
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["*.proto"]},
    include_package_data=True,
    install_requires=REQS["BASE_ALL"],
    setup_requires=REQS["SETUP"],
    extras_require={
        "test": REQS["BASE_ALL"] + REQS["TEST"],
        "develop": REQS["BASE_ALL"] + REQS["TEST"] + REQS["DEV"],
        "docs": REQS["DOCS"]
    },
    dependency_links=DEPENDENCY_LINKS,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.6",
    cmdclass={
        "sdist": SDistCommand,
        "build_proto_modules": BuildPackageProtos,
    },
    # https://github.com/pypa/sample-namespace-packages/issues/6
    zip_safe=False,
)
