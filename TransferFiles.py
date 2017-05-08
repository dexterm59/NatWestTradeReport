import paramiko
import datetime
from datetime import datetime
import argparse
import logging
import os.path
import configparser

report_time = datetime.now()
report_extension = report_time.strftime("%Y%m%d-%H%M%S")

parser = argparse.ArgumentParser(description='Test argument parser with filenames.')

parser.add_argument('config', help='config file for creds, dest, etc')


args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config)
config.sections()

#see if there is a file to transfer

#assign filename to file (may need a loop to xfer multiple files)

input_directory = config['natwest']['inputdirectory']
server = config['natwest']['hostname']
port = config['DEFAULT']['port']
user = config['natwest']['username']
pw = config['natwest']['password']


client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(server, username=user, password=pw)

scp = SCPClient(client.get_transport())

scp.put(filename)
