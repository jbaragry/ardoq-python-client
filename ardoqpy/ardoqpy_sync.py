import logging
from ardoqpy import ArdoqClient

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ArdoqSyncClient(ArdoqClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = {} # cache is a dictionary of workspaces. wsID is the key for each
        self.init_report()

    def get_workspace(self, *args, **kwargs):
        res = super().get_workspace(*args, **kwargs, aggregated=True)
        self.ws[res['_id']] = res
        return res

    def _is_different(self, old, new):
        for k, v in new.items():
            if k not in old.keys(): # might be a new attribute
                return True
            if new[k] != old[k]:
                return True
        return False

    def _find_component(self, comp=None):
        for ind, c in enumerate(self.ws[comp['rootWorkspace']]['components']):
            if c['name'].lower() == comp['name'].lower() and c['typeId'] == comp['typeId']:
                return ind, c
        return 0, {}

    # find component in cache
    # find is based on component name in ws.
    # name comparison is substring. can be set to exact match with exact param
    def find_component(self, ws_id=None, comp_name=None,
                       field_name=None, field_value=None, exact=False):
        if ws_id != None and (comp_name != None or field_name != None):
            if ws_id not in self.ws.keys():
                self.ws[ws_id] = self.get_workspace(ws_id=ws_id)
            comps = list()
            for ind, c in enumerate(self.ws[ws_id]['components']):
                if field_name is not None:
                    if c['field_name'] == field_value:
                        comps.append(c)
                        break
                if exact:
                    if comp_name == c['name']:
                        logging.debug('find_component - cache_hit: %s', comp_name)
                        comps.append(c)
                        break
                else:
                    if comp_name in c['name']:
                        logging.debug('find_component - cache_hit: %s', comp_name)
                        comps.append(c)
            return comps
        else:
            res = super().find_component(ws_id=ws_id, comp_name=comp_name, field_name=field_name,
                                         field_value=field_value, exact=exact)
            return res

    def create_component(self, comp=None):
        # search in cache
        # if its different then update cache and ardoq
        if comp['rootWorkspace'] not in self.ws.keys():
            self.ws[comp['rootWorkspace']] = self.get_workspace(ws_id=comp['rootWorkspace'])

        ind, c = self._find_component(comp=comp)
        if c:
            if self._is_different(c, comp):
                for k, v in comp.items():
                    c[k] = comp[k]
                res = super().update_component(comp_id=c['_id'], comp=c)
                self.ws[comp['rootWorkspace']]['components'][ind] = res
                self.report['updated_comps'] += 1
                return(res)
            else:
                logging.debug('create_component - cache_hit: %s', comp['name'])
                self.report['cache_hit_comps'] += 1
                return c
        res = super().create_component(comp=comp)
        self.ws[comp['rootWorkspace']]['components'].append(res)
        self.report['new_comps'] += 1
        return res

    def update_component(self, comp_id=None, comp=None):
        if comp['rootWorkspace'] not in self.ws.keys():
            self.ws[comp['rootWorkspace']] = self.get_workspace(ws_id=comp['rootWorkspace'])

        res = super().update_component(comp_id=comp_id, comp=comp)

        ind = next(index for index, c in
                   enumerate(self.ws[comp['rootWorkspace']]['components'])
                   if c['_id'] == comp['_id'])
        self.ws[comp['rootWorkspace']]['components'][ind] = res
        self.report['updated_comps'] += 1

    def _find_reference(self, ref=None):
        for ind, r in enumerate(self.ws[ref['rootWorkspace']]['references']):
            if r['type'] == ref['type'] and r['target'] == ref['target'] and r['source'] == ref['source']:
                return ind, r
        return 0, {}

    def create_reference(self, ref=None):
        # search in cache
        # if its different or new then update cache and ardoq
        if ref['rootWorkspace'] not in self.ws.keys():
            self.ws[ref['rootWorkspace']] = self.get_workspace(ws_id=ref['rootWorkspace'])

        ind, r = self._find_reference(ref=ref)
        if r:
            if self._is_different(r, ref):
                for k, v in ref.items():
                    r[k] = ref[k]
                res = super().update_reference(ref_id=r['_id'], ref=r)
                self.ws[ref['rootWorkspace']]['references'][ind] = res
                self.report['updated_refs'] += 1
                return(res)
            else:
                logging.debug('create_ref - cache_hit: %s', ref['displayText'])
                self.report['cache_hit_refs'] += 1
                return r
        res = super().create_reference(ref=ref)
        self.ws[ref['rootWorkspace']]['references'].append(res)
        self.report['new_refs'] += 1
        return res

    def update_reference(self, ref_id=None, ref=None):
        if ref['rootWorkspace'] not in self.ws.keys():
            self.ws[ref['rootWorkspace']] = self.get_workspace(ws_id=ref['rootWorkspace'])

        res = super().update_reference(ref_id=ref_id, ref=ref)
        ind = next(index for index, r in
                   enumerate(self.ws[ref['rootWorkspace']]['references'])
                   if r['_id'] == ref['_id'])
        self.ws[ref['rootWorkspace']]['references'][ind] = res
        self.report['updated_refs'] += 1

    def get_report(self):
        logging.info('Ardoq Sync')
        for k, v in self.report.items():
            logging.info(k, ' : ', v)

    def init_report(self):
        self.report = {'new_comps': 0, 'updated_comps': 0,
                       'new_refs': 0, 'updated_refs': 0,
                       'cache_hit_comps': 0, 'cache_hit_refs': 0,
                       'status': 'success', 'description': None}