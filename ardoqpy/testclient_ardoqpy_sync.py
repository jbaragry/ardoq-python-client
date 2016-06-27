from ardoqpy_sync import ArdoqSyncClient

ardoqs = ArdoqSyncClient(hosturl='https://app.ardoq.com', token='<mytoken>', org='ardoq')

ws = ardoqs.get_workspaces()
print(ws)