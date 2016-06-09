#!/usr/bin/env python3

import ardoqpy
import json
import configparser
import sys, os

configfile = "./testardoqpy.cfg"
# configfile = "./ardoqpy.cfg"
config = configparser.ConfigParser()

def get_config():
    try:
        if (len(config.read(configfile)) != 1):
            raise RuntimeError("Could not read config file ", configfile)
    except:
        raise RuntimeError("could not get config file")

def main():
    get_config()
    print('read config: ', os.getcwd(), ' ', config.sections())
    ardoq = ardoqpy.ArdoqClient(hosturl=config['Ardoq']['host'], token=config['Ardoq']['token'], org=config['Ardoq']['org'])
    workspaces=None
    workspace=None
    component_id=None
    model_id='54d38789e4b0dcc89b8d8e13'  # application service template in the personal space
    component_type='Application'
    #TODO move some of these to config

    print('')
    print('--- getting workspaces ---')
    try:
        workspaces = ardoq.get_workspaces()
        # print (json.dumps(workspaces, sort_keys=True, indent=4))
        for w in workspaces:
            print('name: ', w['name'], ' - id: ', w['_id'])
    except ardoqpy.ArdoqClientException as e:
        print (e)

    ''' need to wait for api changes for new models. Test client must wait until ardoq has done the changes
    print('')
    print('--- create a workspace of type Application Service ---')
    new_workspace = {'description': 'workspace for python test client', 'componentModel': model_id, 'name': 'wsPythonTestClient'}
    try:
        workspace = ardoq.create_workspace(new_workspace)
        # print (json.dumps(python_ws, sort_keys=True, indent=4))
        print("created workspace " + workspace['_id'], ' : ', workspace['name'])
    except ardoqpy.ArdoqClientException as e:
        print (e)


    print('')
    print('--- getting workspace by ID ---')
    try:
        workspace = ardoq.get_workspace(ws_id=workspace['_id'])
        print("workspace " + workspace['_id'], ' : ', workspace['name'])
    except ardoqpy.ArdoqClientException as e:
        print (e)

    print('')
    print('--- delete the new workspace ---')
    try:
        del_workspace = ardoq.del_workspace(workspace['_id'])
        print('delete: ', del_workspace)
    except ardoqpy.ArdoqClientException as e:
        print (e)
    '''

    model_id='5759c89572fa6d16fcc7f439'
    print('')
    print('--- create another workspace of type Application Service and put it in a folder ---')
    new_workspace = {'description': 'workspace for python test client in a folder', 'componentModel': model_id, 'name': 'wsPythonTestClientInFolder'}
    try:
        folder = {'name':'ardoqpyTestClientFolder', 'description': 'testfolderclient description'}
        f = ardoq.create_folder(folder)
        workspace = ardoq.create_workspace(new_workspace)
        # print (json.dumps(python_ws, sort_keys=True, indent=4))
        print("created workspace in a folder " + workspace['_id'], ' : ', f['name'], '/', workspace['name'])
        ws_list = []
        ws_list.append(workspace['_id'])
        fres = ardoq.move_workspace(folder_id = f['_id'], ws_list = ws_list)
    except ardoqpy.ArdoqClientException as e:
        print (e)


    print('')
    print('--- getting model and show the top level componentTypes ---')
    model = ardoq.get_model(ws_id=workspace['_id'])
    for k, v, in model["root"].items():
        print ('componentType: ', v['name'], ' : typeId ', k)
        if v['name'] == component_type:
            component_id = k

    print('')
    print('--- adding a component to a selected workspace ---')
    component = {'description': 'some descript', 'parent': None, 'rootWorkspace': workspace['_id'], 'typeId': component_id, 'name': 'another comp'}
    try:
        # newcomp = ardoq.create_component(ws_id=workspace['_id'], comp=component)
        newcomp = ardoq.create_component(comp=component)
        # print (json.dumps(comp, sort_keys=True, indent=4))
        print('added comp: ', newcomp['_id'], ', with name: ', newcomp['name'])
    except ardoqpy.ArdoqClientException as e:
        print (e)

    print('')
    print('--- get the newly created component---')
    try:
        comp = ardoq.get_component(ws_id = workspace['_id'], comp_id=newcomp['_id'])
        print('got comp: ', comp['_id'], ', with name: ', comp['name'])
    except ardoqpy.ArdoqClientException as e:
        print (e)

    print('')
    print('--- update the newly created component---')
    comp['name'] = 'source comp'
    comp['description'] = "a totally new description"
    try:
        c = ardoq.update_component(ws_id=workspace['_id'], comp_id=comp['_id'], comp=comp)
        print('got comp: ', c['_id'], ', with name: ', c['name'])
    except ardoqpy.ArdoqClientException as e:
        print (e)

    print('')
    print('--- adding another component to a selected workspace ---')
    component = {'description': 'target component', 'parent': None, 'rootWorkspace': workspace['_id'], 'typeId': component_id, 'name': 'target comp'}
    try:
        # newcomp = ardoq.create_component(ws_id=workspace['_id'], comp=component)
        c2 = ardoq.create_component(comp=component)
        # print (json.dumps(comp, sort_keys=True, indent=4))
        print('added comp: ', c2['_id'], ', with name: ', c2['name'])
    except ardoqpy.ArdoqClientException as e:
        print (e)

    print('')
    print('--- adding a reference to a selected workspace ---')
    ref = {'order': 0, 'returnValue': '', 'targetWorkspace': workspace['_id'], 'target': c2['_id'],
           'source': c['_id'], 'rootWorkspace': workspace['_id'], 'type': 2, 'description': 'new ref'}
    try:
        # newcomp = ardoq.create_component(ws_id=workspace['_id'], comp=component)
        r = ardoq.create_reference(ref=ref)
        # print (json.dumps(comp, sort_keys=True, indent=4))
        print('added ref: ', r['_id'], ', with descript: ', r['description'])
    except ardoqpy.ArdoqClientException as e:
        print (e)

    print('')
    print('--- update the reference  ---')
    ref['description'] = 'updated description'
    ref['type'] = 1
    ref['_id'] = r['_id']
    ref['_version'] = r['_version']
    try:
        # newcomp = ardoq.create_component(ws_id=workspace['_id'], comp=component)
        r = ardoq.update_reference(ref_id=r['_id'], ref=ref)
        # print (json.dumps(comp, sort_keys=True, indent=4))
        print('added ref: ', r['_id'], ', with descript: ', r['description'])
    except ardoqpy.ArdoqClientException as e:
        print (e)

if __name__ == '__main__':
    main()
