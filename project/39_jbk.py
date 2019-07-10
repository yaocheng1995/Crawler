#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import time
from time import sleep

import re
import copy
import json
import pandas
from pandas import DataFrame
import requests
from urllib import request
from numpy import random
from bs4 import BeautifulSoup

# Main Process
def main():
    # Set List for errors
    global ERRORS
    ERRORS =[]
    #ERRORS.append('Hello World!')

    #抽提 疾病信息
    extract_disease_info()

    #下载 疾病网页
    download_disease_html()

    ok()


###---------- STEP 1 ------------###

#抽提 疾病信息
def extract_disease_info():
    #获取路径
    file_path = get_file_path()
    #print(file_path)

    #新建列表，存放疾病信息
    disease_info = []

    #抽提疾病信息
    test_file = [file_path[2]]
    #[disease_extraction(fp, disease_info) for fp in test_file]
    [disease_extraction(fp, disease_info) for fp in file_path]
    print (len(disease_info))

    #保存 疾病 相关信息
    save_disease_info(disease_info)

#获取路径
def get_file_path():
    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_folder = os.path.join(upper_path, 'Cache', 'Disease_link')
    #print (file_folder)

    #新建列表，存放所有文件路径
    file_path = []

    #获取所有路径
    for root, dirs, files in os.walk(file_folder):
        for file in files:
            file_path.append(os.path.join(root, file))

    return(file_path)

#格式化抽提疾病信息
def disease_extraction(file_path, disease_info):
    #获取疾病缓存文件
    with open(file_path, "r+", encoding="utf-8") as fp:
        file_cache = fp.read()
    #print (type(file_cache))

    #获取科室信息
    fp_list = file_path.split('\\')
    if len(fp_list) == 8:
        main_department = ''
        sub_department = fp_list[-1].split('.')[0]
    if len(fp_list) == 9:
        main_department = fp_list[-2]
        sub_department = fp_list[-1].split('.')[0]
    #print (main_department, '\t', sub_department)

    if file_cache:
        #分割出单个疾病
        disease_list = file_cache.split('\n')
        #print (len(disease_list))

        #若最后一行为控行，则删除改行
        if not disease_list[-1]:
            disease_list.pop(-1)
        #print (disease_list[-1])

        test_disease = disease_list[0:10]
        #for one in test_disease:
        for one in disease_list:
            #新建字典，存放单个疾病信息
            one_disease = {}

            #抽提疾病信息
            one_list = one.split('\t')
            if len(one_list) == 4:
                one_disease['name'] = one_list[0]
                #one_disease['alias'] = one_list[1]
                one_disease['url'] = one_list[2]
                #one_disease['symptom'] = one_list[3]
                #one_disease['main_d'] = main_department
                #one_disease['sub_d'] = sub_department

                disease_info.append(one_disease)
                #print (one_list)

#保存 疾病 相关信息
def save_disease_info(disease_info):
    #获取当地时间（即本次更新时间）
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_stamp = local_time.split(' ')[0]

    #获取文件名
    #file_name = '_'.join([time_stamp, 'disease_info.csv'])
    file_name = '_'.join([time_stamp, 'disease_link.csv'])

    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', file_name)
    #print(file_path)

    #查看该路径文件夹是否存在，若不存在，则新建该文件夹
    folder = os.path.dirname(file_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    #保存数据到 csv 文件中
    record_frame = DataFrame(disease_info)
    record_frame.to_csv(file_path, encoding="utf-8", index=False)


###---------- STEP 2 ------------###

#抓取病历网页内容
def download_disease_html():
    #读取病历的 url
    disease_url = []
    disease_info = read_disease_info()
    #print (disease_info.ix[0][1])
    [disease_url.append(disease_info.ix[i][1]) for i in range(0, len(disease_info))]
    #print (disease_url[0:10])

    # 验证 是否有重复疾病(有 4133 个重复)
    disease_url = validate_duplication(disease_url)
    print (len(disease_url))

    #设定单个疾病所有网页的列表
    disease_sub_url = ['jbzs/', 'zztz/', 'blby/', 'jcjb/', 'jb/', 'yyzl/', 'bfbz/', 'cyyp/']

    #下载 单个疾病 所有网页
    test_url = disease_url[0:5000]
    for one_url in test_url:
    #for one_url in disease_url:
        #循环下载分页面
        test_sub = disease_sub_url[0:3]
        #for sub_url in test_sub:
        for sub_url in disease_sub_url:
            #合成网页子链接
            new_url = ''.join([one_url, sub_url])
            #print (new_url)
            download_sub_html(new_url, try_num=3)

#读取疾病的 url
def read_disease_info():
    #获取时间戳
    time_stamp = '2018-09-04'

    #获取文件名
    file_name = '_'.join([time_stamp, 'disease_link.csv'])

    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', file_name)
    #print(file_path)

    #读取数据
    return (pandas.read_csv(file_path))

# 验证 url 是否有重复(有 4133 个重复)
def validate_duplication(disease_url):
    set_url = set(disease_url)
    print ('Raw have {} disease'.format(len(disease_url)))
    print ('Set have {} disease'.format(len(set_url)))
    if len(disease_url) == len(set_url):
        print ('There are no duplicate disease ~')
    else:
        print ('There are {} duplicate disease ~'.format(len(disease_url) - len(set_url)))

    #新建列表，存放去重后的疾病链接
    new_disease_url = []
    for one_url in disease_url:
        if one_url not in new_disease_url:
            new_disease_url.append(one_url)

    return (new_disease_url)

#下载 单个疾病 网页
def download_sub_html(target_url, try_num=3):
    #读取缓存
    html_text = read_disease_cache(target_url, choice=0)

    #如果没有缓存，则下载该网页并缓存
    if not html_text:
        if try_num:
            #设置 用户代理
            random_header = get_request_headers()
            #设置 IP代理
            random_proxy = get_ip_proxy()
            #print (random_header, '\t', random_proxy)

            #下载之前，暂停
            sleep_time = random.randint(2,4)
            print('Sleep {}s .. Downloading {}'.format(sleep_time, target_url.split('/')[-3:-1]))
            sleep(sleep_time)

            #下载
            try:
                html_res = requests.request(method='GET', url=target_url, headers=random_header, proxies=random_proxy)
            except Exception as err:
                print ('Download {} Error: {}'.format(target_url.split('/')[-3:-1], err))
                print ('The Rest Download Number is {} ..'.format(try_num-1))
                return (download_sub_html(target_url, try_num-1))
            else:
                #将下载的网页保存
                if html_res.status_code == 200:
                    try:
                        html_text = html_res.content.decode('gbk')
                    except:
                        print ('{} html_text decode error!'.format(target_url.split('/')[-3:-1]))
                        #print (html_text)
                    else:
                        save_disease_cache(html_text, target_url, choice=1)
        else:
            #如果下载次数用完，则不再下载，返回 None
            print ('Download Number is 0 ! {} Return None'.format(target_url.split('/')[-3:-1]))
    else:
        save_disease_cache(html_text, target_url, choice=1)

#设置路劲
def url_to_path(url, choice=0):
    #获取时间戳
    if choice:
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_stamp = local_time.split(' ')[0]
    else:
        time_stamp = '2018-09-09'

    #获取缓存文件夹名
    cache_folder = '_'.join(['Disease', time_stamp])

    #获取缓存文件名
    url_list = url.split('/')
    file_name = '.'.join([url_list[-2], 'txt'])
    cache_name = '\\'.join([url_list[-3], file_name])

    #获取缓存路劲
    root_path, codes_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Cache', cache_folder, cache_name)

    #print (file_path)
    return (file_path)

#获取疾病网页缓存
def read_disease_cache(url, choice=0):
    #获取路劲
    file_path = url_to_path(url, choice)

    #如果有缓存，则读取缓存，否则返回 None
    if os.path.exists(file_path):
        print ('Exists Cache: {}'.format(url.split('/')[-3:-1]))
        with open(file_path, "r+", encoding="gbk") as fp:
            return (fp.read())
    else:
        return (None)

#缓存疾病网页缓存
def save_disease_cache(html_text, url, choice=1):
    #获取路劲
    file_path = url_to_path(url, choice)

    #若缓存文件所在文件夹不存在，则创建该文件夹
    file_folder = os.path.dirname(file_path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    #缓存该文件
    #html_encoding = html_res.apparent_encoding
    #print ('Saving {}'.format(url.split('/')[-3:-1]))
    with open(file_path, "w+", encoding="gbk") as fp:
        fp.write(html_text)
        fp.close()


###---------- Crawler ------------###

#设置 header
def get_request_headers():
    request_headers = {
        'Host' : 'jbk.39.net',
        'Referer' : 'http://jbk.39.net/szkb/jbzs/',
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
