import json
import sys
import os
import urllib.request
import urllib.parse
import logging

# This Client is a copy of the v2 sample client provided on the ardoq developer portal.
# For more information see https://developer.ardoq.com/getting-started/example_client/


class Batch:
    def __init__(self, respondWithEntities=False):
        self.body = {
            "options": {"respondWithEntities": respondWithEntities},
            "components": {"create": [], "update": [], "delete": []},
            "references": {"create": [], "update": [], "delete": []},
        }

    def is_empty(self):
        components = (
            self.body["components"]["create"]
            or self.body["components"]["update"]
            or self.body["components"]["delete"]
        )
        references = (
            self.body["references"]["create"]
            or self.body["references"]["update"]
            or self.body["references"]["delete"]
        )
        return False if components or references else True

    def _create(self, resource, body, batchId):
        content = {"body": body}
        if batchId is not None:
            content["batchId"] = batchId
        self.body[resource]["create"].append(content)
        return self

    def create_component(self, data, batchId=None):
        return self._create("components", data, batchId)

    def create_reference(self, data, batchId=None):
        return self._create("references", data, batchId)

    def _update(self, resource, id, body, version):
        self.body[resource]["update"].append(
            {"ifVersionMatch": version, "id": id, "body": body}
        )
        return self

    def update_component(self, id, data, version="latest"):
        return self._update("components", id, data, version)

    def update_reference(self, id, data, version="latest"):
        return self._update("references", id, data, version)

    def _delete(self, resource, id):
        self.body[resource]["delete"].append({"id": id})
        return self

    def delete_component(self, id):
        return self._delete("components", id)

    def delete_reference(self, id):
        return self._delete("references", id)


default_host = "https://app.ardoq.com"


class API:
    def __init__(self, ardoq_api_host=None, ardoq_api_token=None, ardoq_org_label=None):
        self.ardoq_api_host = ardoq_api_host or os.getenv(
            "ARDOQ_API_HOST", default_host
        )
        self.ardoq_api_token = ardoq_api_token or os.getenv("ARDOQ_API_TOKEN")
        self.ardoq_org_label = ardoq_org_label or os.getenv("ARDOQ_ORG_LABEL")

        if self.ardoq_api_token is None:
            logging.fatal("API Token expected")
            sys.exit(1)
        if self.ardoq_api_host == default_host and self.ardoq_org_label is None:
            logging.fatal(
                "Org label required when using host: '{}'".format(default_host)
            )
            sys.exit(1)

#        print("----------------------------------------------------")
#        print("Using Ardoq host: " + self.ardoq_api_host)
#        print("Using API token ending: ..." + self.ardoq_api_token[-4:])
#        print(
#            "Using Org Label: "
#            + (self.ardoq_org_label if self.ardoq_org_label else "<NOT PROVIDED>")
#        )
#        print("----------------------------------------------------")

    def _init_request(self, url, method, data=None):
        req = urllib.request.Request(url, method=method)
        req.add_header("Authorization", "Bearer " + self.ardoq_api_token)
        if self.ardoq_org_label is not None:
            req.add_header("X-org", self.ardoq_org_label)
        if data is not None:
            req.add_header("Content-Type", "application/json; charset=utf-8")
            data = json.dumps(data).encode("utf-8")
        return [req, data]

    def _request(self, resource, method="GET", query_params=None, data=None):
        url = self.ardoq_api_host + "/api/v2" + resource
        if query_params:
            url = url + "?" + urllib.parse.urlencode(query_params)
        [req, data] = self._init_request(url, method, data)
        with urllib.request.urlopen(req, data=data) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _raw_request(self, resource, method="GET", query_params=None, data=None):
        url = self.ardoq_api_host + "/api/v2" + resource
        if query_params:
            url = url + "?" + urllib.parse.urlencode(query_params)
        [req, data] = self._init_request(url, method, data)
        with urllib.request.urlopen(req, data=data) as resp:
            return resp.read().decode("utf-8")

    def _paginated_request(self, resource, method="GET", query_params=None, data=None):
        result_data = self._request(
            resource, method=method, query_params=query_params, data=data
        )
        while True:
            for value in result_data.get("values", []):
                yield value
            next_url = result_data.get("_links", {}).get("next", {}).get("href")
            if next_url is None:
                return
            [req, _] = self._init_request(next_url, "GET")
            with urllib.request.urlopen(req) as resp:
                result_data = json.loads(resp.read().decode("utf-8"))

    def me(self):
        return self._request("/me", method="GET")

    def list_components(self, query_params=None, paginated=False, raw=False):
        if paginated:
            return self._paginated_request(
                "/components", method="GET", query_params=query_params
            )
        if raw:
            return self._raw_request("/components", method="GET", query_params=query_params)
        return self._request("/components", method="GET", query_params=query_params)

    def create_component(self, data):
        return self._request("/components", method="POST", data=data)

    def read_component(self, id):
        return self._request("/components/" + id, method="GET")

    def update_component(self, id, data, version="latest"):
        return self._request(
            "/components/" + id,
            method="PATCH",
            query_params={"ifVersionMatch": version},
            data=data,
        )

    def delete_component(self, id):
        return self._request("/components/" + id, method="DELETE")

    def list_references(self, query_params=None):
        return self._paginated_request(
            "/references", method="GET", query_params=query_params
        )

    def create_reference(self, data):
        return self._request("/references", method="POST", data=data)

    def read_reference(self, id):
        return self._request("/references/" + id, method="GET")

    def update_reference(self, id, data, version="latest"):
        return self._request(
            "/references/" + id,
            method="PATCH",
            query_params={"ifVersionMatch": version},
            data=data,
        )

    def delete_reference(self, id):
        return self._request("/references/" + id, method="DELETE")

    def list_workspaces(self, query_params=None):
        return self._paginated_request(
            "/workspaces", method="GET", query_params=query_params
        )

    def read_workspace(self, id):
        return self._request("/workspaces/" + id, method="GET")

    def read_workspace_context(self, id):
        return self._request("/workspaces/" + id + "/context", method="GET")

    def batch(self, data):
        return self._request("/batch", method="POST", data=data)

    def reports(self):
        return self._request("/reports", method="GET")

    def report(self, id):
        return self._request("/reports/" + id, method="GET")

    def report_run(self, id, view):
        return self._request("/reports/" + id + "/run/" + view, method="GET")
