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

    #下载疾病信息
    download_disease_info()

    #下载疾病信息
    download_disease()

    ok()



# ------------------ STEP 1 ----------------

#下载疾病信息
def download_disease_info():
    #设置主链接
    main_url = 'https://www.baptistjax.com/health-library/disease'
    #设置 用户代理
    random_header = get_request_headers()
    #设置 IP代理
    random_proxy = get_ip_proxy()

    #下载主页面的 department
    #main_html = requests.request(method="GET", url=main_url, headers=random_header, proxies=random_proxy)

    #获取主网页缓存路径
    disease_html_path = get_cache_path('Cache', 0)

    #保存主网页
    #with open(disease_html_path, "w+", encoding="utf-8") as fp:
        #json.dump(main_html.text, fp)
        #fp.close()

    #读取主页面缓存
    with open(disease_html_path, "r+", encoding="utf-8") as fp:
        html_json = json.load(fp)
        fp.close()

    #抽提疾病信息
    disease_info = extract_disease_info(html_json)
    #print (len(disease_info))
    #[print(one) for one in disease_info]

    #获取疾病信息缓存路径
    disease_info_path = get_cache_path('Output', 1)

    #保存疾病信息
    disease_frame = DataFrame(disease_info)
    disease_frame.to_csv(disease_info_path, encoding='utf-8', index=False)

#获取网页缓存路径
def get_cache_path(main_folder, choice):
    #获取时间戳 及 缓存文件名
    if choice:
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_stamp = local_time.split(' ')[0]
    else:
        time_stamp = '2018-08-30'

    #获取时间戳 及 缓存文件名
    if main_folder == 'Cache':
        file_name = ''.join(['Disease_info_', time_stamp, '.json'])
    else:
        file_name = ''.join(['Disease_info_', time_stamp, '.csv'])

    #获取缓存路劲
    root_path, codes_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, main_folder, file_name)

    #若缓存文件所在文件夹不存在，则创建该文件夹
    file_folder = os.path.dirname(file_path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    #print (file_path)
    return (file_path)

#抽提疾病信息
def extract_disease_info(html_json):
    #用 bs4 打包网页内容
    html_soup = BeautifulSoup(html_json, 'html.parser')

    #新建列表，存放所有疾病信息信息
    disease_info = []

    #设定疾病组名
    group_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    #抽提所有的疾病信息
    disease_soup = html_soup.select('#alphabeticalGroups')[0]
    disease_list = disease_soup.select('.stList.groupA.panes.featured')

    #test_disease = [disease_list[0]]
    #for i in range(0, len(test_disease)):
    for i in range(0, len(disease_list)):
        #获取疾病组名
        group_name = group_names[i]

        #按组抽提疾病的信息
        disease_group = disease_list[i].select('li')
        #disease_group = test_disease[i].select('li')
        for disease in disease_group:
            #新建字典，存放单个疾病信息
            one_disease = {}

            #按组抽提疾病的信息
            one_disease['group'] = group_name
            one_disease['title'] = disease.select('a')[0].text
            one_disease['url'] = disease.select('a')[0]['href']

            disease_info.append(one_disease)

    return(disease_info)



# ------------------ STEP 2 ----------------

#下载疾病信息
def download_disease():
    #读取疾病信息
    disease_info_path = get_cache_path('Output', 0)
    disease_info = pandas.read_csv(disease_info_path)
    #print (len(disease_info))

    #下载单个疾病页面
    #test_disease = disease_info.ix[0]
    #download_html(test_disease[2])
    #[download_html(disease_info.ix[i][2]) for i in range(0, 1000)]
    [download_html(disease_info.ix[i][2]) for i in range(0, len(disease_info))]

#下载单个疾病页面
def download_html(url, try_num=3):
    #查看该网页是否已缓存
    html_text = read_cache(url)
    #print (html_text)

    #如果没有缓存，则下载该网页并缓存
    if not html_text:
        #如果还有下载次数
        if try_num:
            #设定 url
            seed_url = 'https://www.baptistjax.com'
            target_url = ''.join([seed_url, url])
            #设置 header
            random_head = get_request_headers()
            #设置 IP代理
            random_proxy = get_ip_proxy()

            #下载之前，暂停
            sleep_time = random.randint(5,10)
            print('Sleep {}s .. Downloading {}'.format(sleep_time, url.split('/')[-1]))
            sleep(sleep_time)

            #下载
            try:
                html_res = requests.request(method='GET', url=target_url, headers=random_head, proxies=random_proxy, allow_redirects=False)
                #print (html_res.text)
            except Exception as err:
                #下载错误，重新下载
                print ('Download Error: {}'.format(err))
                print ('The Rest Download Number is {} ..'.format(try_num-1))
                download_html(url, try_num-1)
            else:
                if html_res.status_code == 200:
                    #将下载的网页保存
                    print ('Download successed .. Saving {}'.format(url.split('/')[-1]))
                    save_cache(html_res.text, url)
        else:
            #如果下载次数用完，则不再下载，返回 None
            print ('Download Number is 0 ! Failed Download..')
    else:
        #提取缓存，再次保存
        save_cache(html_text, url)

#设置路劲
def url_to_path(url, choice=0):
    #获取时间戳
    if choice:
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_stamp = local_time.split(' ')[0]
    else:
        time_stamp = '2018-09-03'

    #获取缓存文件夹名
    cache_folder = '_'.join(['Disease', time_stamp])

    #获取缓存文件名
    file_name = '.'.join([url.split('/')[-1], 'txt'])

    #获取缓存路劲
    root_path, codes_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Cache', cache_folder, file_name)

    #print (file_path)
    return (file_path)

#验证是否有缓存
def read_cache(url):
    #获取路劲
    file_path = url_to_path(url, 0)
    #print (file_path)

    #如果有缓存，则读取缓存，否则返回 None
    if os.path.exists(file_path):
        print ('Exists Cache : {}'.format(url.split('/')[-1]) )
        with open(file_path, "r+", encoding="utf-8") as fp:
            return (fp.read())
    else:
        return (None)

#缓存网页
def save_cache(html_text, url):
    #获取路劲
    file_path = url_to_path(url, 1)

    #若缓存文件所在文件夹不存在，则创建该文件夹
    file_folder = os.path.dirname(file_path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    #缓存该文件
    #html_encoding = html_res.apparent_encoding
    with open(file_path, "w+", encoding='utf-8', errors='ignore') as fp:
        fp.write(html_text)
        fp.close()



# ------------------ Crawler -----------------

#设置 header
def get_request_headers():
    request_headers = {
        'Host' : 'www.baptistjax.com',
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
    ]

    #随机选取一个 IP 代理
    random_proxy = random.choice(proxy_set)
    #random_proxy = proxy_set[1]

    #print (random_proxy)
    return (random_proxy)


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

