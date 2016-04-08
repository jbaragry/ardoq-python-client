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

    print('')
    print('--- getting workspaces ---')
    workspaces = ardoq.get_workspaces()
    # print (json.dumps(workspaces, sort_keys=True, indent=4))
    for w in workspaces:
        print('name: ', w['name'], ' - id: ', w['_id'])

    print('--- create a workspace of type Application Service ---')
    new_workspace = {'description': 'workspace for python test client', 'componentModel': '56f2b68672fa6d045996f74a', 'name': 'wsPythonClient'}
    workspace = ardoq.create_workspace(new_workspace)
    # print (json.dumps(python_ws, sort_keys=True, indent=4))
    print("created workspace " + workspace['_id'], ' : ', workspace['name'])

    print('')
    print('--- getting workspace by ID ---')
    workspace = ardoq.get_workspace(ws_id=workspace['_id'])
    print("workspace " + workspace['_id'], ' : ', workspace['name'])

    print('')
    print('--- delete the new workspace ---')
    del_workspace = ardoq.del_workspace(workspace['_id'])
    print('delete: ', del_workspace)

    print('--- create another workspace of type Application Service ---')
    new_workspace = {'description': 'workspace for python test client', 'componentModel': '56f2b68672fa6d045996f74a', 'name': 'wsPythonClient'}
    workspace = ardoq.create_workspace(new_workspace)
    # print (json.dumps(python_ws, sort_keys=True, indent=4))
    print("created workspace " + workspace['_id'], ' : ', workspace['name'])

    print('')
    print('--- getting model and show the top level componentTypes ---')
    model = ardoq.get_model(ws_id=workspace['_id'])
    for k, v, in model["root"].items():
        print ('componentType: ', v['name'], ' : typeId ', k)

    print('')
    print('--- adding a component to a selected workspace ---')
    component = {'description': 'some descript', 'parent': None, 'rootWorkspace': workspace['_id'], 'typeId': 'p1458752640732', 'name': 'another comp'}
    newcomp = ardoq.create_component(component)
    # print (json.dumps(comp, sort_keys=True, indent=4))
    print('added comp: ', newcomp['_id'], ', with name: ', newcomp['name'])

    print('')
    print('--- get the newly created component---')
    comp = ardoq.get_component(comp_id=newcomp['_id'])
    print('got comp: ', comp['_id'], ', with name: ', comp['name'])

if __name__ == '__main__':
    main()
