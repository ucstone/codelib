#!/usr/bin/env python
#coding:utf-8
import json
import requests as req
import urllib
import sys

def get_token():
    payload = {"username":"你zoomeye账号","password":"你zoomeye密码"}
    res = req.post('https://api.zoomeye.org/user/login',data=json.dumps(payload))
    return json.loads(res.text)['access_token']

def get_result(resource='web', dork='struts2', page=1):
    targetList = []
    payload = {"Authorization": "JWT " + get_token()}
    path = '{}/search?query={}&page={}&facet=app,os'.format(resource, urllib.quote(dork), page)
    uri = "/".join(['https://api.zoomeye.org', path])
    response = req.get(uri, headers=payload)
    search_res = json.loads(response.content)
    print response.url
    try:
        pages = getPageNum(int(search_res['total']))
    except Exception as e:
        print "Error Code: %s" % response.status_code
        print "URL: {}, Error MSG: {}, Tips:{} ".format(search_res['url'], search_res['message'],  search_res['error'])
        sys.exit()
    for i in xrange(pages):
        res = req.get(uri, headers=payload)
        search_res = json.loads(res.content)
        print "Get page " + str(i + 1) + " info ..."
        if res.status_code == 200:
            # 打印所有匹配项
            if resource == 'host':
                for match in search_res['matches']:
                    res_line = match['ip'] + ':' + str(match['portinfo']['port']), '\t', match['geoinfo']['isp']
                    print res_line
                    targetList.append(res_line)
            elif resource == 'web':
                for match in search_res['matches']:
                    res_line = match['ip'][0] + ' ' + match['title'] + ' ' + 'http://' + match['site']
                    print res_line
                    targetList.append(res_line)
        else:
            print "Error Code: %s" % res.status_code
            print "URL: {}, Error MSG: {}, Tips:{} ".format(search_res['url'], search_res['message'], search_res['error'])
    print "Save Result..."
    save_result(targetList)
    print "Save Done..."

def save_result(targetList):
    with open('result.txt', 'a') as f:
        for eachTarget in targetList:
            # print type(eachTarget.encode('utf-8'))
            f.writelines(eachTarget.encode('utf-8')+'\n')
            # print eachTarget

def getPageNum(total):
    if total == 0:
        print "No result, exit.."
        sys.exit()
    page = total/10
    if total%10 == 0:
        return page
    return page + 1

# resource为搜索类型，dork为搜索的关键字，默认为web类型搜索Struts2漏洞
get_result(resource='web',dork='city:jinan struts2', page=1)
