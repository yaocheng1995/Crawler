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
    #ERRORS.append('Hello World!')

    #下载网页--举例
    download_example()

    ok()


# ------------------ Download ----------------

#下载网页--举例
def download_example():
    #设定目标网站的链接
    target_url = ['http://ccdas.ipmph.com/rwDisease/getRwDiseaseDetail?diseaseId=10537']

    #登录网站, 获取其 cession
    request_cession = web_login()

    #获取目标网页
    if request_cession:
        [download_web(url, request_cession) for url in target_url]
    else:
        print ('Failed to Get Cession..')

#获取目标网页
def download_web(url, request_cession, try_num=5):
    #查看该网页是否已缓存
    cache_file = valid_cache(url)
    #print (cache_file)

    #如果没有缓存，则下载该网页并缓存
    if not cache_file:
        #如果还有下载次数
        if try_num:
            #设定 url
            target_url = url
            #设置 header
            random_head = get_request_headers()
            #设置 IP代理
            random_proxy = get_ip_proxy()
            #设置 登录名和密码
            login_data = get_login_data()

            #下载之前，暂停
            sleep_time = random.randint(5,10)
            print('Sleep {}s .. Downloading'.format(sleep_time))
            sleep(sleep_time)

            #下载
            try:
                #html_res = request_cession.request(method='GET', url=target_url, data=login_data, headers=random_head, proxies=random_proxy, allow_redirects=False)
                html_res = requests.request(method='GET', url=target_url, data=login_data, headers=random_head, proxies=random_proxy, allow_redirects=False)
                #print (html_res.text)
            except Exception as err:
                #下载错误，重新下载
                print ('Download Error: {}'.format(err))
                print ('The Rest Download Number is {} ..'.format(try_num-1))
                download_web(url, request_cession, try_num-1)
            else:
                if html_res.status_code == 200:
                    #将下载的网页保存
                    print ('Download successed .. Saving')
                    save_cache(html_res, url)
                else:
                    #如果 cession 失效，重新获取 cession，并重新下载
                    print ('Cession is unuseful.. Getting a new cessioning..')
                    print ('The Rest Download Number is {} ..'.format(try_num-1))
                    requests_cession = web_login()
                    download_web(url, request_cession, try_num-1)
        else:
            #如果下载次数用完，则不再下载，返回 None
            print ('Download Number is 0 ! Failed Download..')

#设置路劲
def url_to_path(url, folder_name):
    #获取时间戳
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_stamp = local_time.split(' ')[0]

    #获取缓存文件夹名
    cache_folder = '_'.join([folder_name, time_stamp])

    #获取缓存文件名
    file_name = '.'.join([url.split('=')[-1], 'txt'])

    #获取缓存路劲
    root_path, codes_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Cache', cache_folder, file_name)

    #print (file_path)
    return (file_path)

#验证是否有缓存
def valid_cache(url):
    #获取路劲
    file_path = url_to_path(url, 'Template')
    #print (file_path)

    #如果有缓存，则读取缓存，否则返回 None
    if os.path.exists(file_path):
        print ('Exists Cache : {}'.format(url.split('=')[-1]) )
        return (1)
    else:
        return (None)

#缓存网页
def save_cache(html_res, url):
    #获取路劲
    file_path = url_to_path(url, 'Template')

    #若缓存文件所在文件夹不存在，则创建该文件夹
    file_folder = os.path.dirname(file_path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    #缓存该文件
    #html_encoding = html_res.apparent_encoding
    with open(file_path, "w+", encoding='utf-8', errors='ignore') as fp:
        json.dump(html_res.text, fp)
        fp.close()



# ------------------ Crawler -----------------

#登录目标网站
def web_login(test_login=0, try_num=3):
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
        login_proxy = get_ip_proxy()
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
                return (web_login(request_cession, try_num=try_num-1))
            else:
                return (test_res.status_code)
        else:
            try:
                login_res = request_cession.request(method='POST', url=login_url, data=login_data, headers=login_headers, proxies=login_proxy)
                #login_res = request_cession.request(method='POST', url=login_url, data=login_data, headers=login_headers)
            except Exception as err:
                print ('Login Error : Rest Number is {} ..'.format(try_num-1))
                return (web_login(test_login=0 ,try_num=try_num-1))
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
        {'http': '124.42.7.103:80'},
        {'http': '39.107.118.76:8118'},
        {'http': '49.4.2.76:80'},
        {'http': '101.4.136.34:80'},
        {'http': '101.4.136.34:8080'},
        {'http': '101.4.136.34:81'},
        {'http': '113.207.44.70:3128'},
        {'http': '222.33.192.238:8118'},
        {'http': '223.96.95.229:3128'}
    ]

    #随机选取一个 IP 代理
    random_proxy = random.choice(proxy_set)
    #random_proxy = proxy_set[0]

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



# ------------------ Other -------------------

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

