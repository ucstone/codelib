#/usr/bin/env python
#coding:utf-8
import requests
import re
'''
查询IP地址归属地，得访问IP138.COM这个站点。
'''

headers = {
'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
"Accept": "text/html,application/xhtml+xml-learn,application/xml-learn;q=0.9,*/*;q=0.8",
"Accept-Encoding" : "gzip, deflate",
"Referer" : "http://www.ip138.com/"
}

reip = re.compile(r'<li>(.*?)</li>')

with open(r"d:\jihe.txt") as ips: #open里是ip文件
    for ip in ips:
        r = requests.get('http://www.ip138.com/ips1388.asp?ip='+ip.strip()+'&action=2', headers=headers)
        seg = reip.findall(r.content)
        print ip.strip(),'---',seg[0]
