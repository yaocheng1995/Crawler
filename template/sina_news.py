import re
import json
import pandas
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

#主程序
def main():
    #设置错误输出
    global CodesError
    CodesError =[]

    #基础教学#
    #base_train()

    #实战案例1：新浪新闻网#
    XLnews = get_XL_news()
    data_process(XLnews)
    #print (XLnews[0])

    #print (soup.text)
    ok()

#抓取新浪新闻网信息
def get_XL_news():
    #获取新浪新闻网主页信息
    XLurl = 'http://news.sina.com.cn/'
    XLsoup = get_news(XLurl)

    #获取新浪新闻网-国内新闻链接
    XlClassLink = []
    for news in XLsoup.select('.cNavLinks') :
        if (len(news.select('span')) >0) :
            for link in news.select('a') :
                XlClassLink.append(link['href'])
    XLCurl = XlClassLink[4]

    #获取新浪新闻网-国内新闻网页信息
    XLCsoup = get_news(XLCurl)
    #print (type(XLurl),XLurl,type(XLsoup))
    #print (type(XLCurl),XLCurl,type(XLCsoup))

    #根据不同HTML标签取得对应内容
    NewsTitle = []
    NewsTime = []
    NewsLink = []
    for new in XLCsoup.select('.news-item') :
        if (len(new.select('h2')) >0) :
            NewsTitle.append(new.select('h2')[0].text)
            NewsTime.append(new.select('.time')[0].text)
            NewsLink.append(new.select('a')[0]['href'])
    #print (len(NewsTitle))
    #for i in range(0,len(NewsTitle)) :
    #   print (NewsTime[i],NewsTitle[i],NewsLink[i])

    #抓取单页新闻内文资料
    #NewsDetail = [get_news_detail(link) for link in NewsLink]
    #print (len(NewsDetail))

    #抓取分页下的网页链接
    NewsUrls = []
    get_subpage_rul(NewsUrls)
    #[print(url) for url in NewsUrls[0:5]]

    #抓取多页新闻内文信息
    NewsDetail = [get_news_detail(url) for url in NewsUrls]

    #print (NewsDetail[0])
    return(NewsDetail)

#获取网页信息，并读进BS中
def get_news(newsrul):
    #获取网页信息
    newsres = requests.get(newsrul)
    newsres.encoding = 'utf-8'

    #将网页打包进BeautifulSoup中
    soup = BeautifulSoup(newsres.text, 'html.parser')
    return (soup)

#获取分页下的网页链接
def get_subpage_rul(urls):
    #该链接在JS → 'zt_..'中找到，并去除了最后一部分'&..'
    Pageurl = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}'

    #通过requests获取JS中的链接，并用json下载
    for i in range (1,20) :
        pageres = requests.get(Pageurl.format(i))
        pagejson = json.loads(pageres.text.lstrip('  newsloadercallback(').rstrip(');'))
        #将新闻url存放进列表中
        [urls.append(pj['url']) for pj in pagejson['result']['data']]
    #print(urls,'\nUrls number is：',len(urls))

#获取新闻内文资料（更新版）
def get_news_detail(url):
    #建一个空字典，存放获取到的所有元素
    XLnews = {}

    #获取单个新闻的网页信息
    newsoup = get_news(url)

    #获取标题
    XLnews['title'] = newsoup.select('.main-title')[0].text
    #获取时间
    Date = newsoup.select('.date-source')[0].contents[1].text
    XLnews['date'] = change_time_format(Date)
    #获取来源
    XLnews['source'] = newsoup.select('.date-source')[0].contents[3].text
    #获取编辑
    XLnews['author'] = newsoup.select('.show_author')[0].text.strip('责任编辑：')
    #获取内文
    XLnews['article'] = '\n'.join([txt.text.strip() for txt in newsoup.select('.article p')[:-1]])
    #获取评论数
    XLnews['comments'] = get_news_cmt(url)
    #获取网页链接
    XLnews['link'] = url

    #print (XLnews)
    return(XLnews)

#获取新闻内文资料（初版，已放弃）
def get_news_detail_pro(links,titles,times,resources,authors,texts,cmtnums):
    #for i in range(0,30):  #数量控制
    for link in links:
        #newsoup = get_news(links[i])   #测试用
        newsoup = get_news(link)        #正式用
        titles.append(newsoup.select('.main-title')[0].text)                            #获取标题
        times.append(newsoup.select('.date-source')[0].contents[1].text)                #获取时间
        resources.append(newsoup.select('.date-source')[0].contents[3].text)            #获取来源
        authors.append(newsoup.select('.show_author')[0].text.strip('责任编辑：'))       #获取编辑
        texts.append('\n'.join([txt.text.strip() for txt in newsoup.select('.article p')[:-1]]))    #获取内文
        cmtnums.append(get_news_cmt(link))                                              #获取评论数
        #print (newsoup.select('.date-source')[0])

#获取评论数
def get_news_cmt(url):
    #获取新闻id
    ##re获取（更优）
    newid = re.search('doc-i(.*).shtml',url).group(1)
    ##切割获取
    #newsid = links[i].split('/')[-1].strip('doc-i').rstrip('.shtml')

    #该链接在JS → 'info..'中找到，并去除了最后一部分'&..'
    cmturl = ('http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=gn&newsid=comos-{}&group=undefined&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=3&t_size=3&h_size=3&thread=1')

    #通过requests获取js中的评论数内容，然后通过json模块下载内容
    cmts = requests.get(cmturl.format(newid))
    jcmt = json.loads(cmts.text)

    #之前‘count’这个key有时候找不到，因此设置错误输出
    try:
        cmtnum = jcmt['result']['count']['show']
    except KeyError:
        return('0')
        global CodesError
        CodesError.append(link)
    else:
        return(cmtnum)

#变换时间的格式
def change_time_format(date):
    #将str转换成time形式
    timeD = datetime.strptime(date, '%Y年%m月%d日 %H:%M')

    #将time转换成str形式
    strD = timeD.strftime('%Y-%m-%d %H:%M')

    return(strD)

#新浪新闻数据处理：
def data_process(news):
    #将新闻数据用pandas存放到矩阵中
    XLarray = pandas.DataFrame(news)
    #print (type(XLarray))

    #将新闻数据保存到Excel
    XLarray.to_excel('XLnews.xlsx')

    #将新闻数据保存到数据库
    with sqlite3.connect('XLnews.aqlite') as db:
        XLarray.to_sql('XLnews', con = db )
        #XLarray2 = pandas.read_sql_query('SELECT * FROM XLnews', con = db)

#个人习惯，在程序结尾输出错误详情
def ok():
    global CodesError
    print ('-------------我是淫荡的分割线-------------')
    print ('Codes Exist',len(CodesError),'Errors')


#-----基础教学-----#
def base_train():
    newsrul = "http://news.sina.com.cn/"
    #newsres = get_news_all(newsrul)
    newsres = get_news_all()
    soup = new_into_bs()
    HTMLlab = html_tags(soup)
    HTMLcss = html_CSS(soup)

#获取网页信息
def get_news_all():
    newsrul = "http://news.sina.com.cn/"
    newsres = requests.get(newsrul)

    #把编码格式改为“utf-8”，才能将文本输出
    newsres.encoding = 'utf-8'

    #print (newsres.text)
    #print (type(newsres))
    return (newsres)

#将网页读进BeautifulSoup中
def new_into_bs():
    #这是HTML的网页元素格式举例
    html_sample = ' \
    <html> \
    <body> \
    <h1 id="title">Hello World</h1> \
    <a href="#" class="link">This is link1</a> \
    <a href="# link2" class="link">This is link2</a> \
    </body> \
    </html>'

    #将该字符串用bs4的格式封装起来，使用"html.parser"剖析器
    soup = BeautifulSoup(html_sample, 'html.parser')

    #print (type(soup))
    #print (soup.text)
    return (soup)

#找出所有含特定标签的HTML元素
def html_tags(soup):
    #print(type(soup))

    #找出含有‘h1’标签的元素
    header = soup.select('h1')
    print ('header=')
    #print (header)
    #print (header[0])
    print (header[0].text)

    #找出含有‘a’标签的元素
    alink = soup.select('a')
    print ('alink=')
    #print (alink)
    for link in alink:
        #print (link)
        print (link.text)

#取得含有特定CSS属性的元素
def html_CSS(soup):
    #找出所有id为title的元素，id前面需加#
    alink = soup.select('#title')
    print (alink[0].text)

    #找出所有class为link的元素，class前面需加.
    for link in soup.select('.link') :
        print (link.text)

    #找出所有a tag的href链接
    alinks = soup.select('a')
    for link in alinks :
        print (link)
        print (link['href'])

    #举例，bs4将exa打包成soup文件，内部可按字典方法读取
    exa = '<a href="#" qoo=123 abc=789> i am a link </a>'
    exsoup = BeautifulSoup(exa, 'html.parser')
    print(exsoup.select('a')[0]['qoo'])


#执行主程序
main()
