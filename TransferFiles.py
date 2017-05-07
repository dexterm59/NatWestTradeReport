import paramiko
import os

#see if there is a file to transfer

#assign filename to file (may need a loop to xfer multiple files)

server ='server name'
port = 22
user = 'user name'
pw = 'password'


client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(remote_host, username=user, password=pw)

scp = SCPClient(client.get_transport())

scp.put(filename)
