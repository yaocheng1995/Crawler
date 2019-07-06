#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import time

import json
import pandas
import random
import requests
import socket
import sqlite3
from bs4 import BeautifulSoup
from time import sleep
from pandas import DataFrame
from urllib import request



# Main Process
def main():
    # Set List for errors
    global ERRORS
    ERRORS =[]

    #爬取 快代理 的 proxy
    #download_kuaidaili()

    #合并多个 csv 中的 proxy
    #combine_proxy()

    #验证下载的 proxy -- 用百度验证
    #validate_ip_proxy()

    #对验证后的 proxy 进行去重
    #proxy_redu()

    #登录目标网站
    login_web_test()

    ok()


# -------------------------------------------------

#爬取 快代理 的 proxy
def download_kuaidaili():
    #新建列表，存放 proxy
    proxy_set = []

    #下载国内高匿代理
    download_proxy('inha', proxy_set)

    #下载国内普通代理
    download_proxy('intr', proxy_set)

    #保存下载的 proxy
    save_download_proxy(proxy_set)
    print (len(proxy_set))

#下载代理
def download_proxy(p_type, proxy_set):
    #设定种子链接
    seed_url = 'https://www.kuaidaili.com/free/{}/{}/'

    #for i in range(100, 500):
    for i in range(2, 3):
        #设定目标链接
        target_url = seed_url.format(p_type, i)
        print (target_url)

        #设置睡眠时间
        delay = random.randint(3,5)
        print ('download.. Sleep {}s'.format(delay))
        sleep(delay)

        #下载一页 proxies
        try:
            html_res = requests.get(target_url)
        except Exception as e:
            print ('download {} errors: {}'.format(target_url, e))
            html_res = None

        #如果网页成功下载
        if html_res:
            print (html_res)

            #抽提 proxy
            html_soup = BeautifulSoup(html_res.text, 'html.parser')
            proxy_list = html_soup.select('tbody')[0].select('tr')
            for proxy in proxy_list:
                #新建字典，存放一个 proxy
                one_proxy = {}

                one_proxy['IP'] = proxy.select('td')[0].text
                one_proxy['PORT'] = proxy.select('td')[1].text
                one_proxy['TYPE'] = proxy.select('td')[3].text
                #one_proxy['Anonymity'] = proxy.select('td')[2].text
                #one_proxy['Loation'] = proxy.select('td')[4].text
                #one_proxy['ResponseTime'] = proxy.select('td')[5].text
                #one_proxy['LastValidTime'] = proxy.select('td')[6].text

                #print (one_proxy)
                proxy_set.append(one_proxy)

#保存下载的 proxy
def save_download_proxy(proxy_set):
    #将数据打包到 DataFrame 中
    proxy_array = DataFrame(proxy_set)

    #获取保存路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Rawfile', 'IP_proxy.csv')
    #file_path = os.path.join(upper_path, 'Rawfile', 'IP_proxy.sqlite')

    #保存为 json 文件
    #with open(file_path, "w+", encoding="utf-8") as fp:
    #    for proxy in proxy_set:
    #        fp.write(str(proxy)+'\n')

    #保存为 csv 文件
    proxy_array.to_csv(file_path, index=False, encoding="utf-8")

    #保存为 sql 文件
    #with sqlite3.connect(file_path) as fp:
    #    proxy_array.to_sql('ip', con=fp)
    #with sqlite3.connect('XLnews.sqlite') as db:
    #    XLarray.to_sql('XLnews', con = db )

# -------------------------------------------------

#合并多个 csv 中的 proxy
def combine_proxy():
    ip_proxy_all = []
    new_file_path = 'D:\\codes\\Python\\Crawler\\Record\\ccdas\\Rawfile\\IP_proxy.csv'

    file_path_1 = 'D:\\codes\\Python\\Crawler\\Record\\ccdas\\Rawfile\\IP_proxy_1.csv'
    file_path_2 = 'D:\\codes\\Python\\Crawler\\Record\\ccdas\\Rawfile\\IP_proxy_2.csv'

    proxy_1 = pandas.read_csv(file_path_1, nrows=None)
    proxy_2 = pandas.read_csv(file_path_2, nrows=None)
    print(len(proxy_1), len(proxy_2))

    for i in range(0, len(proxy_1)):
        one_proxy = proxy_1.ix[i]
        ip_proxy_all.append(one_proxy)
    for i in range(0, len(proxy_2)):
        one_proxy = proxy_2.ix[i]
        ip_proxy_all.append(one_proxy)
    print (len(ip_proxy_all))

    proxy_array = DataFrame(ip_proxy_all)
    proxy_array.to_csv(new_file_path, index=False)

# -------------------------------------------------

#验证下载的 proxy
def validate_ip_proxy():
    #获取文件路径，并读取文件
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    #file_path = os.path.join(upper_path, 'Rawfile', 'test_IP_proxy.csv')
    file_path = os.path.join(upper_path, 'Rawfile', 'IP_proxy.csv')
    proxy_set = pandas.read_csv(file_path)

    #新建列表，存放有效 ip
    valid_proxy = []
    #设定 链接时间
    socket.setdefaulttimeout(3)
    #设定 测试网址
    target_url = "http://www.baidu.com"

    #for i in range(500, 1000):
    for i in range(0, len(proxy_set)):
        #设定 ip 代理
        ip_str = proxy_set.ix[i][0]
        port_str = str(proxy_set.ix[i][1])
        ip_proxy = {'http':':'.join([ip_str, port_str])}
        print('Now is {}'.format(ip_proxy))
        #print (ip_proxy, type(ip_proxy))

        px = request.ProxyHandler(ip_proxy)
        opener = request.build_opener(px)
        try:
            html_req = request.Request(target_url)
            html_res = opener.open(html_req)
            #html_text = html_res.read()
            #if html_text:
            if html_res:
                valid_proxy.append(ip_proxy)
                print ('This is a effective proxy: {}'.format(ip_proxy))
                #print (html_text)
                #with open('html_text.txt', "w+", encoding="utf-8") as ht:
                #    json.dump(html_text, ht)
        except Exception as e:
            print (e)
            continue

    #保存验证过的 proxy
    #save_validate_proxy(valid_proxy)
    #valid_proxy = set(valid_proxy)
    save_validate_proxy(valid_proxy)
    print ('There are {} effective proxies:'.format(len(valid_proxy)))
    [print(proxy) for proxy in valid_proxy]

#保存验证过的 proxy
def save_validate_proxy(proxy_data):
    #获取保存路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', 'validate_IP_proxy_0718.txt')

    #保存为 txt 文件
    with open(file_path, "w+", encoding="utf-8") as fp:
        json.dump(proxy_data, fp)

# -------------------------------------------------

#对验证后的 proxy 进行去重
def proxy_redu():
    #读取 proxy 文件
    proxy_data = read_valid_proxy()
    #print (proxy_data[0]['http'])
    #print (len(proxy_data))

    #新建列表，存放去重后的 proxy
    proxy_redu = []

    #去重
    proxy_IP = set()
    for one_proxy in proxy_data:
        one_IP = one_proxy['http']
        if one_IP not in proxy_IP:
            proxy_IP.add(one_IP)
            proxy_redu.append(one_proxy)
    #print (len(proxy_redu))

    #保存去重后的 proxy
    save_redu_proxy(proxy_redu)

#读取 proxy 文件
def read_valid_proxy():
    #获取保存路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', 'validate_IP_proxy_0718.txt')

    #保存为 txt 文件
    with open(file_path, "r+", encoding="utf-8") as fp:
        proxy_data = json.load(fp)
        return (proxy_data)

#保存去重后的 proxy
def save_redu_proxy(proxy_redu):
    #获取保存路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', 'redu_proxy_now.txt')

    #保存为 txt 文件
    with open(file_path, "w+", encoding="utf-8") as fp:
        for proxy in proxy_redu:
            fp.write(''.join([str(proxy), '\n']))

# ------------------ Crawler ---------------------

#登录目标网站测试
def login_web_test():
    #获取 IP代理
    ip_proxy_pool = read_ip_proxy()
    print (len(ip_proxy_pool))

    #新建列表，存放有效 proxy
    effect_proxy = []

    #登录目标网站，获取 cession
    #test_proxy = ip_proxy_pool[0:2]
    #for one_proxy in test_proxy:
    for one_proxy in ip_proxy_pool:
        print('Now is {}'.format(one_proxy))

        #登录网站
        request_cession = login_web_by_proxy(one_proxy)

        #如果登陆成功
        if request_cession:
            #测试登录状态
            login_status = login_web_by_proxy(one_proxy, request_cession)
            if login_status == 200:
                effect_proxy.append(one_proxy)
                print ('This is a effective proxy: {}'.format(one_proxy))
            else:
                print ('Login status is {}'.format(login_status))

    #保存有效 proxy
    save_effect_proxy(effect_proxy)

#获取 IP代理
def read_ip_proxy():
    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', 'redu_proxy.txt')

    #保存为 txt 文件
    with open(file_path, "r+", encoding="utf-8") as fp:
        ip_proxy_file = fp.read()

    #新建列表，存放 proxy
    ip_proxy_pool = []

    #拆分文件，获取单个 proxy
    ip_proxy_data = ip_proxy_file.split('\n')
    ip_proxy_data.pop(-1)
    [ip_proxy_pool.append(eval(i)) for i in ip_proxy_data]

    #print (ip_proxy_pool[0])
    return (ip_proxy_pool)

#登录目标网站
def login_web_by_proxy(one_proxy, test_login=0, try_num=3):
    #如果还有下载次数
    if try_num:
        #设置 session
        request_cession = requests.session()

        #设置 睡眠时间
        sleep_time = random.randint(5,10)

        #设置 url ，并在下载之前睡眠
        if test_login:
            test_url = 'http://ccdas.ipmph.com/personCenter/goUserInfo'
            print('Sleep {}s .. Test login status'.format(sleep_time))
        else:
            login_url = 'http://ccdas.ipmph.com/pc/login/doLogin'
            print('Sleep {}s .. Login CCDAS ing'.format(sleep_time))
        sleep(sleep_time)

        #设置 header
        login_headers = get_request_headers()
        #设置 IP代理
        login_proxy = one_proxy
        #设置 登录名和密码
        login_data = get_login_data()

        #登录网站
        if test_login:
            #获取 cookies 信息
            request_cession = test_login
            try:
                test_res = request_cession.request(method='GET', url=test_url, headers=login_headers, proxies=login_proxy, allow_redirects=False)
            except Exception as err:
                print ('Test Error : Rest Number is {} ..'.format(try_num-1))
                return (login_web_by_proxy(one_proxy, request_cession, try_num=try_num-1))
            else:
                return (test_res.status_code)
        else:
            try:
                login_res = request_cession.request(method='POST', url=login_url, data=login_data, headers=login_headers, proxies=login_proxy)
                #login_res = request_cession.request(method='POST', url=login_url, data=login_data, headers=login_headers)
            except Exception as err:
                print ('Login Error : Rest Number is {} ..'.format(try_num-1))
                return (login_web_by_proxy(one_proxy, try_num=try_num-1))
            else:
                return (request_cession)

#设置 header
def get_request_headers():
    request_headers = {
        'Host' : 'ccdas.ipmph.com',
        'Origin' : 'http://ccdas.ipmph.com',
        'Referer' : 'http://ccdas.ipmph.com/',
        'User-Agent' : get_user_agent()['User-Agent']
    }

    return (request_headers)

#设置 用户代理
def get_user_agent():
    #用户代理 数据集
    user_agent_set = [
        {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER"},
        {"User-Agent":"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"},
        {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"},
    ]

    #随机选取一个用户代理
    random_user_agent = random.choice(user_agent_set)

    #print (random_user_agent)
    return (random_user_agent)

#设置 IP代理
def get_ip_proxy():
    # IP代理 数据集
    proxy_set = [
        {'http': '27.191.234.69:9999'},
        {'http': '39.107.118.76:8118'},
        {'http': '49.4.2.76:80'},
        {'http': '101.4.136.34:80'},
        {'http': '101.4.136.34:8080'},
        {'http': '101.4.136.34:81'},
        {'http': '113.207.44.70:3128'},
        {'http': '118.144.149.200:3128'},
        {'http': '118.144.149.206:3128'},
        {'http': '124.42.7.103:80'},
        {'http': '124.206.133.219:3128'},
        {'http': '218.28.131.34:3128'},
        {'http': '220.249.185.178:9999'},
        {'http': '221.4.133.67:53281'},
        {'http': '222.33.192.238:8118'},
        {'http': '222.73.68.144:8090'},
        {'http': '222.217.68.148:8089'},
        {'http': '223.85.196.75:9999'},
        {'http': '223.96.95.229:3128'}
    ]

    #随机选取一个 IP 代理
    random_proxy = random.choice(proxy_set)

    #print (random_proxy)
    return (random_proxy)

#设置 登录名和密码
def get_login_data():
    login_data = {
        'connection': '18862230523',
        'username': '18862230523',
        'rwAccount': '9625960',
        'email': '',
        'realName': '',
        'sex': '',
        'telephone': '18862230523',
    }

    return (login_data)

#保存有效 proxy
def save_effect_proxy(proxy_data):
    #获取保存路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', 'effect_IP_proxy_0808.txt')

    #保存为 txt 文件
    print ('Saving effective proxies: {}'.format(len(proxy_data)))
    with open(file_path, "w+", encoding="utf-8") as fp:
        for proxy in proxy_data:
            fp.write(''.join([str(proxy), '\n']))


# -------------------------------------------------

# Get Errors path
def get_error_path():
    # Get localtime
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Change time's form
    time_part = (local_time.split(' '))
    part_1 = time_part[0].split('-')
    part_2 = time_part[1].split(':')
    new_time = '_'.join(['_'.join(part_1), '_'.join(part_2)])

    # Get error file name
    file_name = ''.join(["ERRORS_", new_time, ".txt"])

    # Get error file path
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    error_path = os.path.join(upper_path, "Output", "Error_files", file_name)

    # Get path folder
    error_folder = os.path.dirname(error_path)

    # Make new folder  If folder is not exist
    if not os.path.exists(error_folder):
        os.makedirs(error_folder)

    #print (error_path)
    return (error_path)

# Errors output
def ok():
    # Output errors
    global ERRORS
    print ('### 错误输出：')
    print ('Exists {} Errors'.format(len(ERRORS)))
    [print(e) for e in ERRORS]
    print ('---------- 我 是 淫 荡 的 分 割 线 ----------')

    if ERRORS:
        # get localtime
        error_path = get_error_path()

        # Output error file to following location
        with open(error_path, 'w+', encoding='utf-8') as e:
            [e.write(''.join([ers, '\n'])) for ers in ERRORS]

# Run main
main()

