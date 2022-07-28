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
    - can be run in simulate mode which updates the report but does not execute write operations in ardoq

## Documentation
(see the test client for examples)

### ArdoqClient Import Usage
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
    - get all models and templates
    - print model to get IDs for component and reference types
    - find reference_type by name
    - find component_type by name
- folder
  - create
  - get by ID and all folders
- util
    - pprint
        - pretty print responses from ardoq calls

### ArdoqSyncClient Import Usage
```
from ardoqpy_sync import ArdoqSyncClient
ardoq = ArdoqSyncClient(hosturl=host, token=token)
ardoqsim = ArdoqSyncClient(hosturl=host, token=token, simulate=True)
```

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
    ardoq = ardoqpy.ArdoqClient(hosturl='https://YOURORG.ardoq.com', token='YOURTOKEN')
    ardoq.get_workspaces()

## Changelog
- 202207
  - add find_reference_type to return reftype definition from the metamodel for a workspace 
  - add find_component_type to return comptype definition from the metamodel for a workspace. Checks full hierarchy

- 202204
  - add print_model to print component and reference IDs

- 20220228
  - add PR to include references in get_component function
  - fixed bug in ardoq_sync when logging ref without displayText

- 20220212
  - deprecated org parameter
  - removed problem with slash on url
  - change get all components in ws to search operation. In line with public API docs

- 20220131
  - fixed bug in SyncClient when searching for references in a WS without refs

- 20220122
  - changed get_model. calling without ws_id now returns all models 
  - added get_folder. returns all folders if no folder_id

- 20211107
  - improve simulation mode
  - added cache_miss_comps and cache_miss_refs lists to capture items found in ardoq that are no longer in the source systems

- 20210717
    - Added simulate option to SyncClient to simulate write operations to update the report without modifying ardoq

- 20210420
    - Fixed PyPy support

- 20170125
    - Added pip and fields creation support.

- 20160618
    - bug and feature improvements
    - first version of the sync client

- 20160402
    - Initial dev
    

## TODO
- complete the full REST-API for fields and tags

## License
The ardoq-python-client is licensed under the MIT License

See LICENSE.md
