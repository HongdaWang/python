#!/usr/bin/python
#encoding=utf-8

'''
Date: 2015-3-23
Author: HD
Email: wanghongda7606@126.com
'''

import os
import sys
import time
import re
import subprocess
import pycurl
import cStringIO
from subprocess import Popen, PIPE

class Daemonize:
    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, err:
            sys.stderr.write("Fork 1 has failed --> %d--[%s]\n" % (err.errno,err.strerror))
            sys.exit(1)
        os.chdir('/')
        os.setsid()
        os.umask(0)
        try:
            pid = os.fork()
            if pid > 0:
                print "Daemon process pid %d" % pid
                sys.exit(0)
        except OSError, err:
            sys.stderr.write("Fork 2 has failed --> %d--[%s]\n" % (err.errno,err.strerror))
            sys.exit(1)
        sys.stdout.flush()
        sys.stderr.flush()
    def start_daemon(self):
        self.daemonize()
        self.run_daemon()

    def run_daemon(self):
        pass

class Watchpppd(Daemonize):
    def getlatency(self):
        basepath = "/etc/ppp/peers/"
        dict = {}
        tmplist = []
        for parent,dirnames,filenames in os.walk(basepath):
	    for filename in filenames:
	        intepath = "/etc/ppp/peers/" + filename
	        fopen = open(intepath)
	        try:
	            fread = fopen.read()
	            getip = re.findall(r'pptp (\S+) --', fread)
	        finally:
	            fopen.close()
	        vpnip = getip[0]
                latency = subprocess.Popen(''' ping -i0.5 -c5 -w5 -q %s |sed -n '4p'|awk -F" " '{print $10}'|awk -F"m" '{print $1}' ''' % vpnip, stdout = PIPE, shell = True).stdout.read()
	        if latency.strip()=='0':
		    continue
	        tmplist.append(latency)
	        dict[filename] = latency
        return tmplist,dict

    def action(self,sortedlist,dict):
        for latency in sortedlist:
            vpnname = self.getvpnname(latency,dict)
            os.system("/usr/sbin/poff")
            res = os.system("/usr/sbin/pon " + vpnname)
            res = res>>8
	    if res != 2:
	        continue
	    else:
	        break

    def getvpnname(self,latency,dict):
        for key,value in dict.items():
	    if value != latency:
	        continue
	    return key

    def quicksort(self,list,start_index,end_index):
        if start_index >= end_index:
            return
        flag = list[end_index]
        i = start_index - 1
        for j in range(start_index,end_index):
            if list[j] > flag:
                pass
            else:
                i += 1
                tmp = list[i]
                list[i] = list[j]
                list[j] = tmp
        tmp = list[end_index]
        list[end_index] = list[i+1]
        list[i+1] = tmp
        middle = i+1
        self.quicksort(list,start_index,middle-1)
        self.quicksort(list,middle+1,end_index)

    def watch(self):
	res = self.vpnstatus()
        if not res:
            (list,dict) = self.getlatency()
            self.quicksort(list,0,len(list)-1)
            self.action(list,dict)
	
    def vpnstatus(self):
	URL = 'www.google.com'
        buf = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, URL)
        c.setopt(pycurl.TIMEOUT, 10)
        c.setopt(pycurl.WRITEFUNCTION, buf.write)
        try:
            c.perform()
        except Exception, e:
            http_code = c.getinfo(c.HTTP_CODE)
            c.close()
            buf.close()
            return http_code
        http_code = c.getinfo(c.HTTP_CODE)
        c.close()
        buf.close()
	return http_code

    def run_daemon(self):
	while 1:
	    self.watch()
            time.sleep(120)
if __name__ == "__main__":
    watchdog = Watchpppd()
    watchdog.start_daemon()
