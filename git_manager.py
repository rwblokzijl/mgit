#!/usr/bin/env python3

import argparse
import os
import paramiko
import re
import subprocess
import sys
import time

def check_output(*args, **kwargs):
    return subprocess.check_output(*args, **kwargs).decode('utf-8').strip()

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def regex_type(s, pat=re.compile(r"[a-f0-9A-F]{32}")):
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s

def ip_address(s):
    return regex_type(s, pat=re.compile(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"))

def command(s):
    if s in ["init", "show", "list"]:
        return s
    raise argparse.ArgumentTypeError

parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
parser.add_argument('command', action='store', help='command', type=command)
parser.add_argument('directory', action='store', nargs='?', help='directory to act on', default=".", type=str)
parser.add_argument('-y', action='store_true', help='integrate previously existing repos')
#parser.add_argument('-se', action='store_true', help='enable service')
#parser.add_argument('-sd', action='store_true', help='disable service')
#parser.add_argument('-s', '--script', action='store', help='name of script', nargs='+', type=str)

args = parser.parse_args()

# print (args.directory)

if(args.directory.strip("/") == "."):
    PROJECT_NAME = os.path.basename(os.getcwd())
    PROJECT_DIR = '/data/git/projects/' + PROJECT_NAME
else:
    PROJECT_NAME = os.path.basename(args.directory)
    PROJECT_DIR = '/data/git/projects/' + PROJECT_NAME
LOCAL_DIR = args.directory.strip('/')

ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.25')

### IS GIT ALREADY INITED
def git_exist_local():
    return os.path.isdir(LOCAL_DIR+'/.git')

### Does remote git already exist
def git_exist_remote():
    stdin, stdout, stderr = ssh.exec_command('[ -d "'+PROJECT_DIR+'" ]')
    if stdout.channel.recv_exit_status() is 0:
        return True
    else:
        return False

### Create remote
def create_remote():
    print("Creating remote: " + PROJECT_DIR)
    stdin, stdout, stderr = ssh.exec_command('mkdir ' + PROJECT_DIR)
    if stdout.channel.recv_exit_status() is not 0: # Blocking call
        print("ERROR: Remote folder already exists, not creating remote repo")
        return False # dir already exists
    stdin, stdout, stderr = ssh.exec_command('git init --bare ' + PROJECT_DIR)
    if stdout.channel.recv_exit_status() is not 0: # Blocking call
        print("ERROR: Could not create remote repo for some reason")
        return False
    return True

### Create Local
def create_local():
    if not os.path.isdir(LOCAL_DIR):
        print("creating a new git project in " + LOCAL_DIR)
        os.mkdir(LOCAL_DIR)
    subprocess.call(["git", "init", LOCAL_DIR])

def add_remote():
    print("Adding remote ")
    subprocess.call(["git", "-C", LOCAL_DIR, "remote", "add", "origin", "bloodyfool@git.blokzijl.family:" + PROJECT_DIR])

### List status
def list_status():
    if git_exist_local():
        print(check_output(["git", "-C", LOCAL_DIR, "remote", "-v"]))
    else:
        print(LOCAL_DIR + "is not the root of a git directory")

def init():
    if git_exist_local():
        if not args.y:
            if not query_yes_no("The local repo already exists, do you want to add it to the local folder?"):
                exit()
    else:
        create_local()

    if git_exist_remote():
        if not args.y:
            if not query_yes_no("The remote repo already exists, do you want to add it to the local folder?"):
                exit()
    else:
        create_remote()

    add_remote()

if args.command == "init":
    init()
elif args.command == "show":
    list_status()
elif args.command == "list":
    list_status()


