#!/usr/bin/python
#encoding=utf-8

'''
Date: 2015-4-8
Author: HD
Email: wanghongda7606@126.com
'''

import os
import sys
import re
from fabric.colors import *
from fabric.api import *

env.user = 'root'
env.password = '123456'
env.hosts = ['10.10.10.10']

env.package_dir = 'zabbix_agent'
env.logical_dir = 'logical'
env.login_dir = 'login'
env.remote_path = '/home/install/'
env.zabbix_agent_path = '/usr/local/zabbix_agent/'

def check_ip(ip):
    addr = ip.strip().split('.')
    print addr
    if len(addr) != 4:
        print '%s is invalid!' % ip
        sys.exit()
    for i in range(4):
        try:
            addr[i] = int(addr[i])
        except:
            print '%s is invalid! ip is not int' % ip
            sys.exit()
        if addr[i] <= 254 and addr[i] >= 0:
            pass
        else:
            print '%s is invalid! ip is not in 0-254' % ip
            sys.exit()
        i+=1
    else:
        return True

def update_file(type):
    path = './' + type + '/zabbix_agentd.conf'
    new_name = prompt('Please input hostname:', default='')
    if new_name == '':
        print 'error: Hostname is invalid!'
        sys.exit()
    if os.path.exists(path):
        try:
            fopen = open(path)
            fread = fopen.read()
            old_name = re.findall(r'Hostname=(\S+)\n', fread)[0]
            data = re.sub(old_name, new_name, fread)
        finally:
            fopen.close()
        try:
            fopen = open(path, 'wb')
            fopen.write(data)
        finally:
            fopen.close()
    else:
        print 'File %s is not exists!'
        sys.exit()

def install():
    print yellow('Start put package...')
    with settings(warn_only = True):
        run('mkdir -p %s' % (env.remote_path))
    with settings(warn_only = True):
        result = put(env.package_dir, env.remote_path)
    if result.failed and no ('Put %s to %s failed, Continue[Y/N]?' % (env.package_dir, env.remote_path)):
        abort('Aborting task!')
    with cd(env.remote_path + env.package_dir):
        run('sh install.sh')
    print green('Install Zabbix_agent success!')

@task
def logic():
    install()
    print yellow('Start configure zabbix_agent of logical server...')

    with settings(warn_only = True):
        result = put(env.logical_dir + '/scripts', env.zabbix_agent_path)
    if result.failed and no ('Put %s to %s failed, Continue[Y/N]?' % (env.logical_dir + '/scripts', env.zabbix_agent_path)):
        abort('Aborting task!')

    update_file('logical')
    with cd(env.zabbix_agent_path + 'etc'):
        run('mv zabbix_agentd.conf zabbix_agentd.conf.bak')
    with settings(warn_only = True):
        result = put(env.logical_dir + '/zabbix_agentd.conf', env.zabbix_agent_path + 'etc')
    if result.failed and no ('Put %s to %s failed, Continue[Y/N]?' % (env.logical_dir + '/zabbix_agentd.conf', env.zabbix_agent_path + 'etc')):
        abort('Aborting task!')
    else:
        run('service zabbix_agentd start')
        print green('Configure logical-server success!')

@task
def login():
    install()
    print yellow('Start configure zabbix_agent of login server...')

    update_file('login')
    with cd(env.zabbix_agent_path + 'etc'):
        run('mv zabbix_agentd.conf zabbix_agentd.conf.bak')
    with settings(warn_only = True):
        result = put(env.login_dir + '/zabbix_agentd.conf', env.zabbix_agent_path + 'etc')
    if result.failed and no ('Put %s to %s failed, Continue[Y/N]?' % (env.login_dir + '/zabbix_agentd.conf', env.zabbix_agent_path + 'etc')):
        abort('Aborting task!')
    else:
        run('service zabbix_agentd start')
        print green('Configure login-server success!')
