#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Date: 2015-3-11
Author: HD
Email: wanghongda7606@126.com
'''

import json
import urllib2
import sys
class zabbixtools:
    def __init__(self):
        self.url = "http://10.10.3.202/zabbix/api_jsonrpc.php"
        self.header = {"Content-Type": "application/json"}
        self.authID = self.user_login()
    def user_login(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "user": "TEXT",
                        "password": "TEXT"
                        },
                    "id": 0
                    })
        request = urllib2.Request(self.url,data)
        for key in self.header:#####for loop add headers,simulation browser to post information#####
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print "Auth Failed, Please Check Your Name And Password:",e.code
        else:
            response = json.loads(result.read())
            result.close()
            authID = response['result']
            return authID
    def get_data(self,data):
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except urllib2.URLError as e:
            if hasattr(e, "reason"):
                print "We failed to reach a server."
                print "Reason: ", e.reason
            elif hasattr(e, "code"):
                print "The server could not fulfill the request."
                print "Error code: ", e.code
            return 0
        else:
            response = json.loads(result.read())
            result.close()
            return response
    def host_specific_status(self):
        hostip = raw_input("Enter Your Check Host IP:")
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output":["hostid","name","status","ip"],
                        "selectInterfaces": ["interfaceid","ip"],
                        "filter": {"ip": hostip}
                        },
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)['result']
        if (res != 0) and (len(res) != 0):
            #for host in res:
            host = res[0]
            if host["status"] == "0":
                print "Host_Name:",host["name"], "Monitoring!"
                return host["hostid"]
            elif host["status"] == "1":
                print "Host_Name:",host["name"], "NOT Monitoring!"
                return host["hostid"]
        else:
            print "Get Host Error or cannot find this host,please check !"
            return 0        
    def host_del(self):
        hostip = raw_input("Enter Your Check Host IP:")
        hostid = self.host_get(hostip)
        if hostid == 0:
            print "This host cannot find in zabbix,please check it !"
            sys.exit()
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.delete",
                    "params": [{"hostid": hostid}],
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)["result"]
        if "hostids" in res.keys():
            print "Delet Host:%s success !", hostip
        else:
            print "Delet Host:%s failure !", hostip
    def hostgroup_get(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.get",
                    "params": {
                        "output": "extend",
                        },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)
        if "result" in res.keys():
            res = res["result"]
            if (res !=0) or (len(res) != 0):
                print "Number Of Group: ", len(res)
                for host in res:
                    print "\t","HostGroup_id:",host['groupid'],"\t","HostGroup_Name:",host['name']
        else:
            print "Get HostGroup Error,please check !"
    def template_get(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "template.get",
                    "params": {
                        "output": "extend",
                        },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)#['result']
        if "result" in res.keys():
            res = res["result"]
            if (res !=0) or (len(res) != 0):
                print "Number Of Template: ", len(res)
                for host in res:
                    print "\t","Template_id:",host['templateid'],"\t","Template_Name:",host['name']
                print
        else:
            print "Get Template Error,please check !"
    def host_create(self):
        hostip = raw_input("Enter your Host IP:")
        groupid = raw_input("Enter your Group ID:")
        templateid = raw_input("Enter your Tempate ID:")
        g_list=[]
        t_list=[]
        for i in groupid.split(","):
            var = {}
            var["groupid"] = i
            g_list.append(var)
        for i in templateid.split(","):
            var = {}
            var["templateid"] = i
            t_list.append(var)
        if hostip and groupid and templateid:
            data = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "host.create",
                        "params": {
                            "host": hostip,
                            "interfaces": [
                                {
                                    "type": 1,
                                    "main": 1,
                                    "useip": 1,
                                    "ip": hostip,
                                    "dns": "",
                                    "port": "10050"
                                }
                            ],
                            "groups": g_list,
                            "templates": t_list,
                    },
                        "auth": self.authID,
                        "id": 1,
                        })
            res = self.get_data(data,hostip)
            if "result" in res.keys():
                res = res["result"]
                if "hostids" in res.keys():
                    print "Create host success"
            else:
                print "Create host failure: %s", res["error"]["data"]
        else:
            print "Enter Error: ip or groupid or tempateid is NULL,please check it !"
    def hostlist_get(self):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": ["hostid", "name", "status"],
                    "selectInterfaces": ["interfaceid", "ip"]},
                "auth": self.authID,
                "id": 1
            })
        res = self.get_data(data)["result"]
        print "Number Of Hosts: ", len(res)
        if (res != 0) and (len(res) != 0):
            for host in res:
                if host["status"] == "0":
                    print "\t", "Host ID:", host["hostid"], "\t", "Host Name:", host["name"], "\t", "Monitoring!"
                elif host["status"] == "1":
                    print "\t", "Host ID:", host["hostid"], "\t", "Host Name:", host["name"], "\t", "NOT Monitoring!"
        else:
            print "Get Host Error or cannot find this host,please check !"
            return 0
def main():
    test = zabbixtools()
    test.template_get()
    test.hostgroup_get()
    test.hostlist_get()
    #test.host_specific_status()
    #test.host_del()
    #test.host_create()
if __name__ == "__main__":
    main()
