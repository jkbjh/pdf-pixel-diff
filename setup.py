import io
import os
import re

from setuptools import find_packages
from setuptools import setup

try:

    from pip.req import parse_requirements

    # parse_requirements() returns generator of pip.req.InstallRequirement objects
    install_reqs = parse_requirements("requirements.in")

    # reqs is a list of requirement
    # e.g. ['django==1.5.1', 'mezzanine==1.4.6']
    reqs = [str(ir.req) for ir in install_reqs]
except ImportError:
    reqs = []  # PIP not available...


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type("")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    name="python_example",
    version="0.0.0",
    url="TODO",
    license="MIT",
    author="The Author",
    author_email="author@email.com",
    description="An example for a python package.",
    long_description=read("README.md"),
    packages=find_packages(exclude=("tests",)),
    install_requires=reqs,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
