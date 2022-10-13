import logging
import secrets
from ardoqpy import ArdoqClient

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

'''
ArdoqSyncClient is a subclass of ArdoqClient
It provides the same functions as the superclass but maintains a cache of ardoq model information
Read return from the cache if it exists
Write operations update ardoq only if the item is missing from the cache or if new attributes are different from those in the cache

Has one additional operation keyword argument - simulate
If simulate is True then write operations update the report but are not performed in ardoq and the cache is not updated
return value from these operations will be the same as the input param

ardoq = ArdoqSyncClient(hosturl='https://myorg.ardoq.com', token='....', simulate=True)
'''


class ArdoqSyncClient(ArdoqClient):

    def __init__(self, *args, simulate=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = {} # cache is a dictionary of workspaces. wsID is the key for each
        self.init_report()
        self.simulate = simulate

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

    def _find_component(self, comp=None, field_name=None, field_value=None):
        for ind, c in enumerate(self.ws[comp['rootWorkspace']]['components']):
            if field_name is not None:
                # can't use .lower() when I can't tell if its a string....
                if c[field_name] == field_value and c['typeId'] == comp['typeId']:
                    return ind, c
            else:
                if c['name'].lower() == comp['name'].lower() and c['typeId'] == comp['typeId']:
                    return ind, c
        return 0, {}

    # find component in cache
    # find is based on component name in ws.
    # name comparison is substring. can be set to exact match with exact param
    def find_component(self, ws_id=None, comp_name=None,
                       field_name=None, field_value=None, exact=False):
        if ws_id is not None:
            if ws_id not in self.ws.keys():
                self.ws[ws_id] = self.get_workspace(ws_id=ws_id)
        if comp_name is not None and not field_name:
            comps = list()
            for ind, c in enumerate(self.ws[ws_id]['components']):
                if field_name is not None:
                    if c[field_name] == field_value:
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
        else: # why am I calling suprt instead of _find.... because that returns result of enumerate...
            res = super().find_component(ws_id=ws_id, comp_name=None, field_name=field_name,
                                         field_value=field_value, exact=exact)
            return res

    def create_component(self, comp=None, field_name=None, field_value=None):
        """
        will create a new component
        if component already exists then it will update instead
        find function is based on comp_name only
        :param comp: the component values
        :param field_name: the field name to use for matching if the component exist. If this param is missing then name will be used
        :param field_value: the value of the field for the match
        :return:
        """
        # search in cache based on name
        # if its different, then update cache and ardoq
        if comp['rootWorkspace'] not in self.ws.keys():
            self.ws[comp['rootWorkspace']] = self.get_workspace(ws_id=comp['rootWorkspace'])

        # update the find to include field name, but that means create needs that field name
        # find only works on component name. comps with same name but different attributes will update rather
        # then creating a 2nd component.
        ind, c = self._find_component(comp=comp, field_name=field_name, field_value=field_value)
        if c:
            if self._is_different(c, comp):
                for k, v in comp.items():
                    c[k] = comp[k]
                if not self.simulate:
                    res = super().update_component(comp_id=c['_id'], comp=c)
                    self.ws[comp['rootWorkspace']]['components'][ind] = res
                    self.report['updated_comps'] += 1
                    return(res)
                else:
                    self.report['updated_comps'] += 1
                    return (c)
            else:
                logging.debug('create_component - cache_hit: %s', comp['name'])
                self.report['cache_hit_comps'] += 1
                return c
        if not self.simulate:
            res = super().create_component(comp=comp)
            self.ws[comp['rootWorkspace']]['components'].append(res)
            self.report['new_comps'] += 1
            self.report['new_comps_l'].append({'_id': res['_id'], 'name': res['name'], 'type': res['type']})
            return res
        else:
            self.report['new_comps'] += 1
            comp['_id'] = secrets.token_hex(15) # make a fake _id if when simulating
            self.report['new_comps_l'].append({'_id': comp['_id'], 'name': comp['name'], 'type': comp['typeId']})
            return(comp)

    def update_component(self, comp_id=None, comp=None):
        if comp['rootWorkspace'] not in self.ws.keys():
            self.ws[comp['rootWorkspace']] = self.get_workspace(ws_id=comp['rootWorkspace'])
        if not self.simulate:
            res = super().update_component(comp_id=comp_id, comp=comp)
            ind = next(index for index, c in
                       enumerate(self.ws[comp['rootWorkspace']]['components'])
                       if c['_id'] == comp['_id'])
            self.ws[comp['rootWorkspace']]['components'][ind] = res
            self.report['updated_comps'] += 1
            return res
        else:
            self.report['updated_comps'] += 1
            return comp

    def del_component(self, comp_id=None):
        if not self.simulate:
            res = super().del_component(comp_id=comp_id)
            self.report['del_comps'] += 1
            return res
        else:
            self.report['del_comps'] += 1
            return comp_id

    def _find_reference(self, ref=None):
        if not self.ws[ref['rootWorkspace']]['references']:
            return 0, {}
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
                if not self.simulate:
                    res = super().update_reference(ref_id=r['_id'], ref=r)
                    self.ws[ref['rootWorkspace']]['references'][ind] = res
                    self.report['updated_refs'] += 1
                    return(res)
                else:
                    self.report['updated_refs'] += 1
                    return ref
            else:
                if 'displayText' in ref.keys():
                    logging.debug(f"create_ref - cache_hit: {ref['displayText']}")
                else:
                    logging.debug(f"create_ref - cache_hit: {ref['type']}")
                self.report['cache_hit_refs'] += 1
                return r
        if not self.simulate:
            res = super().create_reference(ref=ref)
            if not self.ws[ref['rootWorkspace']]['references']:
                self.ws[ref['rootWorkspace']]['references'] = []
            self.ws[ref['rootWorkspace']]['references'].append(res)
            self.report['new_refs'] += 1
            return res
        else:
            self.report['new_refs'] += 1
            ref['_id'] = secrets.token_hex(15)  # make a fake _id if when simulating
            return ref

    def update_reference(self, ref_id=None, ref=None):
        if ref['rootWorkspace'] not in self.ws.keys():
            self.ws[ref['rootWorkspace']] = self.get_workspace(ws_id=ref['rootWorkspace'])
        if not self.simulate:
            res = super().update_reference(ref_id=ref_id, ref=ref)
            ind = next(index for index, r in
                       enumerate(self.ws[ref['rootWorkspace']]['references'])
                       if r['_id'] == ref['_id'])
            self.ws[ref['rootWorkspace']]['references'][ind] = res
            self.report['updated_refs'] += 1
            return res
        else:
            self.report['updated_refs'] += 1
            return ref

    def del_reference(self, ref_id=None):
        if not self.simulate:
            res = super().del_reference(ref_id=ref_id)
            self.report['del_refs'] += 1
            return res
        else:
            self.report['del_refs'] += 1
            return ref_id

    def get_report(self):
        logging.info('Ardoq Sync')
        for k, v in self.report.items():
            logging.info(f'{k} : {v}')
        return self.report

    def init_report(self):
        # TODO: can remove the number keys that also have lists. Original dict didn't have the list vals
        self.report = {'new_comps': 0, 'new_comps_l': [], 'updated_comps': 0, 'del_comps': 0,
                       'new_refs': 0, 'updated_refs': 0, 'del_refs': 0,
                       'cache_hit_comps': 0, 'cache_hit_refs': 0,
                       'cache_miss_comps': [], # list of components
                       'cache_miss_refs': [], # list of refs
                       'status': 'success', 'description': None}