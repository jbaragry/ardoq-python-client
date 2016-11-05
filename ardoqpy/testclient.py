#!/usr/bin/env python3

import logging
from ardoqpy import ArdoqClient, ArdoqClientException
import json
import configparser
import sys, os

configfile = "./testardoqpy.cfg"
# configfile = "./ardoqpy.cfg"
config = configparser.ConfigParser()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
#log file hardcoded in same dir for now
logger = logging.getLogger(__name__)

def ardoq_config():
    try:
        if (len(config.read(configfile)) != 1):
            raise RuntimeError("Could not read config file ", configfile)
    except:
        raise RuntimeError("could not get config file")

def main():
    ardoq_config()
    logger.debug('read config: %s %s', os.getcwd(), config.sections())
    ardoq = ArdoqClient(hosturl=config['Ardoq']['host'], token=config['Ardoq']['token'], org=config['Ardoq']['org'])
    workspaces=None
    workspace=None
    component_id=None
    model_id='54d38789e4b0dcc89b8d8e13'  # application service template in the personal space
    component_type='Application'
    #TODO move some of these to config

    print('')
    print('--- getting workspaces ---')
    try:
        workspaces = ardoq.get_workspaces(summary=True)
        ardoq.pprint(workspaces)
        for w in workspaces:
            print('name: ', w['name'], ' - id: ', w['_id'])
    except ArdoqClientException as e:
        logger.info (e)

    print('--- creating folder for test client ---')
    folder = {'name': 'ardoqpyTest', 'description': 'folder for ardoqpy test client'}
    print('creating folder for model: {}'.format(folder))
    try:
        f = ardoq.create_folder(folder)
    except ArdoqClientException as e:
        print(e)
    logger.info('created folder: %s', f)

    print('')
    print('--- create a workspace of type Application Service ---')
    new_workspace = {'description': 'workspace for ardoqpy test client', 'componentTemplate': model_id,
                     'name': 'ardoqpyAppServices', 'folder': f['_id']}
    try:
        workspace = ardoq.create_workspace(new_workspace)
        print("created workspace {} : {}".format(workspace['_id'], workspace['name']))
    except ArdoqClientException as e:
        logger.info (e)


    print('')
    print('--- getting workspace by ID ---')
    try:
        workspace = ardoq.get_workspace(ws_id=workspace['_id'])
        print("workspace " + workspace['_id'], ' : ', workspace['name'])
    except ardoqpy.ArdoqClientException as e:
        logger.info (e)

    print('')
    print('--- delete the new workspace ---')
    try:
        del_workspace = ardoq.del_workspace(workspace['_id'])
        print('delete: ', del_workspace)
    except ardoqpy.ArdoqClientException as e:
        logger.info (e)

    print('')
    print('--- create another workspace of type Application Service and put it in the same folder ---')
    new_workspace = {'description': 'workspace for ardoqpy test client', 'componentTemplate': model_id,
                     'name': 'ardoqpyAppServices', 'folder': f['_id']}
    try:
        workspace = ardoq.create_workspace(new_workspace)
        print("created workspace in a folder " + workspace['_id'], ' : ', f['name'], '/', workspace['name'])
        ws_list = []
        ws_list.append(workspace['_id'])
    except ArdoqClientException as e:
        logger.info (e)


    print('')
    print('--- get the model for the newly created workspace and show the top level componentTypes ---')
    model = ardoq.get_model(ws_id=workspace['_id'])
    for k, v, in model["root"].items():
        print ('componentType: ', v['name'], ' : typeId ', k)
        if v['name'] == component_type:
            component_id = k

    print('')
    print('--- adding a component to a selected workspace ---')
    component = {'description': 'some descript', 'parent': None, 'rootWorkspace': workspace['_id'],
                 'typeId': component_id, 'name': 'new component'}
    try:
        newcomp = ardoq.create_component(comp=component)
        print('added comp: ', newcomp['_id'], ', with name: ', newcomp['name'])
    except ArdoqClientException as e:
        logger.info (e)

    print('')
    print('--- get the newly created component---')
    try:
        comp = ardoq.get_component(ws_id = workspace['_id'], comp_id=newcomp['_id'])
        print('got comp: ', comp['_id'], ', with name: ', comp['name'])
    except ArdoqClientException as e:
        logger.info (e)

    print('')
    print('--- update the newly created component---')
    comp['name'] = 'renamed component'
    comp['description'] = "a totally new description"
    try:
        c = ardoq.update_component(comp_id=comp['_id'], comp=comp)
        print('got comp: ', c['_id'], ', with name: ', c['name'])
    except ArdoqClientException as e:
        logger.info (e)

    print('')
    print('--- adding another component to a selected workspace ---')
    component = {'description': 'target component', 'parent': None, 'rootWorkspace': workspace['_id'],
                 'typeId': component_id, 'name': 'target comp'}
    try:
        c2 = ardoq.create_component(comp=component)
        print('added 2nd comp: ', c2['_id'], ', with name: ', c2['name'])
    except ArdoqClientException as e:
        logger.info (e)

    print('')
    print('--- adding a reference beteen the components ---')
    ref = {'order': 0, 'returnValue': '', 'targetWorkspace': workspace['_id'], 'target': c2['_id'],
           'source': c['_id'], 'rootWorkspace': workspace['_id'], 'type': 2, 'description': 'new reference'}
    try:
        r = ardoq.create_reference(ref=ref)
        print('added ref: ', r['_id'], ', with descript: ', r['description'])
    except ArdoqClientException as e:
        logger.info (e)

    print('')
    print('--- update the reference  ---')
    ref['description'] = 'updated description'
    ref['type'] = 1
    ref['_id'] = r['_id']
    ref['_version'] = r['_version']
    try:
        r = ardoq.update_reference(ref_id=r['_id'], ref=ref)
        print('added ref: ', r['_id'], ', with descript: ', r['description'])
    except ArdoqClientException as e:
        logger.info (e)


if __name__ == '__main__':
    main()
