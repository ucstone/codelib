#!/usr/bin/env python
#coding:utf-8
import json
import requests as req
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from time import sleep

class Zoomeye(object):
    def __init__(self, host="api.zoomeye.org"):
        self._base_uri = "http://%s" % host
        self._headers = {"Authorization": "JWT %s" % self.get_token(), "Content-Type": "application/json"}

    def get_token(self):
        payload = {"username": "你的ZoomEye账号", "password": "你的ZoomEye密码"}
        try:
            res = req.post('https://api.zoomeye.org/user/login', data=json.dumps(payload))
        except Exception as e:
            print e
            sys.exit()
        return json.loads(res.text)['access_token']

    # 查看当月还有多少剩余查询结果
    def resource_info(self):
        return req.get("https://api.zoomeye.org/resources-info", headers=self._headers).content

    def search(self, keyword, page=1, searchtype="web"):
        uri = 'https://api.zoomeye.org/%s/search?query=%s&page=%s&fact=app,os' % (searchtype, urllib.quote(keyword), page)
        try:
            response = req.get(uri, headers=self._headers)
            search_res = json.loads(response.content)
            print response.url
        except Exception as e:
            print e
        # 此处判断有无搜索到结果，如果响应代码为200表示请求到结果，否则打印错误提示
        if response.status_code == 200:
            pages = self.getPageNum(int(search_res['total']))
        else:
            print "Error Code: ",response.status_code, "Tips: ",search_res
            sys.exit()
        #执行查询操作
        for i in range(page,pages+1):
            print "Get page " + str(i) + " info ..."
            uri = 'https://api.zoomeye.org/%s/search?query=%s&page=%s&fact=app,os' % (searchtype, urllib.quote(keyword), page)
            try:
                result_page = req.get(uri, headers=self._headers)
                page_content = json.loads(result_page.content)
                print type(page_content)
            except Exception as e:
                print e
            if result_page.status_code == 200:
                # 搜索有两种类型，一种是host，另一种是web服务
                if searchtype == 'host':
                    for match in page_content['matches']:
                        # print match
                        # 整理host搜索结果，这里可以自己看返回包自定义
                        res_line = match['ip'] + ':' + str(match['portinfo']['port'])+'\t'+match['portinfo']['banner'].strip()+'\t'+match['geoinfo']['isp']
                        print res_line
                        self.save_result(res_line)
                elif searchtype == 'web':
                    for match in page_content['matches']:
                        # 整理web搜索结果，这里可以自己看返回包自定义
                        res_line = match['ip'][0] +'\t'+ match['title'] +'\t'+ 'http://' + match['site']
                        print res_line #此行可注释，不影响查询结果
                        self.save_result(str(res_line).encode('utf-8'))
            else:
                print "Error Code: %s" % result_page.status_code
                print "URL: {}, Error MSG: {}, Tips:{} ".format(search_res['url'], search_res['message'],
                                                                search_res['error'])
            sleep(0.2)

    # 将结果写入文件
    def save_result(self, targetList):
        with open('result.txt', 'a') as f:
            f.writelines(targetList+ '\n')

    # 对搜索结果进行分页
    def getPageNum(self, total):
        if total == 0:
            print "No result, exit.."
            sys.exit()
        page = total / 10
        if total % 10 == 0:
            return page
        return page + 1

if __name__ == "__main__":
    z = Zoomeye()
    # 查看当月还有多少剩余查询结果
    print z.resource_info()
    # 查询
    print z.search("openssh", searchtype="host",page=1)
