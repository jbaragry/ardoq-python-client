# coding: utf-8

import requests
import json
from http import cookiejar
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

'''
    A simple and thin Python library for the Ardoq REST API
    It exposes the JSON response to the calling client and checks for and throws HTTP errors

    It returns JSON rather than HTTP response so that I can cache the results and add synch functionality later
    though I might change this in the future to return the full HTTP response.

    written for python 3.3+
'''


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class ArdoqClientException(Exception):
    pass


class AuthorizationError(ArdoqClientException):
    """Raised when auth_token is invalid or not adequate for the operation."""


class NotFoundError(ArdoqClientException):
    """Specified room or user not found."""


class ServiceUnavailable(ArdoqClientException):
    """The service is temporarily unavailably."""


class BadRequest(ArdoqClientException):
    """Error in data provided in the request."""


class ArdoqClient(object):
    '''
        Example usage::
            ...
    '''
    def __init__(self, hosturl='https://app.ardoq.com/', token=None, org='ardoq'):
        '''
        Create an Ardoq API client.
        :param hosturl: The Ardoq installation you wish to connect to (defaults to https://app.ardoq.com)
        :param token: An authorization token
        :param org:
            organization to use. Defaults to personal org
        '''

        self.baseurl = hosturl + '/api/'
        self.token = token
        self.org = org
        self.session = requests.Session()
        self.session.cookies.set_policy(BlockAll())  # for stopping cookies that mess up high-volume API calls to ardoq
        _headers = {'Authorization': 'Token token='+self.token}
        self.session.headers.update(_headers)
        self.workspaces = None
        self.workspace = None
        self.model = None

    @staticmethod
    def _unwrap_response(resp):
        code = resp.status_code

        if code == 200 or code == 201:
            return resp.json()
        elif code == 204:
            return {}
        else:
            logging.debug('request: %s', resp.request.body)
            raise ArdoqClientException({'code': code, 'reason': resp.reason, 'text': resp.text})

    def _get(self, resrc, **kwargs):
        url = self.baseurl + resrc
        kwargs.update({
            'org': self.org
        })
        resp = self.session.get(url, params=kwargs)
        return self._unwrap_response(resp)

    def _post(self, resrc, payload, **kwargs):
        url = self.baseurl + resrc
        kwargs.update({
            'org': self.org
        })
        resp = self.session.post(url, json=payload, params=kwargs)
        return self._unwrap_response(resp)

    def _put(self, resrc, payload, **kwargs):
        url = self.baseurl + resrc
        kwargs.update({
            'org': self.org
        })
        resp = self.session.put(url, json=payload, params=kwargs)
        return self._unwrap_response(resp)

    def _delete(self, resrc, **kwargs):
        url = self.baseurl + resrc
        kwargs.update({
            'org': self.org
        })
        resp = self.session.delete(url, params=kwargs)
        return self._unwrap_response(resp)

    def pprint(self, obj):
        print (json.dumps(obj, sort_keys=True, indent=4))

    '''
    functions for workspaces
    '''
    # get all workspaces
    def get_workspaces(self, summary=False):
        self.workspaces = self._get('workspace' if not summary else 'workspace/summary')
        return self.workspaces

    # gets the workspace using either the workspace ID or name
    # TODO need to check if the ID or name is in the existing workspaces...
    # TODO: change this to only get the workspace by ID.
    #       need a different function to find the id by name
    def get_workspace(self, ws_id=None, aggregated=False):
        if ws_id is None:
            raise ArdoqClientException("need an id for get_workspace")
        endpoint = 'workspace' + '/' + ws_id
        if aggregated:
            endpoint += '/aggregated'
        self.workspace = self._get(endpoint)
        return self.workspace

    def create_workspace(self, ws=None):
        if ws is None:
            raise ArdoqClientException('must provide a workspace')
        res = self._post('workspace', ws)
        return res

    # delete a workspace
    def del_workspace(self, ws_id = None):
        if ws_id is None:
            raise ArdoqClientException('must provide a workspace id')
        res = self._delete('workspace/' + ws_id)
        return res

    def create_folder(self, folder=None):
        if folder is None:
            raise ArdoqClientException('must provide a folder name and payload')
        res = self._post('workspacefolder', folder)
        return res

    def get_folder(self, folder_id=None):
        res = self._get('workspacefolder/' + folder_id)
        return res

    def move_workspace(self, folder_id = None, ws_list = None):
        if ws_list is None and folder_id is None:
            raise ArdoqClientException('must provide a folder id and list of workspaces to move')
        res = self._put('workspacefolder/' +  folder_id + '/add', {'workspaces': ws_list})
        return res

    '''
    functions for models
    '''
    # get the model for a given workspace id
    def get_model(self, ws_id=None, model_id=None):
        if ws_id is None:
            raise ArdoqClientException('must provide a workspaceID')
        # if self.workspace['_id'] != ws_id:
        if model_id is None:
            self.workspace = self._get('workspace' + '/' + ws_id)
            model_id = self.workspace['componentModel']
        self.model = self._get('model' + '/' + model_id)
        return self.model

    # get all model for and organisation
    # TODO combine with get_model
    def get_models(self):
        self.models = self._get('model' + '/')
        return self.models

    def create_model(self, model=None):
        if model is None:
            raise ArdoqClientException('must provide a model')
        res=self._post('model', model)

    def create_field(self, field=None):
        if field is None:
            raise ArdoqClientException('must provide a field')
        res=self._post('field', field)

    '''
    functions for components
    '''
    # post a new component
    def create_component(self, comp=None):
        if comp is None:
            raise ArdoqClientException('must provide a component')
        res = self._post('component', comp)
        return res

    '''
    get component
        :param ws_id: mandatory, get component within this workspace
        :param comp_id: id for the component to get. If None, then gets all components for that workspace
    '''
    def get_component(self, ws_id=None, comp_id=None):
        if ws_id is None and comp_id is None:
            raise ArdoqClientException('must provide a workspace id')
        if comp_id is not None:
            # comp = self._get('workspace/' + ws_id + '/component/' + comp_id) this is how the upcoming API will work
            comp = self._get('component/' + comp_id)
        else:
            comp = self._get('workspace/' + ws_id + '/component')
        return comp

    def update_component(self, comp_id=None, comp=None):
        if comp_id is None or comp is None:
            raise ArdoqClientException('must provide a component id, and component')
        res = self._put('component/' + comp_id, comp)
        return res

    def del_component(self, comp_id=None):
        if comp_id is None:
            raise ArdoqClientException('must provide a component id')
        res = self._delete('component/' + comp_id)
        return res

    def find_component(self, ws_id=None, comp_name=None, field_name=None, field_value=None, exact=False):
        if ws_id is None:
            raise ArdoqClientException('must provide a workspace id')
        if comp_name is not None:
            res= self._get('component/search', workspace=ws_id, name=comp_name)
            if exact is True:
                for r in res:
                    if r['name'] == comp_name:
                        return [dict(r)]
                return []
            return res
        if field_name is not None:
            res= self._get('component/fieldsearch', workspace=ws_id, **{field_name: field_value})
            if exact is True:
                for r in res:
                    if r[field_name] == field_value:
                        return [dict(r)]
                return []
            return res
        raise ArdoqClientException('must provide a component name, or field name/value pair')


    '''
    functions for references
    '''
    def create_reference(self, ref=None):
        if ref is None:
            raise ArdoqClientException('must provide a reference')
        res = self._post('reference', ref)
        return res

    def get_reference(self, ws_id=None, ref_id=None):
        if ws_id is None:
            raise ArdoqClientException('must provide a source workspace id')
        #if ref_id is not None:
            # comp = self._get('workspace/' + ws_id + '/component/' + comp_id) this is how the upcoming API will work
        if ref_id is None:
            ref_id = ''
        ref = self._get('reference/' + ref_id, workspace=ws_id)
        return ref

    def del_reference(self, ref_id=None):
        if ref_id is None:
            raise ArdoqClientException('must provide a reference id')
        res = self._delete('reference/' + ref_id)
        return res

    def update_reference(self, ref_id=None, ref=None):
        if ref_id is None or ref is None:
            raise ArdoqClientException('must provide a reference id, and reference')
        res = self._put('reference/' + ref_id, ref)
        return res

    '''
    functions for tags
    '''
    def create_tag(self, tag=None):
        if tag is None:
            raise ArdoqClientException('must provide a tag')
        res = self._post('tag', tag)
        return res

    def get_tag(self, ws_id=None, tag_id=None):
        if ws_id is None and tag_id is None:
            raise ArdoqClientException('must provide a workspace id and/or tag id')
        if tag_id is not None:
            tag = self._get('tag/' + tag_id)
        if ws_id is not None and tag_id is None:
            tag = self._get('tag/' + 'workspace/' + ws_id)
        return tag
