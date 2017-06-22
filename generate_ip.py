#-*- coding:utf-8 -*-
#!/usr/bin/python
'''
使用Python3 才能运行正常
'''
import ipaddress

with open(r'd:\i.txt','r') as lines:
    with open(r'd:\iiiii-ip.txt', 'w+') as ip_txt:
        line = lines.readlines()
        for i in line:
            net = ipaddress.ip_network(i.strip())
            for ip in net:
                print(ip)
                ip_txt.write(str(ip)+'\n')
