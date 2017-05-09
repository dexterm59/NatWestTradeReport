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


input_dir = config['natwest']['inputdirectory']
processed_dir = config['natwest']['processeddirectory']
remote_dir = config['natwest']['depositdirectory']
server = config['natwest']['hostname']
port = config['DEFAULT']['port']
user = config['natwest']['username']
pw = config['natwest']['password']
logfile = config['natwest']['logfile']
loglevel = config['natwest']['loglevel']

logging.basicConfig(filename=logfile, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=numeric_level)
logging.info("started")

logging.info("Script running with: input_dir: %s, processed_dir: %s, remote_dir: %s, server: %s, port: %s, user: %s, password: XX, logfile: %s, loglevel: %s",
             input_dir,
             processed_dir,
             remote_dir,
             server,
             port,
             user,
             logfile, loglevel)


#see if there is a file to transfer

files = os.listdir(input_dir)
if not files:
    logging.info("No files to transmit. Exiting...")
    exit(0)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=user, password=pw)
sftp = ssh.open_sftp()
sftp.chdir(remote_dir)

file_count = 0
for file in files:
    localfile = input_dir + file
    sftp.put(localfile, file)
    os.rename(localfile, processed_dir + file)
    logging.info("Deposited %s in %s directory", localfile, remote_dir)
    file_count += 1

logging.info("End of run, %d files transferred.", file_count)

sftp.close()

