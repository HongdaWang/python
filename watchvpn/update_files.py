#!/usr/bin/python
#encoding=utf-8

'''
Date: 2015-3-11
Author: HD
Email: wanghongda7606@126.com
'''
import os
import sys
import re
import urllib
import urllib2
import cookielib

def get_real_url(url):
    req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept':'text/html;q=0.9,*/*;q=0.8',
    'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding':'gzip',
    'Connection':'close',
    'Referer':None
    }
    req = urllib2.Request(url,None,req_header)
    resp = urllib2.urlopen(req)
    html = resp.read()
    url = re.search(r'<base href="(\S+)" />', html).group(1)
    return url

def get_ips(url):
    cookie = cookielib.CookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cookie_handler)
    header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36'}

    data = {'username':'jack', 'passwd':'123456', 'Submit':'登录', 'option':'com_user', 'task':'login'}
    endata = urllib.urlencode(data)
    req_login = urllib2.Request(url, urllib.urlencode(data), header)
    page_login = opener.open(req_login).read()
    login_status = re.search(r'用户名和密码不匹配', page_login)

    if login_status == None:
        req_xianlu = urllib2.Request(url+'xianlu.html', headers = header)
        page_xianlu = opener.open(req_xianlu).read()
        ips = re.findall(r'美国高速-(\S+)</center></td>[^.]+<center>(\S+)</center></td>', page_xianlu)
        return ips
    else:
        print 'Login Failed'
        sys.exit()

def update_files(list):
    for a in list:
        path = '/etc/ppp/peers/us'+a[0]
        new_ip = a[1]
        if os.path.exists(path):
            try:
                fopen = open(path)
                fread = fopen.read()
                old_ip = re.findall(r'pptp (\S+) --', fread)[0]
                data = re.sub(old_ip, new_ip, fread)
            finally:
                fopen.close()
            try:
                fopen = open(path, 'wb')
                fopen.write(data)
            finally:
                fopen.close()
        else:
            continue

if __name__ == "__main__":
    url = 'http://gjsq.link/'
    url = get_real_url(url)
    list = get_ips(url)
    update_files(list)
