#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xlrd
import os
import sys
import argparse

reload(sys)
sys.setdefaultencoding("utf-8")

"""
            he_scan.py -xlspath "D:\\no5"
            he_scan.py -xls "D:\\no5\\bd.xls"
            he_scan.py -xlspath "D:\\no5" -risk xxx
            he_scan.py -xls "D:\\no5\\bd.xls" -risk xxx

            he_scan.py -curpath "d:\\no5" -prepath "d:\\no4\\high-risk"
            he_scan.py -curfile "D:\\no5\\bd.txt" -prepath "d:\\no4\\high-risk"
            """


# 对文本进行提取
def edit_txt(res_file):
    res = open(res_file, 'r')
    if os.path.exists('ftp'):
        pass
    else:
        os.mkdir('ftp')

    # print os.getcwd()
    cur_path = (os.path.abspath('.') + os.sep).decode("gbk")
    # print type(cur_path)
    # print cur_path

    resname = res_file.split(os.sep)[-1].split('.')[0].split('-')[0].decode("gbk")
    # print cur_path + "ftp" + os.sep + "ftp" + resname + '.txt'
    # print type(resname)
    ftp_file = open(cur_path + "ftp" + os.sep + "ftp-" + resname + '.txt', 'w+')

    if os.path.exists('ssh'):
        pass
    else:
        os.mkdir('ssh')
    ssh_file = open(cur_path + "ssh" + os.sep + 'ssh-' + resname + '.txt', 'wb+')

    if os.path.exists('telnet'):
        pass
    else:
        os.mkdir('telnet')
    telnet_file = open(cur_path + "telnet" + os.sep + 'telnet-' + resname + '.txt', 'wb+')

    for line in res.readlines():
        if '21/open/tcp//ftp' in line:
            ftp_file.writelines(line.split('\t')[0].split(' ')[1] + os.linesep)
        elif '22/open/tcp//ssh' in line:
            ssh_file.writelines(line.split('\t')[0].split(' ')[1] + os.linesep)
        elif '23/open/tcp//telnet' in line:
            telnet_file.writelines(line.split('\t')[0].split(' ')[1] + os.linesep)
    ftp_file.close()
    ssh_file.close()
    telnet_file.close()
    print "edit_txt function finished!"


# 调用nmap进行端口扫描
def port_scan(res_file):
    # print type(file)
    os.system("nmap -Pn -vv -n -T4 -p21,22,23 --open -iL %s -oG %s" % (res_file, res_file.split('.')[0] + '-nmap.txt'))
    print "port_scan function finished!"
    edit_txt(res_file.split('.')[0] + '-nmap.txt')


# 提取所有高危IP
def get_all_ip(xls_name):
    # 打开Excel
    try:
        excle = xlrd.open_workbook(xls_name)
        # 获取sheets
        sheets = excle.sheets()
    except:
        print u"请确保excel没有被打开或者你的文件路径有问题"
        sys.exit()
    # 使用漏洞明细sheet
    sheet_name = sheets[1]
    # 获取行数
    nrows = sheet_name.nrows
    ips = []
    for row_num in range(1, nrows):
        row = sheet_name.cell_value(row_num, 3)
        ips.append(row)

    # write_txt(set(ips), xls_name.split('.')[0])
    txt_name = xls_name.split('.')[0]
    result = txt_name + '.txt'
    ips_res = open(result, 'w+')
    for ip in ips:
        ips_res.writelines(ip.lstrip("\r\n\t\t\t").replace('\r\n', os.linesep))
    ips_res.close()
    with open(result, 'r') as before_dup:
        with open(txt_name + '-all.txt', 'w+') as after_dup:  # 保存去重后的所有IP
            for ip in set(before_dup.readlines()):
                print ip
                after_dup.writelines(ip)
    if os.name == 'nt':  # 去除中间文件
        os.system('del %s' % result)
    elif os.name == 'posix':
        os.system('rm -fr %s' % result)

    port_scan(txt_name + '-all.txt')  # 端口扫描


def get_risk_ip(xls_name):
    txt_name = xls_name.split('.')[0]
    if os.path.exists('high-risk'):
        pass
    else:
        os.mkdir('high-risk')
    try:
        # 打开Excel
        xls_res = xlrd.open_workbook(xls_name)
        # 获取sheets
        sheets = xls_res.sheets()
    except:
        print u"请确保excel没有被打开"
        sys.exit()
    # 使用漏洞明细sheet
    vuls = sheets[1]
    # 获取行数
    nrows = vuls.nrows
    risk_ip = []
    for row in range(1, nrows):
        # 提取"危险级别"
        row_value = vuls.cell_value(row, 2)
        if row_value == u'高危':
            # 如果是高危则提取高危IP
            ip = vuls.cell_value(row, 3)
            # print type(ip)
            risk_ip.append(ip)

    result = txt_name + '.txt'
    ips = open(result, 'w+')
    for ip in risk_ip:
        ips.writelines(ip.lstrip("\r\n\t\t\t").replace('\r\n', os.linesep))
    ips.close()

    with open(result, 'r') as before_dup:
        with open(os.getcwd() + os.sep + "high-risk" + os.sep + os.path.basename(txt_name) + '-risk.txt', 'w+') as after_dup:
            for ip in set(before_dup.readlines()):
                after_dup.writelines(ip)
    if os.name == 'nt':
        os.system('del %s' % result)
    elif os.name == 'posix':
        os.system('rm -fr %s' % result)
    print u"高危IP提取完成"


def is_path(param):
    # print param
    if os.path.isfile(param):
        print u"请输入正确的参数"
        sys.exit(1)


def is_file(param):
    if os.path.isdir(param):
        print u"请输入正确的参数"
        sys.exit(1)


def compare(f1, f2):
    print os.path.basename(f1)  # .decode("gbk")
    count = 0
    file1 = open(f1, 'r').readlines()
    try:
        file2 = open(f2, 'r').readlines()
    except Exception, r:
        # print r
        print u"请确保文件名一致"
        sys.exit()

    file1_num = len(file1)
    file2_num = len(file2)

    if file1_num > file2_num or file1_num == file2_num:
        for line1 in file1:
            for line2 in file2:
                if cmp(line1.strip(), line2.strip()) == 0:
                    count = count + 1
        print u'当月漏洞:', count
        print u'新增漏洞:', file1_num - count
        print u'消除漏洞:', file2_num - count
    else:
        for line2 in file2:
            for line1 in file1:
                if cmp(line2.strip(), line1.strip()) == 0:
                    count = count + 1
        print u'当月漏洞:%s' % count
        print u'新增漏洞:', file1_num - count
        print u'消除漏洞:', file2_num - count


if __name__ == "__main__":
    # 接受cmd参数
    parser = argparse.ArgumentParser()
    group1 = parser.add_argument_group(u'提取Excel中的IP')
    group1.add_argument("-xlspath", type=str, help=u"批量提取IP,输入Excel报告所在的目录")
    group1.add_argument("-xls", type=str, help=u"单个提取,输入Excel报告完整路径")
    group1.add_argument("-risk", type=str, help=u"提取高危IP时需加上此参数，参数值任意，不为空就行")

    group2 = parser.add_argument_group(u'与上月高危IP比对')
    group2.add_argument("-prepath", type=str, help=u"上月高危IP文件所在目录")
    group2.add_argument("-curpath", type=str, help=u"当月高危IP文件所在目录")
    group2.add_argument("-curfile", type=str, help=u"当月高危IP文件，请输入完整路径")
    args = parser.parse_args()

    # 提取IP操作
    if args.risk:
        if args.xlspath:  # 批量提取搞IP
            is_path(args.xlspath)  # 判断输入的参数是否正确
            # print u"is_path 已经被执行"
            os.chdir(args.xlspath)
            for xls_name in os.listdir('.'):
                if xls_name.endswith('.xls'):
                    get_risk_ip(xls_name)
        elif args.xls:  # 单个提取搞IP
            is_file(args.xls)
            os.chdir(os.path.dirname(os.path.abspath(args.xls)))
            get_risk_ip(args.xls)
    elif args.xlspath:  # 批量提取全量存活IP
        is_path(args.xlspath)
        os.chdir(args.xlspath)
        for xls_name in os.listdir('.'):
            if xls_name.endswith('.xls'):
                get_all_ip(xls_name)
    elif args.xls:  # 单个提取全量存活IP
        is_file(args.xls)
        os.chdir(os.path.dirname(args.xls))
        get_all_ip(args.xls)

    # 进行高危IP消除计算工作
    if args.curpath:  # 批量计算增减消除
        is_path(args.curpath)
        os.chdir(args.curpath)
        # print os.getcwd()
        if args.prepath:
            is_path(args.curpath)
            for txt_name in os.listdir('.'):
                if txt_name.endswith('.txt'):
                    compare(args.curpath + os.sep + txt_name, args.prepath + os.sep + txt_name)  # compare(当月, 上月)
    if args.curfile:  # 单个计算增减消除
        is_file(args.curfile)
        os.chdir(os.path.dirname(os.path.abspath(args.curfile)))
        if args.prepath:
            is_path(args.prepath)
            compare(args.curfile, args.prepath + os.sep + os.path.basename(args.curfile))
