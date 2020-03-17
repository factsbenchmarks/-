import requests
from bs4 import BeautifulSoup
import random
import re
import os
import hashlib
import time
import threading
from multiprocessing import Pool #进程池
from concurrent.futures import ThreadPoolExecutor
import re

STORAGE_DIR = r'C:\STORAGE\heitai'
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
]

START_URL = 'https://zh.nyahentai.cc/language/chinese/popular/page/{}'

pattern = re.compile('src=(.*?jpg)')

def get_content(url):
    '''
    返回url的html内容
    :param url:
    :return:
    '''
    headers = {
        'User-Agent':random.choice(USER_AGENT_LIST),
    }
    r = requests.get(url,headers=headers,timeout=10)
    if r.status_code == 200:
        return r.text

def list_page_parse(content):
    '''
    列表页解析，获取详情页
    :param content:
    :return:
    '''
    new_urls = []
    soup = BeautifulSoup(content,'lxml')
    a_s = soup(name='a',class_='target-by-blank')
    for a in a_s:
        url = 'https://zh.nyahentai.cc' + a.attrs['href'] + 'list2/'
        name = a.img.attrs['alt']
        if name:
            new_urls.append(name+'|'+url)
    #     content1 = get_content(url)
    #     if content1:
    #         soup1 = BeautifulSoup(content1, 'lxml')
    #         img_l = soup1(name='img',class_='list-img')
    #         src_l = []
    #         for img in img_l:
    #             src = img.attrs['src']
    #             src = pattern.findall(src)
    #             if src:
    #                 new_urls.append(src[0])
    # print('list_page_urls',new_urls)
    return new_urls


def download_picture(future):
    '''
    根据url，下载图片，保存到指定位置
    :param url:
    :return:
    '''
    headers = {
        'User-Agent':random.choice(USER_AGENT_LIST),

        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'cookie':'_ga=GA1.2.1779356565.1583917096; __cfduid=dd5d9f6bcad1d9261710244785d37d2b21583917105; _gid=GA1.2.889872390.1584380237; _gat_gtag_UA_134953920_15=1',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'none',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',

    }
    infos = future.result()

    for info in infos:
        file_name,file_url = info.split('|')
        print('file_url',file_url)
        file_name = file_name.replace('!','').replace('?','').replace('<','').replace('>','')\
            .replace('|','').replace(':','').replace('/','').replace(':','')\
            .replace('"','').replace('*','')
        file_path = os.path.join(STORAGE_DIR,file_name)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        content_cat = get_content(file_url)
        i = 1
        if content_cat:
            soup_cat = BeautifulSoup(content_cat, 'lxml')
            img_cat = soup_cat(name='img',class_='list-img')
            for img in img_cat:
                src = img.attrs['src']
                src = pattern.findall(src)
                if src:
                    time.sleep(random.randint(2, 6))
                    print('img_url',src[0])
                    r = requests.get(src[0],headers=headers,timeout=20)
                    pic_path = os.path.join(file_path,str(i)+'.jpg')
                    if r.status_code == 200 and not os.path.exists(pic_path):
                        f = open(pic_path,'wb')
                        f.write(r.content)
                        f.close()
                        print('{} download success'.format(pic_path))
                    i+=1


def get_md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()



def fengniao(num):
    content = get_content(START_URL.format(num))

    return list_page_parse(content)


if __name__ == '__main__':
    excutor = ThreadPoolExecutor()
    for i in range(1,10):
        excutor.submit(fengniao,i).add_done_callback(download_picture)

    excutor.shutdown()
    print('----------END-----------------')