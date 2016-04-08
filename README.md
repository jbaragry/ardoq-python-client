# Ardoqpy - a Python client for The Ardoq REST API

## Description

Ardoqpy is a thin client library for the Ardoq REST API.

## Documentation

You're reading it


## Installation

no `easy_install` or `pip` support
just clone it and use it as you need to

## Dependencies

- [Requests](https://github.com/kennethreitz/requests) - ardoqpy requires the requests package to be installed


## Quick Start
To get started, simply install ardoqpy, reate an ArdoqClient object and call methods:

    clone the repo
    edit `ardoq.cfg` to include your API token
    make sure `ardoqpy.py` opens your `ardoq.cfg`configuration file
    use `testclient.py`as a basis for your own client

or from the console
    from ardoq
>>> from ardoqpy.ardoqpy import ArdoqClient
>>> ardoq = ardoqpy.ArdoqClient(hosturl='https://app.ardoq.com', token='_your token_', org='ardoq')
>>> ardoq.get_workspaces()

## Version

- 0.1 - 2016/04/02 - Initial dev

## TODO
- complete the full REST-API for all ardoq resources
- add support for synching that is comparable to the java-api for ardoq
