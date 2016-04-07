# coding: utf-8

import requests

'''
    A simple and thin Python library for the Ardoq REST API
    It exposes the JSON response to the calling client and checks for and throws HTTP errors

    It returns JSON rather than HTTP response so that I can cache the results and add synch functionality later
    though I might change this in the future to return the full HTTP response.
'''


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
            import ardoqpy
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
        _headers = {'Authorization': 'Token token='+self.token}
        self.session.headers.update(_headers)
        self.workspaces = None
        self.workspace = None
        self.model = None

    @staticmethod
    def _unwrap_response(resp):
        code = resp.status_code
        # TODO: check for error before getting the json
        json = resp.json()
        # errmsg = json.get('error', {}).get('message', 'Unknown error')

        if code == 200 or code == 201:
            return json
        elif code == 204:
            return {}
        elif code == 400:
            raise BadRequest(errmsg)
        elif code == 401:
            raise AuthorizationError(errmsg)
        elif code == 404:
            raise NotFoundError(errmsg)
        elif code == 503:
            raise ServiceUnavailable(errmsg)
        else:
            raise ArdoqClientException('%d: %s' % (code, errmsg))

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


    def _delete(self, resrc, **kwargs):
        url = self.baseurl + resrc
        kwargs.update({
            'org': self.org
        })
        resp = self.session.delete(url, params=kwargs)
        return self._unwrap_response(resp)


    def get_workspaces(self):
        self.workspaces = self._get('workspace')
        return self.workspaces


    # gets the workspace using either the worksspace ID or name
    def get_workspace(self, wsId=None, wsName=None):
        if self.workspaces is not None:
            if wsId is None and wsName is None:
                raise ArdoqClientException("need an arg for get_workspace")
            wsIndex = -1
            if wsId is not None:
                for i, v in enumerate(self.workspaces):
                    if v['_id'] == wsId:
                        wsIndex = i
            else:
                for i, v in enumerate(self.workspaces):
                    if v['name'] == wsName:
                        wsIndex = i
            self.workspace = self.workspaces[wsIndex]
        else:
            if wsId is None:
                raise ArdoqClientException("Don't have the workspaces yet, I'll need the workspace ID to get the ws")
            self.workspace = self._get('workspace' + '/' + wsId)
        return self.workspace

    def create_workspace(self, ws=None):
        if ws is None:
            raise ArdoqClientException('must provide a workspace')
        res = self._post('workspace', ws)
        return res

    # get the model for a given workspace id
    def get_model(self, wsId=None):
        if wsId is None:
            raise ArdoqClientException('must provide a workspaceID')
        self.model = self._get('model' + '/' + self.workspace['componentModel'])
        # TODO need to check if I have this workspace already, otherwise get it
        #   start by defaulting to the current workspace
        return self.model

    # post a new component
    def create_component(self, comp=None):
        if comp is None:
            raise ArdoqClientException('must provide a component')
        res = self._post('component', comp)
        return res

    def get_component(self, comp_id=None):
        if comp_id is None:
            raise ArdoqClientException('must provide a component id')
        comp = self._get('component/' + comp_id)
        return comp

