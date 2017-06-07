#!/usr/bin/env python
# -*-encoding: utf-8 -*-
__author__ = 'M1k3'

import argparse
import sys
import os

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
reload(__import__('sys')).setdefaultencoding('utf-8')

# 提取nmap扫描结果文件
def deal_nmap_xml(xml_name, save_name):
    tree = ET.parse(xml_name)
    # res_file = open(save_name + '-all.txt', 'w') #生成过程文件
    root = tree.getroot()
    count = []  # 统计存活IP地址数量
    IP_ALL = []  # 开放端口总数
    IP = ''

    for child in root:
        if child.tag == 'host':  # 查找host标签
            for xx in child:
                for state in xx.iter('status'):
                    if state.attrib.get('state') == "up":  # 判断主机是否存活
                        for ports in child:
                            for neighbor in ports.iter('address'):  # 提取主机IP地址
                                IP = neighbor.attrib['addr']
                                count.append(IP)
                            for port in ports:  # 端口信息 ports标签
                                for neighbor in port.iter('state'):
                                    # print neighbor.attrib['state']
                                    if neighbor.attrib['state'] == "open":  # 判断端口是否开放
                                        if port.attrib.has_key('portid'):
                                            # print IP + ":" + port.attrib.get('portid')
                                            lll = IP + ":" + port.attrib.get('portid') + '\n'
                                            # res_file.write(lll)
                                            IP_ALL.append(lll)

    print "There are  %d surviving!" % len(count)
    print "Open port has: %d" % len(IP_ALL)
    # res_file.close()
    return IP_ALL


# 根据端口提取相应的IP
def get_ip(ALL, ports):
    port_file = []
    for port in ports.split(','):
        for line in ALL:
            if len(line.split(':'))>2:
                print line.strip()+" Exception"
            if port == line.split(':')[1].strip():
                 # print line,
                 port_file.append(line)
    print "Port extraction is complete!"
    return port_file


# 比较新发现资产和合规平台资产
def nmap_platform_cmp(file, pfile):
    f1 = file  # sys.argv[1]  # 新发现资产比对
    f2 = pfile  # sys.argv[2]  # 合规平台资产导出的全部资产，整理到一个txt文档中

    os.chdir(f1)
    file_list = []

    if os.path.exists('res'):
        pass
    else:
        os.mkdir('res')

    for txt_file in os.listdir('.'):
        if txt_file.endswith('.txt'):
            file_list.append(txt_file)

    for txt_file in file_list:
        result = []
        if txt_file.endswith('.txt'):
            with open(txt_file, 'r') as xx_file:  # 打开新扫描的资产
                xx_ip = xx_file.readlines()
                print u"Before being removed", len(xx_ip)
                with open(f2, 'r') as yy_file:  # 打开合规平台导出的资产
                    yy_ip = yy_file.readlines()
                    for xx in xx_ip:
                        if xx in yy_ip:  # 若新扫描的资产在合规平台中，则说明已经上报并剔除
                            result.append(xx)
                            xx_ip.remove(xx)  # 删除已经报备过的IP

                # print xx_ip
                print u"After removal", len(xx_ip)
                # 将新发现的资产提取出来
                with open(f1 + os.path.sep + 'res' + os.path.sep + txt_file.split('-')[0] + '-res.txt',
                          'w+') as zz_file:
                    for ip in xx_ip:
                        zz_file.writelines(ip)

        print u"Has been reported:%d" % len(result)
        with open(txt_file, 'r') as xx:
            # xx.readlines()
            print u"%s 未报备资产 %s 个" % (txt_file, str(len(xx.readlines()) - len(result)))
        print 15 * '###'


if __name__ == '__main__':
    # 接受cmd参数
    parser = argparse.ArgumentParser()

    group1 = parser.add_argument_group(u'处理nmap扫描文件')
    group1.add_argument("-xpath", type=str, help=u"批量转换,输入nmap扫描结果xml文件所在的目录")
    group1.add_argument("-xml", type=str, help=u"转换单个xml文件,输入nmap扫描结果xml文件")
    group1.add_argument("-port", type=str, default='21', help=u'要提取的端口;提取多个的格式为"21,80,445"')

    group2 = parser.add_argument_group(u'与合规平台文件比对')
    group2.add_argument("-pfile", type=str, help=u"合规平台已经上报的资产")
    # parser.add_argument("-tfile", type=str, help=u'get ips or domains for this file')
    group2.add_argument("-tpath", type=str, help=u"新扫描的资产文件，只接受目录")
    args = parser.parse_args()

    # nmap扫描结果处理相关参数
    xml_path = args.xpath
    xml_file = args.xml
    ports = args.port
    # 合规平台资产比较相关参数
    platform_file = args.pfile
    # txt_file = args.tfile
    txt_path = args.tpath

    if xml_file and ports:
        save_name = xml_file.split('.')[0]
        # print save_name
        print 'Began to extract %s open port IP' % xml_file
        IP_ALL = deal_nmap_xml(xml_file, save_name)
        get_ip(IP_ALL, ports)

    if xml_path and ports:
        os.chdir(xml_path)
        ALL = []
        for i in os.listdir(xml_path.strip()):
            if i.endswith('.xml'):
                xml_path_file = xml_path + os.path.sep + i
                save_name = i.split('.')[0]
                # print save_name
                print 'Began to extract %s open port IP' % i
                IP_ALL = deal_nmap_xml(xml_path_file, save_name)
                ALL = ALL+IP_ALL
        with open('port-res.txt','w+') as xx:
            for ip in get_ip(ALL, ports):
                xx.write(ip)
                # print ip,

    if txt_path and platform_file:
        try:
            if os.path.isfile(txt_path):
                print u"请输入要处理文件的目录"
            else:
                nmap_platform_cmp(txt_path, platform_file)
        except:
            print u"请输入要处理文件所在目录"
    else:
        pass
