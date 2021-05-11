# Ardoqpy - a Python3 client for The Ardoq REST API

## Description

Ardoqpy is a thin client library for the [Ardoq](https://ardoq.com) REST API.
It consists of 2 clients
- ArdoqClient
    - thin client for the rest-api
- ArdoqSyncClient
    - subclass of ArdoqClient
    - maintains a cache of aggregated workspace information
    - overrides write operations
        - only create components and references if they are not already in the cache
        - update cache for create and update operations
        - cache hit is based on
            - component: name, typeId
                - NB: name match is CASE_INSENSITIVE
            - reference: source, target, and type
    - overriders find_component (comp_name)
        - loads aggregated workspace to cache if its not present
        - finds component based on either of the following 
            - name: substring or exact match
            - fieldname == fieldvalue (you need to ensure the types can handle equivalence)
                - fieldname, if not None, is checked first

## Documentation
(see the test client for examples)

### Import Usage
```
from ardoqpy import ArdoqClient
```

ArdoqClient Implemented:
- workspace
    - get all
        - summary=True is undocumented in the REST docs but returns stats for workspaces
    - get by ID
    - get by ID aggregated
    - create workspace
    - delete
    - create folder
    - move workspace to folder
- component
    - get by ID
    - get all for workspace
    - create
    - delete
    - update
    - find by name in workspace
    - find by field_name / field_value in workspace
- reference
    - get all for workspace
    - get by ID
    - create
    - update
    - delete
- tag
    - get by ID
    - get all for workspace
    - create
- model
    - get by ID
- util
    - pprint
        - pretty print responses from ardoq calls


ArdoqSyncClient Implemented:
- all interfaces from ArdoqClient
- component
    - create
        - cache check is based on name attribute only (case insensitive)
    - update
- reference
    - create
        - cache check is based on source, target, and type attributes
    - update



## Installation

```
pip install ardoqpy
```

## Dependencies

- Python 3
- [Requests](https://github.com/kennethreitz/requests) - ardoqpy uses requests package for http requests


## Quick Start
To get started, simply install ardoqpy, create an ArdoqClient object and call methods:

    edit `ardoq.cfg` to include your API token
    make sure `ardoqpy.py` opens your `ardoq.cfg`configuration file
    use `testclient.py`as a basis for your own client

or from the console

    from ardoqpy import ArdoqClient
    ardoq = ardoqpy.ArdoqClient(hosturl='https://app.ardoq.com', token='_your token_', org='ardoq')
    ardoq.get_workspaces()

## Changelog
- 2017/01/25
    - Added pip and fields creation support.

- 2016/04/02
    - Initial dev
- 2016/06/18
    - bug and feature improvements
    - first version of the sync client

## TODO
- complete the full REST-API for fields and tags

## License
The ardoq-python-client is licensed under the MIT License

See LICENSE.md
