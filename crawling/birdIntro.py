import re
import time
import random
import requests
import pandas as pd
from retrying import retry
from selenium import webdriver
from bs4 import BeautifulSoup
import pymysql
import urllib

# 请求头池
user_agent = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; "
    ".NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR "
    "2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR "
    "3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
    ".NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR "
    "3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 ("
    "Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 "
    "Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 "
    "Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 "
    "LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
    "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 "
    "LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
    "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
    "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
    "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 "
    "Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 "
    "Safari/537.36",
]

@retry(stop_max_attempt_number=8)
def getHtml(url):
    try:
        random_user_agent = random.choice(user_agent)  # 从user_agent池中随机生成headers
        response = requests.get(url, headers={'user-agent': random_user_agent})
        response.encoding = 'utf-8'
        if response.status_code == 200:
            html = response.content.decode()
            return html
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)

# 第一步，先把简介信息采集下来，形成一个数据库 先做这个--
baseUrl = "http://www.birder.cn"
driver = webdriver.Firefox()

# 数据库信息
address = 'localhost'
DataBase  = "bird"
Sqlusername = "root"
Sqlpw = "mysql9995"
port = 3306

# 连接数据库
connection = pymysql.connect(host=address, user=Sqlusername, password=Sqlpw,
                             database=DataBase, charset="utf8", port=port, db='python')


def getIntro(url):

    oneBird = {}

    html = getHtml(url)
    soup = BeautifulSoup(html, 'html.parser')
    # 获取名称
    name = soup.find('div',attrs={'class':'title clearBox'})
    nameList = name.contents
    oneBird['中文名'] = nameList[0].strip()
    oneBird['拉丁名'] = nameList[2].string
    enName = nameList[3].strip()
    start = enName.find('：')+1
    end = enName.find(')')
    oneBird['英文名'] = enName[start:end]

    # 获取图片
    img = soup.find('div',attrs={'class':'ban2'}).find('img')
    oneBird['imgUrlA'] = baseUrl + img['src']
    # 获取简介信息
    intro = soup.find('div',attrs={'class':'pt17 meassage'}).descendants
    KeyValue = []
    for item in intro:
        if item.name is None and item != '\n':
            KeyValue.append(item)

    for i in range(0,len(KeyValue),2):
        key =  KeyValue[i]
        lastId = key.find('：')
        try:
            oneBird[key[:lastId]] = KeyValue[i+1]
        except:
            oneBird[key[:lastId]] =None
            # 拆解 目和科
    classic = oneBird['分类']
    fid = classic.find('\xa0')
    lid = classic.rfind('\xa0')+1
    oneBird['目'] =  classic[:fid]
    oneBird['科'] = classic[lid:]

    return oneBird

def save_data(oneBird):
    attrName = ['中文名','拉丁名','英文名','imgUrlA','目','科','IUCN 红色名录等级','中国保护级别','描述',
                '虹膜','嘴','脚','叫声','分布范围','分布状况','习性','俗名']
    attrValue = [None]*17
    for i in range(len(attrName)):
        if attrName[i] in oneBird.keys():
            attrValue[i] = oneBird[attrName[i]]



    try:
        # 检查连接是否断开，如果断开就进行重连
        connection.ping(reconnect=True)
        cursor1 = connection.cursor()

        sql = 'insert into birdintro(中文名,拉丁名,英文名,imgUrlA,目,科,IUCN红色名录等级,中国保护等级,描述,虹膜,' \
              '嘴,脚,叫声,分布范围,分布状况,习性,俗名) ' \
              'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

        cursor1.execute(sql, (attrValue[0], attrValue[1], attrValue[2], attrValue[3],attrValue[4],
                              attrValue[5],attrValue[6],attrValue[7],attrValue[8],attrValue[9],
                              attrValue[10],attrValue[11],attrValue[12],attrValue[13],attrValue[14],attrValue[15],attrValue[16]))

        # 提交事务
        connection.commit()
        print("%s记录保存成功\n" % (attrValue[0]))
    except Exception as e:
        print("操作出现错误：{}".format(e))
        # 回滚所有更改
        connection.rollback()

    cursor1.close()
    connection.close()


# def EnterIntro():
#     a_lis = driver.find_elements_by_tag_name('a')
#     # length = len(links)
#     for a in a_lis:
#         link = a.get_attribute("href")
#         # links = driver.find_element_by_tag_name('a')
#         # links = driver.find_elements_by_xpath("/html/body/div[2]/div/div[2]/div[1]/div[2]/ul/li[1]/div[2]/div[2]/ul/li/a")
#         # link = links[i]
#         # driver.get(url)
#         # 针对单个页面进行爬取的函数
#         # one = getIntro(url)
#         # save_data(one)
#         print(link)
#         driver.get(link)
#
#     # 爬完一个目以后怎么切换到另一个目去？
#
# # 根据driver不停地做数据的采集工作 -- 尽可能多地采下来
# # while True:
# #     @retry(stop_max_attempt_number=8)
# #     def network_programming(num):
# #         url = 'https://s.taobao.com/search?q=%E9%9B%B6%E9%A3%9F&imgfile=&js=1&stats_click=search_radio_tmall%3A1' \
# #               '&initiative_id=staobaoz_20190508&tab=mall&ie=utf8&sort=sale-desc&filter=reserve_price%5B%2C200%5D' \
# #               '&bcoffset=0&p4ppushleft=%2C44&s=' + str(num)
# #         random_user_agent = random.choice(user_agent)  # 从user_agent池中随机生成headers
# #         # random_proxies = random.choice(proxies)  # 从代理ip池中随机生成proxies
# #         web = requests.get(url, headers={'user-agent': random_user_agent}, proxies={'http': random_proxies})
# #         web = requests.get(url, headers={'user-agent': random_user_agent})
# #         web.encoding = 'utf-8'
# #         return web
# #
# driver.get("http://www.birder.cn/species/Tragopan-melanocephalus")
# # div = driver.find_elements_by_class_name('nav')
# EnterIntro()

def CrawlIntro():
    html = getHtml("http://www.birder.cn/species/Tragopan-melanocephalus")
    soup = BeautifulSoup(html,'html.parser')
    a_link = soup.find_all('a')
    firstId = 0
    lastId = 0
    for i in range(len(a_link)):
        if a_link[i].string == '鸟种':
            firstId = i+868
        if a_link[i].string =='黑颈䴙䴘':
            lastId = i+1
    for a in a_link[firstId:lastId]:
        if '科' in a.string:
            continue
        url = baseUrl + a['href']
        print("爬取页面...%s\n"%(url))
        # 针对单个页面进行爬取的函数
        one = getIntro(url)
        save_data(one)
        time.sleep(0.8)

# CrawlIntro()