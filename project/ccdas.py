#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import time

import re
import copy
import json
import pandas
import requests
from bs4 import BeautifulSoup
from time import sleep
from numpy import random
from pandas import DataFrame
from urllib import request

# Main Process
def main():
    # Set List for errors
    global ERRORS
    ERRORS =[]
    #ERRORS.append('Hello World!')

    #下载科室信息
    download_department_info()

    #下载科室的 疾病知识 列表
    download_disease_list()

    #抽提 疾病 的详细信息
    disease_extraction()

    #下载 疾病网页
    download_disease_html()

    ok()


###---------- STEP 1 ------------###

#下载所有科室信息
def download_department_info():
    #设定主页面 url
    main_url = 'http://ccdas.ipmph.com/department/getAllDepartments?departmentLevel=1&departmentCode=&source=disease'
    #设置 用户代理
    random_header = get_request_headers()
    #设置 IP代理
    random_proxy = get_ip_proxy()
    #下载主页面的 department
    main_html = requests.request(method="GET", url=main_url, headers=random_header, proxies=random_proxy)
    main_json = json.loads(main_html.text)

    #获取并保存 主科室信息
    main_department_info = [get_department_info(mj) for mj in main_json['result']]
    save_department_csv(main_department_info, 1)

    #下载分科室信息
    #test_department = main_department_info[0:3]
    #sub_department_info = [download_sub_info(td) for td in test_department]
    sub_department_info = [download_sub_info(mdi) for mdi in main_department_info]
    save_department_csv (sub_department_info, 2)
    save_department_csv (sub_department_info, 3)
    #print(sub_department_info)

    #将科室信息保存为 json 文件
    save_department_info(sub_department_info)
    #[print(sub) for sub in sub_department_info]

#下载分科室页面
def download_sub_info(single_department, try_num=3):
    #获取科室编码
    department_code = single_department['department_code']
    #读取缓存
    html_text = read_department_cache(department_code)

    #如果没有缓存，则下载该网页并缓存
    if not html_text:
        if try_num:
            #获取 url
            seed_url = 'http://ccdas.ipmph.com/department/getAllDepartments?departmentLevel=2&departmentCode={}&source=cases'
            sub_url = seed_url.format(department_code)
            #设置 用户代理
            random_header = get_request_headers()
            #设置 IP代理
            random_proxy = get_ip_proxy()

            #暂停下载，睡眠
            delay = random.randint(5,10)
            print ("Downloading {}.. Sleep {} s".format(department_code, delay))
            sleep(delay)

            #下载主页面的 department
            try:
                sub_html =  requests.request(method="GET", url=sub_url, headers=random_header, proxies=random_proxy)
            except:
                print ('Download {} Error.. Rest Number is {}'.format(department_code, try_num))
                return(download_sub_info(single_department, try_num-1))
            else:
                #将下载的网页保存
                print ('Download {} successful .. Saving'.format(department_code))
                save_department_cache(sub_html.text, department_code)
        else:
            #如果下载次数用完，则不再下载，返回 None
            print ('Download Number is 0 ! Failed Download ..')
    else:
        save_department_cache(html_text, department_code)
        #获取分科室信息
        sub_json = json.loads(html_text)
        if 'result' in sub_json.keys():
            single_department['sub'] = [get_department_info(sj) for sj in sub_json['result']]
        else:
            single_department['sub'] = None

        #print (single_department)
        return (single_department)

#设置路劲
def code_to_path(department_code, choice=0):
    #获取时间戳
    if choice:
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_stamp = local_time.split(' ')[0]
    else:
        time_stamp = '2018-08-13'

    #获取缓存文件夹名
    cache_folder = '_'.join(['Department', time_stamp])

    #获取缓存文件名
    file_name = '.'.join([department_code, 'txt'])

    #获取缓存路劲
    root_path, codes_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Cache', cache_folder, file_name)

    #print (file_path)
    return (file_path)

#获取科室页面文件
def read_department_cache(department_code, choice=0):
    #获取路劲
    file_path = code_to_path(department_code, choice)

    #如果有缓存，则读取缓存，否则返回 None
    if os.path.exists(file_path):
        print ('{} Exists Cache'.format(department_code))
        with open(file_path, "r+", encoding="utf-8") as fp:
            return (fp.read())
    else:
        return (None)

#保存科室页面内容
def save_department_cache(html_text, department_code, choice=1):
    #获取路劲
    file_path = code_to_path(department_code, choice)

    #若缓存文件所在文件夹不存在，则创建该文件夹
    file_folder = os.path.dirname(file_path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    #缓存该文件
    #html_encoding = html_res.apparent_encoding
    with open(file_path, "w+", encoding="utf-8") as fp:
        fp.write(html_text)
        fp.close()

#获取科室信息
def get_department_info(single_department):
    #新建字典，存放相关信息
    department = {}

    #获取 科室信息
    department['department_name'] = single_department['departmentName']
    department['department_code'] = single_department['departmentCode']
    department['department_level'] = single_department['departmentLevel']
    department['is_new_record'] = single_department['isNewRecord']
    department['is_leaf'] = single_department['isLeaf']
    department['is_del'] = single_department['isDel']

    #print (department)
    return (department)

#缓存 department 信息
def save_department_csv(depart_info, level):
    #新建列表，存放 codes 和 name
    csv_info = []
    #提取 name 和 codes
    if level==1 :
        [csv_info.append([info['department_code'], info['department_name']]) for info in depart_info]
    elif level==2 :
        for info in depart_info:
            if info['sub']:
                [csv_info.append([sub['department_code'], sub['department_name']]) for sub in info['sub']]
    else:
        for info in  depart_info:
            if info['sub']:
                [csv_info.append([sub['department_code'], sub['department_name']]) for sub in info['sub']]
            else:
                csv_info.append([info['department_code'], info['department_name']])
    csv_frame = DataFrame(csv_info)
    #print (csv_frame)

    #获取当地时间（即本次更新时间）
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_stamp = local_time.split(' ')[0]

    #获取文件名
    if level==1 :
        file_name = ''.join(['first_level_department_', time_stamp, '.csv'])
    elif level==2 :
        file_name = ''.join(['second_level_department_', time_stamp, '.csv'])
    else:
        file_name = ''.join(['All_department_', time_stamp, '.csv'])

    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    csv_path = os.path.join(upper_path, 'Output', file_name)
    #print(csv_path)

    #查看该路径文件夹是否存在，若不存在，则新建该文件夹
    folder = os.path.dirname(csv_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    #保存数据到 csv 文件中
    csv_frame.to_csv(csv_path, encoding='utf-8', index=False)

#缓存 department 网页
def save_department_info (department_info):
    #获取当地时间（即本次更新时间）
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_stamp = local_time.split(' ')[0]
    file_name = ''.join(['department_information_', time_stamp, '.txt'])

    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    json_path = os.path.join(upper_path, "Cache", file_name)
    #print (json_path)

    #查看路径文件夹是否存在，若不存在，则新建文件夹
    json_folder = os.path.dirname(json_path)
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    #将数据保存为 json 文件
    with open(json_path, 'w+', encoding='utf-8', errors='ignore') as jp:
        json.dump(department_info, jp)


###---------- STEP 2 ------------###

#下载每个病历的号码
def download_disease_list():
    #读取科室信息，从中提取科室号码
    department_numbers = read_department_number()
    #print (department_numbers, len(department_numbers))

    #下载每个科室的 disease 列表
    page_num = []
    #test_numbers = [department_numbers[4]]
    #for code in test_numbers:
    for code in department_numbers:
        #下载第一页 disease list
        totle_page = download_page_disease(code, page_num=1, try_num=3)
        print ('{} totle page is {}'.format(code, totle_page))

        #下载后续所有页的 disease list
        if totle_page:
            [download_page_disease(code, page_num=i, try_num=3) for i in range(2, totle_page+1)]

            #获取下载页面的编号
            [page_num.append('\\'.join([code, str(num)])) for num in range(1, totle_page+1)]

    #保存 page 的数量
    save_page_num(page_num)
    print ("There are {} pages disease".format(len(page_num)))
    #[print(page) for page in page_num]

#读取科室信息，从中提取科室号码
def read_department_number():
    time_stamp = '2018-08-14'
    file_name = ''.join(['first_level_department_', time_stamp, '.csv'])

    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, "Output", file_name)
    #print (file_path)

    #读取 csv 文件
    department_info = pandas.read_csv(file_path)

    #新建列表，存放科室编号
    department_numbers = []
    for i in range(0, len(department_info)):
        department_numbers.append(department_info.ix[i][0])
    #print (department_numbers)
    return (department_numbers)

#下载一页 records
def download_page_disease(department_code, page_num=1, try_num=3):
    #获取下载页面的编号
    code_page = '\\'.join([department_code, str(page_num)])

    #读取缓存
    html_text = read_page_cache(code_page)

    #如果没有缓存，则下载该网页并缓存
    if not html_text:
        #设定 post 内容
        request_payload = {
            "departmentCode": department_code,
            "icd10code": "",
            "pageNo": page_num,
            "pageSize": "50",
            "recordFlag": "record",
            "searchText": "",
            "symptomsWords": ""
        }
        #print (request_payload)

        #如果还有下载次数
        if try_num:
            #设定访问主页链接
            target_url = 'http://ccdas.ipmph.com/rwDisease/getRwDiseaseList'
            #设置 用户代理
            random_header = get_request_headers()
            #设置 IP代理
            random_proxy = get_ip_proxy()
            #print (random_header, '\t', random_proxy)

            #下载之前，暂停
            sleep_time = random.randint(5,10)
            print('Sleep {}s .. Downloading {}'.format(sleep_time, code_page))
            sleep(sleep_time)

            #下载
            try:
                html_res = requests.request(method='POST', url=target_url, headers=random_header, proxies=random_proxy, json=request_payload)
                #print (html_res)
            except Exception as err:
                print ('Download {} Error: {}'.format(code_page, err))
                print ('The Rest Download Number is {} ..'.format(try_num-1))
                return (download_page_disease(department_code, page_num, try_num-1))
            else:
                #将下载的网页保存
                if html_res:
                    html_text = html_res.text
                    save_page_cache(html_text, code_page)
                    #print (html_text)
                    #print_to_json(html_text, 'test_post_1.txt')
        else:
            #如果下载次数用完，则不再下载，返回 None
            print ('Download Number is 0 ! {} Return None'.format(code_page))
            html_text = None
    else:
        #再次缓存该文件
        save_page_cache(html_text, code_page)

    #返回 总页数
    if page_num==1 :
        try:
            html_json = json.loads(html_text)
        except:
            return (None)
        else:
            #print (html_json['result']['totlePage'])
            return (html_json['result']['totlePage'])

#设置路劲
def code_page_to_path(code_page, choice=0):
    #获取时间戳
    if choice:
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_stamp = local_time.split(' ')[0]
    else:
        time_stamp = '2018-08-14'

    #获取缓存文件夹名
    cache_folder = '_'.join(['List', time_stamp])

    #获取缓存文件名
    file_name = '.'.join([code_page, 'txt'])

    #获取缓存路劲
    root_path, codes_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Cache', cache_folder, file_name)

    #print (file_path)
    return (file_path)

#获取缓存网页
def read_page_cache(code_page, choice=0):
    #获取路劲
    file_path = code_page_to_path(code_page, choice)

    #如果有缓存，则读取缓存，否则返回 None
    if os.path.exists(file_path):
        print ('{} Exists Cache'.format(code_page))
        with open(file_path, "r+", encoding="utf-8") as fp:
            return (fp.read())
    else:
        return (None)

#缓存下载网页
def save_page_cache(html_text, code_page, choice=1):
    #获取路劲
    file_path = code_page_to_path(code_page, choice)

    #若缓存文件所在文件夹不存在，则创建该文件夹
    file_folder = os.path.dirname(file_path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    #缓存该文件
    #html_encoding = html_res.apparent_encoding
    with open(file_path, "w+", encoding="utf-8") as fp:
        fp.write(html_text)
        fp.close()

#保存 page 的数量
def save_page_num(page_num):
    #获取当地时间（即本次更新时间）
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_stamp = local_time.split(' ')[0]

    #获取文件名
    file_name = ''.join(['page_num_', time_stamp, '.csv'])

    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    csv_path = os.path.join(upper_path, 'Output', file_name)
    #print(csv_path)

    #查看该路径文件夹是否存在，若不存在，则新建该文件夹
    folder = os.path.dirname(csv_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    #保存数据到 csv 文件中
    page_frame = DataFrame(page_num)
    page_frame.to_csv(csv_path, encoding='utf-8', index=False)


###---------- STEP 3 ------------###

#抽提 疾病 的详细信息
def disease_extraction():
    #读取 page number
    page_num = read_page_num()
    #print(page_num[2])
    #新建列表，存放提取后的病例
    disease_extra = []
    #新建列表，存放提取的疾病 ID
    disease_info = []

    test_page = [page_num[2]]
    #for one_page in test_page:
    for one_page in page_num:
        #读取当页文件
        page_file = read_page_cache(one_page)

        #如果文件有内容
        if page_file:
            #将读取内容打包为 json 格式
            page_json = json.loads(page_file)
            disease_list= page_json['result']['list']
            #保存单个病例文件
            single_disease_extra = []
            upper_code = one_page.split('\\')[0]
            [text_extraction(disease, single_disease_extra, upper_code) for disease in disease_list]
            [save_list_disease(disease) for disease in single_disease_extra]

            #提取疾病的相关信息
            for one_disease in single_disease_extra:
                #新建列表，存放抽提结果
                one_disease_info = {}
                one_disease_info['diseaseId'] = one_disease['diseaseId']
                one_disease_info['departmentCode'] = one_disease['sub_departmentCode']
                one_disease_info['title'] = one_disease['title']

                disease_info.append(one_disease_info)

    #保存疾病相关信息
    save_disease_info(disease_info)

#提取疾病文字内容
def text_extraction(disease, disease_extra, upper_code):
    #新建字典，存放单个疾病文字内容
    one_disease = {}

    #获取标题：title
    one_disease['title'] = disease['title']
    #获取疾病的ID：caseId
    one_disease['diseaseId'] = disease['diseaseId']
    #获取主科室序号：main_departmentCode
    one_disease['main_departmentCode'] = upper_code
    #获取分科室序号：sub_departmentCode
    one_disease['sub_departmentCode'] = disease['departmentCode']
    #获取疾病来源：from
    one_disease['from'] = disease['from']
    #获取内容类型：caseOrNo
    one_disease['caseOrNo'] = disease['caseOrNo']
    #获取文章类型：articleType
    one_disease['articleType'] = disease['articleType']
    #获取关键词：keywords
    one_disease['keywords'] = disease['keywords']
    #获取 icd9 代码：icd9CmCode
    one_disease['icd9CmCode'] = disease['icd9CmCode']
    #获取 icd9 词汇：icd9CmWords
    one_disease['icd9CmWords'] = disease['icd9CmWords']
    #获取 icd10 代码：icd10Code
    one_disease['icd10Code'] = disease['icd10Code']
    #获取 icd10 词汇：icd10Words
    one_disease['icd10Words'] = disease['icd10Words']
    #获取中文名称：chineseDisease
    one_disease['chineseDisease'] = disease['chineseDisease']
    #获取中文别名：chineseDisAlias
    one_disease['chineseDisAlias'] = disease['chineseDisAlias']
    #获取英文名称：englishDis
    one_disease['englishDis'] = disease['englishDis']
    #获取英文别名：englishDisAlias
    one_disease['englishDisAlias'] = disease['englishDisAlias']
    #获取子标题：containTitles
    one_disease['containTitles'] = disease['containTitles']
    #获取疾病摘要：disAbstract
    one_disease['disAbstract'] = disease['disAbstract']
    #获取感染情况：infection
    one_disease['infection'] = disease['infection']
    #获取疾病诊断：caseDiagnosis
    one_disease['caseDiagnosis'] = disease['caseDiagnosis']
    #获取分类内容：classificationOfContent
    one_disease['classificationOfContent'] = disease['classificationOfContent']
    #获取症状：symptomsWords
    one_disease['symptomsWords'] = disease['symptomsWords']
    #获取症状分类：symptomsClassification
    one_disease['symptomsClassification'] = disease['symptomsClassification']
    #获取药物信息：drugsWords
    one_disease['drugsWords'] = disease['drugsWords']
    #获取药物信息分类：drugsClassification
    one_disease['drugsClassification'] = disease['drugsClassification']
    #获取 le：leWords
    one_disease['leWords'] = disease['leWords']
    #获取 le 分类：leClassification
    one_disease['leClassification'] = disease['leClassification']
    #获取图片：containsPictures
    one_disease['containsPictures'] = disease['containsPictures']
    #获取表格：containsTables
    one_disease['containsTables'] = disease['containsTables']
    #获取更新时间：updateDate
    one_disease['updateDate'] = disease['updateDate']
    #获取  时间：syncDate
    one_disease['syncDate'] = disease['syncDate']
    #获取疾病的简介：disDesc
    one_disease['disDesc'] = disease['disDesc']
    #获取疾病的临床资料：disClinical
    one_disease['disClinical'] = disease['disClinical']
    #获取疾病的治疗：disTreat
    one_disease['disTreat'] = disease['disTreat']
    #获取疾病的诊断：disDiagnose
    one_disease['disDiagnose'] = disease['disDiagnose']
    #获取疾病的预后：disProg
    one_disease['disProg'] = disease['disProg']
    #获取疾病的预防：disPreventive
    one_disease['disPreventive'] = disease['disPreventive']

    disease_extra.append(one_disease)
    #return (one_disease)

#保存单个疾病文件
def save_list_disease(disease, name=0):
    #设置时间戳
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_stamp = local_time.split(' ')[0]

    #获取缓存文件夹名
    cache_folder = '_'.join(['List_Disease_json', time_stamp])
    #cache_folder = '_'.join(['List_Disease_text', time_stamp])
    #获取缓存文件名
    file_name = '.'.join([disease['diseaseId'], 'json'])
    #file_name = '.'.join([disease['diseaseId'], 'txt'])

    #将 dict 转成 str
    disease_str = str(disease)

    #替换字符 “\u3000”
    disease = re.sub(r'\\u3000', ' ', disease_str)

    #获取缓存路劲
    root_path, codes_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Cache', cache_folder, file_name)
    #print (file_path)

    #若缓存文件所在文件夹不存在，则创建该文件夹
    file_folder = os.path.dirname(file_path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    #缓存该文件
    print ("Saving {}".format(file_name))
    with open(file_path, "w+", encoding="utf-8") as fp:
        json.dump(disease, fp)
        #fp.write(disease)
        fp.close()

#保存疾病相关信息
def save_disease_info(disease_info):
    #获取当地时间（即本次更新时间）
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_stamp = local_time.split(' ')[0]

    #获取文件名
    file_name = ''.join(['disease_ID_', time_stamp, '.csv'])

    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', file_name)
    #print(file_path)

    #查看该路径文件夹是否存在，若不存在，则新建该文件夹
    folder = os.path.dirname(file_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    #保存数据到 txt 文件中
    disease_frame = DataFrame(disease_info)
    disease_frame.to_csv(file_path, encoding="utf-8", index=False)

    #保存数据到 txt 文件中
    #with open(file_path, "w+", encoding="utf-8", errors="ignore") as fp:
    #    json.dump(record_info, fp)


###---------- STEP 4 ------------###

#抓取疾病网页内容
def download_disease_html():
    #读取病历的 id
    disease_id = []
    disease_info = read_disease_info()
    #print (disease_info.ix[0][1])
    [disease_id.append(disease_info.ix[i][1]) for i in range(0, len(disease_info))]
    #print (disease_id)

    # 验证 id 是否有重复(无重复)
    validate_duplication(disease_id)

    #下载 单个病历 网页
    [download_single_disease(str(id_num), try_num=3) for id_num in disease_id]

#读取疾病的 id
def read_disease_info():
    #获取时间戳
    time_stamp = '2018-08-14'

    #获取文件名
    file_name = ''.join(['disease_ID_', time_stamp, '.csv'])

    #获取路径
    root_path, code_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Output', file_name)
    #print(upper_path)

    #读取数据
    return (pandas.read_csv(file_path))
    #with open(file_path, "r+", encoding="utf-8", errors="ignore") as fp:
    #    return (json.load(fp))

# 验证 id 是否有重复(无重复)
def validate_duplication(record_id):
    set_id = set(record_id)
    print ('Raw have {} ID'.format(len(record_id)))
    print ('Set have {} ID'.format(len(set_id)))
    if len(record_id) == len(set_id):
        print ('There are no duplicate ID ~')
    else:
        print ('There are {} duplicate ID ~'.format(len(record_id) - len(set_id)))

#下载 单个疾病 网页
def download_single_disease(id_num, try_num=3):
    #读取缓存
    html_text = read_disease_cache(id_num)

    #如果没有缓存，则下载该网页并缓存
    if not html_text:
        if try_num:
            #设定目标 url
            target_url = 'http://ccdas.ipmph.com/rwDisease/getRwDiseaseDetail?diseaseId={}'.format(id_num)
            #print (target_url)
            #设置 用户代理
            random_header = get_request_headers()
            #设置 IP代理
            random_proxy = get_ip_proxy()
            print (random_proxy)
            #print (random_header, '\t', random_proxy)

            #下载之前，暂停
            sleep_time = random.randint(5,10)
            print('Sleep {}s .. Downloading {}'.format(sleep_time, id_num))
            sleep(sleep_time)

            #下载
            try:
                html_res = requests.request(method='GET', url=target_url, headers=random_header, proxies=random_proxy)
                #print (html_res.text)
            except Exception as err:
                print ('Download {} Error: {}'.format(id_num, err))
                print ('The Rest Download Number is {} ..'.format(try_num-1))
                return (download_single_disease(id_num, try_num-1))
            else:
                #将下载的网页保存
                if html_res:
                    save_disease_cache(html_res.text, id_num)
                    #print (html_res.text)
        else:
            #如果下载次数用完，则不再下载，返回 None
            print ('Download Number is 0 ! {} Return None'.format(id_num))
    else:
        save_disease_cache(html_text, id_num)
        #print (html_text)

#设置路劲
def id_num_to_path(id_num, choice=0):
    #获取时间戳
    if choice:
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_stamp = local_time.split(' ')[0]
    else:
        time_stamp = '2018-08-29'

    #获取缓存文件夹名
    cache_folder = '_'.join(['Disease', time_stamp])

    #获取缓存文件名
    file_name = '.'.join([id_num, 'json'])

    #获取缓存路劲
    root_path, codes_file = os.path.split(sys.argv[0])
    upper_path, code_folder = os.path.split(root_path)
    file_path = os.path.join(upper_path, 'Cache', cache_folder, file_name)

    #print (file_path)
    return (file_path)

#获取 disease 缓存
def read_disease_cache(id_num, choice=0):
    #获取路劲
    file_path = id_num_to_path(id_num, choice)

    #如果有缓存，则读取缓存，否则返回 None
    if os.path.exists(file_path):
        print ('{} Exists Cache'.format(id_num))
        with open(file_path, "r+", encoding="utf-8") as fp:
            return (fp.read())
    else:
        return (None)

#缓存 disease 网页
def save_disease_cache(html_text, id_num, choice=1):
    #获取路劲
    file_path = id_num_to_path(id_num, choice)

    #若缓存文件所在文件夹不存在，则创建该文件夹
    file_folder = os.path.dirname(file_path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    #缓存该文件
    #html_encoding = html_res.apparent_encoding
    with open(file_path, "w+", encoding="utf-8") as fp:
        #json.dump(html_text, fp)
        fp.write(html_text)
        fp.close()


###---------- Crawler ------------###

#登录网站
def web_login(test_login=0):
    #输出提示
    if test_login:
        print ('Test login status ..')
    else:
        print ('Login CCDAS ing..')

    #设置 session
    ccdas_session = requests.session()

    #设置 睡眠时间
    sleep_time = random.randint(5,10)

    #设置 url ，并在下载之前睡眠
    if test_login:
        test_url = 'http://ccdas.ipmph.com/personCenter/goUserInfo'
        print('Sleep {}s .. Testing {}'.format(sleep_time, test_url))
    else:
        login_url = 'http://ccdas.ipmph.com/pc/login/doLogin'
        print('Sleep {}s .. Logining {}'.format(sleep_time, login_url))
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
        ccdas_session = test_login
        test_res = ccdas_session.request(method='GET', url=test_url, headers=login_headers, allow_redirects=False)

        print('Login status is : {}'.format(test_res.status_code))
        return (test_res)
    else:
        login_res = ccdas_session.request(method='POST', url=login_url, data=login_data, headers=login_headers)

        #print (ccdas_session.cookies)
        return (ccdas_session)

#设置 header
def get_request_headers():
    request_headers = {
        'Host' : 'ccdas.ipmph.com',
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
    ]

    #随机选取一个 IP 代理
    random_proxy = random.choice(proxy_set)
    #random_proxy = proxy_set[1]

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
