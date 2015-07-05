#!/usr/bin/python
#encoding=utf-8

'''
Date: 2015-5-16
Author: HD
Email: wanghongda7606@126.com
'''

import os
import sys
import re
import subprocess
from subprocess import Popen, PIPE
from fabric.colors import *
from fabric.api import *

env.user = 'root'
env.password = '123456'
env.roledefs = {             #define servers ip
    'loginservers': ['10.10.10.11'],
    'logicservers': ['10.10.10.10']
}
env.RDS = 'test.mysql.rds.aliyuncs.com'
env.accesskeyid = 'abcdef'
env.accesskeysecret = '111111'

def update_file(new_ip, path):
    if os.path.exists(path):
        try:
            fopen = open(path)
            fread = fopen.read()
            data = re.sub(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', new_ip, fread)
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

@roles('loginservers')
def login():
    print yellow('Starting LOGIN task...')

#Initializing system environment

    print yellow('Initializing system environment...')

    result = put('./login/aliwww.tar.gz', '~/')
    if result.failed and no ('Put package failed, Continue[Y/N]?'):
        abort('Aborting task!')
    else:
        with cd('~/'):
            run('tar -zxvf aliwww.tar.gz')
        with cd('~/sh-1.4.1'):
            run('sh ./install.sh')

    with settings(warn_only = True):
        result = put('./login/node-v0.12.2.tar.gz', '~/')
    if result.failed and no ('Put package failed, Continue[Y/N]?'):
        abort('Aborting task!')
    else:
        with cd('~/'):
            run('tar -zxvf node-v0.12.2.tar.gz')
    with cd('~/node-v0.12.2'):
        run('./configure')
        run('make && make install')

    print green('Initializing system environment Done!')

#configure config.inc

    env.logic_in_ip = get_ip(ifname = 'eth0')
    update_file(env.logic_in_ip, path = './login/yunhai/config.inc')
    old_RDS = subprocess.Popen(''' cat ./login/yunhai/config.inc|grep db_config|awk -F "'" '{print $4}'|tr -d '\n' ''', stdout = PIPE, shell = True).stdout.read()
    with hide('warnings', 'running', 'stdout', 'stderr'):
        local(' sed -i "s/%s/%s/g" ./login/yunhai/config.inc ' % (old_RDS, env.RDS))

#configure CreateDatebase.php

    old_accesskeyid = subprocess.Popen(''' cat ./login/yunhai/aliyun/CreateDatabase.php |grep accessKeyId|awk -F '"' '{print $2}'|tr -d '\n' ''', stdout = PIPE, shell = True).stdout.read()
    old_accesskeysecret = subprocess.Popen(''' cat ./login/yunhai/aliyun/CreateDatabase.php |grep accessKeySecret|awk -F '"' '{print $2}'|tr -d '\n' ''', stdout = PIPE, shell = True).stdout.read()
    with hide('warnings', 'running', 'stdout', 'stderr'):
        local(' sed -i "s/%s/%s/g" ./login/yunhai/aliyun/CreateDatabase.php ' % (old_accesskeyid, env.accesskeyid))
        local(' sed -i "s/%s/%s/g" ./login/yunhai/aliyun/CreateDatabase.php ' % (old_accesskeysecret, env.accesskeysecret))

#configure db_config.sh

    old_RDS = subprocess.Popen(''' cat ./login/aliyun_sql/db_config.sh|grep host|awk -F '=' '{print $2}'|tr -d '\n' ''', stdout = PIPE, shell = True).stdout.read()
    with hide('warnings', 'running', 'stdout', 'stderr'):
        local(' sed -i "s/%s/%s/g" ./login/aliyun_sql/db_config.sh ' % (old_RDS, env.RDS))

#put packages

    with lcd('/task/yhxz/login'):
        local('tar -zcvf yunhai.tar.gz ./yunhai')
    with settings(warn_only = True):
        result = put('./login/yunhai.tar.gz', '/alidata/www')
    if result.failed and no ('Put package failed, Continue[Y/N]?'):
        abort('Aborting task!')
    else:
        with cd('/alidata/www'):
            run('tar -zxvf yunhai.tar.gz')

    with lcd('/task/yhxz/login'):
        local('tar -zcvf aliyun_sql.tar.gz ./aliyun_sql')
    with settings(warn_only = True):
        result = put('./login/aliyun_sql.tar.gz', '~/')
    if result.failed and no ('Put package failed, Continue[Y/N]?'):
        abort('Aborting task!')
    else:
        with cd('~/'):
            run('tar -zxvf aliyun_sql.tar.gz')

    with settings(warn_only = True):
        result = put('./login/yunhai.conf', '/alidata/server/nginx/conf/vhosts')
    if result.failed and no ('Put package failed, Continue[Y/N]?'):
        abort('Aborting task!')
    else:
        run('/etc/init.d/nginx restart')

    print yellow('Cleaning up...')

    local('rm -rfv ./login/yunhai.tar.gz')
    local('rm -rfv ./login/aliyun_sql.tar.gz')
    with cd('/alidata/www'):
        run('rm -rfv yunhai.tar.gz')
    with cd('~/'):
        run('rm -rfv aliyun_sql.tar.gz')
        run('rm -rfv node-v0.12.2')
        run('rm -rfv node-v0.12.2.tar.gz')

    print green('LOGIN task Done!')

@roles('logicservers')
def get_ip(ifname):
    ip = run(''' ifconfig %s|grep 'inet addr:'|awk -F ' ' '{print $2}'|awk -F ':' '{print $2}'|tr -d '\n' ''' % ifname)
    return ip

@roles('logicservers')
def logic():
    print yellow('Starting LOGIC task...')
    with hide('running', 'stdout', 'stderr'):
        env.logic_in_ip = get_ip(ifname = 'eth0')
        env.logic_ex_ip = get_ip(ifname = 'eth1')


#configure DB

    update_file(env.logic_in_ip, path = './logic/yunhai/DB/etc/bind.conf')
    old_RDS = subprocess.Popen(''' cat ./logic/yunhai/DB/etc/bench.conf |grep DB_IP|awk -F ' ' '{print $2}'|tr -d '\n' ''', stdout = PIPE, shell = True).stdout.read()
    with hide('warnings', 'running', 'stdout', 'stderr'):
        local(' sed -i "s/%s/%s/g" ./logic/yunhai/DB/etc/bench.conf ' % (old_RDS, env.RDS))
    print green('Configure DB OK!')

#configure gateway

    update_file(env.logic_in_ip, path = './logic/yunhai/gateway/etc/bind.conf')
    update_file(env.logic_in_ip, path = './logic/yunhai/gateway/etc/bench.conf')
    print green('Configure Gateway OK!')

#configure online

    update_file(env.logic_ex_ip, path = './logic/yunhai/online/etc/bind.conf')
    update_file(env.logic_in_ip, path = './logic/yunhai/online/etc/bench.conf')
    print green('Configure Online OK!')

#configure proxy

    update_file(env.logic_in_ip, path = './logic/yunhai/proxy/etc/bind.conf')
    update_file(env.logic_in_ip, path = './logic/yunhai/proxy/etc/route.xml')
    print green('Configure Proxy OK!')

#put files

    with lcd('/task/yhxz/logic'):
        local('tar -zcvf yunhai.tar.gz ./yunhai')
    with settings(warn_only = True):
        run('mkdir -p /alidata')
        result = put('./logic/yunhai.tar.gz', '/alidata')
    if result.failed and no ('Put package failed, Continue[Y/N]?'):
        abort('Aborting task!')
    else:
        local('rm -rfv ./logic/yunhai.tar.gz')
    with cd('/alidata'):
        run('tar -zxvf yunhai.tar.gz')
        run('rm -rfv yunhai.tar.gz')
    print green('LOGIC task Done!')
