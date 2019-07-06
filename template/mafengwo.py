#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import time

import requests
import http.cookiejar as cookielib
from time import sleep
from numpy import random

# Main Process
def main():
    # Set List for errors
    global ERRORS
    ERRORS =[]
    #ERRORS.append('Hello World!')

    #测试
    mafengwo_login()
    mafengwo_login(1)

    ok()

#登录马蜂窝网站
def mafengwo_login(test_login=0):
    #获取 cookies 缓存文件路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    cookies_name = os.path.join(upper_path, 'Output', 'mfw.txt')
    print (cookies_name)

    #输出提示
    if test_login:
        print ('Test login status ..')
    else:
        print ('Login MFW ing..')

    #设置 session 和 cookies
    mfw_session = requests.session()
    mfw_session.cookies = cookielib.LWPCookieJar(filename=cookies_name)

    #设置 url
    if test_login:
        test_url = 'http://www.mafengwo.cn/sales/collect.php'
    else:
        login_url = 'https://passport.mafengwo.cn/login/'

    #设置 header
    login_headers = {
        'referer' : 'https://passport.mafengwo.cn/',
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'
    }


    #设置 登录名和密码
    login_data = {
        'passport' : '18862230523',
        'password' : 'dhp326317'
    }

    #下载之前，暂停
    sleep_time = random.randint(1,3)
    print('Sleep {}s .. Downloading'.format(sleep_time))
    sleep(sleep_time)

    #登录网站
    if test_login:
        #下载 cookies 信息
        mfw_session.cookies.load()
        #mfw_session = test_login

        test_res = mfw_session.request(method='GET', url=test_url, headers=login_headers, allow_redirects=False)

        print('Login status is : {}'.format(test_res.status_code))
    else:
        login_res = mfw_session.request(method='POST', url=login_url, data=login_data, headers=login_headers)

        print (mfw_session.cookies)
        #保存 cookies 信息
        mfw_session.cookies.save()


###---------- Template ------------###

# Get Errors path
def get_error_path():
    # Get localtime
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Change time's form
    time_part = local_time.split(' ')
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

