#!/usr/bin/python
#**coding:utf-8**
import requests
import logging
import urllib
import threading
import re
import time
from bs4 import BeautifulSoup
import argparse
from prettytable import PrettyTable

urlInfo = {}
processend = 0
dir_list = []
count = 1

findJsOrCss = 0
accessPage = []
accessPageTmp = []
JsOrCssAccessFile = []
logging.captureWarnings(True)

timetest = 0

def check_url(url):
    # 对爬取的url 进行检测，去重以及检测是否属于该站点
    if "#" in url :
        url = url.split("#")[0]
    if urllib.parse.urlparse(url).hostname == urlInfo["host"] \
        and url not in accessPageTmp and url not in JsOrCssAccessFile:
        return True
    else:
        return False

def endOutput():
    # 结果输出
    if processend == count :
        time.sleep(3)
        table = PrettyTable(['\033[33m序号 ','\033[33m可访问地址\033[0m'])
        for i in range(0,len(accessPage)):
            table.add_row([i,"\033[32m"+accessPage[i]+"\033[0m"])
        print(table)

        if findJsOrCss == 1:
            jsTable = PrettyTable(['\033[33m序号','\033[33m可访问静态资源地址\033[0m'])
            for i in range(0,len(JsOrCssAccessFile)):
                jsTable.add_row([i,"\033[32m"+JsOrCssAccessFile[i]+"\033[0m"])
            print(jsTable)
        
        print("耗时 ：" + str(time.time() - timetest))
        return 1
    return 0


# 循环检测accessPageTmp 中是否存在元素 ，存在则交给page_connect验证
def check_accessPageTmp(findJsOrCss):
    while 1:
        if len(accessPageTmp) != 0:
            accessPageTmp1 = accessPageTmp[::]
            for x in range(0,len(accessPageTmp1)):
                if accessPageTmp1[x] not in accessPage:
                    tmp = accessPageTmp1[x]
                    accessPageTmp.remove(tmp)
                    page_connect(tmp,findJsOrCss)
                else:
                    accessPageTmp.remove(accessPageTmp1[x])
                    
        else:
            # 所有线程结束则输出结果
            if endOutput()== 1 : break

def get_url_from_access_page(page,findJsOrCss):
    if check_url(page) == False :
        return 0
    try:
        res = requests.get(page,verify=False,timeout=3)
        res.content.decode('utf-8', 'ignore')
    except Exception as e:
        print("\033[31m[-] timeout "+ page +"\033[0m") 
        return 0
    html = BeautifulSoup(res.text,"lxml")
    res.close()

    # 页面js css 
    if findJsOrCss == 1:
        scriptORcss = html.findAll("script")
        scriptORcss += html.findAll("link")
        scriptORcss += html.findAll("img")

        for s in scriptORcss:
            src = s.get("src") or s.get("href") 
            if src != None and src not in JsOrCssAccessFile:
                if src.startswith("//"):
                    url = urlInfo["scheme"]+ ":" + src
                    if check_url(url) :
                        print("\033[32m[+] 200 " + url + "\033[0m")
                        JsOrCssAccessFile.append(url)
                elif src.startswith("http"):
                    if check_url(src) :
                        print("\033[32m[+] 200 " + src + "\033[0m")
                        JsOrCssAccessFile.append(src)
                elif src.startswith("/"):
                    url = urlInfo["hostUrl"] + src
                    if check_url(url) :
                        print("\033[32m[+] 200 " + url + "\033[0m")
                        JsOrCssAccessFile.append(url)
                elif src != "":
                    # 检测传进来的是目录还是文件
                    if page.endswith('/') :
                        url = page + src
                    else:
                        url = urlInfo["hostUrlAndPath"][::-1].split("/",1)[1][::-1] + "/" + src
                    if check_url(url) :
                        print("\033[32m[+] 200 " + url + "\033[0m")
                        JsOrCssAccessFile.append(url)

                    
    # 爬取表单url
    forms = html.findAll("form")
    forms += html.findAll("a")
    if forms != None :
        for form in forms:
            f = form.get("action") or form.get("href") or ""
            # //开头的url
            if f.startswith("//"):
                url = urlInfo["scheme"]+ ":" +f
                if check_url(url) : accessPageTmp.append(url)
            # 网站绝对路径
            elif f.startswith("/"):
                url = urlInfo["hostUrl"] + f
                if check_url(url) : accessPageTmp.append(url)
            # 网址
            elif f.startswith("http"):
                if check_url(f) : accessPageTmp.append(f)
            elif f != "":
                # 检测传进来的是目录还是文件
                if page.endswith('/') : url = page + f
                else:
                    url = urlInfo["hostUrlAndPath"][::-1].split("/",1)[1][::-1] + "/" + f
                if check_url(url) : accessPageTmp.append(url)


def page_connect(url,findJsOrCss):
    if  url  in accessPage  and check_url(url) ==False :
        return 0

    # 测试页面是否可用
    try:
        res = requests.head(url,verify=False,timeout=3)
    except Exception as e:
        print("\033[31m[-] timeout "+ url +"\033[0m")  
        return 0
    if res.status_code in [200,301,500] :
        CL = 0
        if "Content-Length" in res.headers :
            CL = res.headers["Content-Length"]
        # 打印当前扫描结果
        print("\033[32m[+]  "+str(res.status_code)+"  " + str(CL).ljust(9) + "  " + url + " "  +"\033[0m")

        if url not in accessPage: accessPage.append(url)
        # 排除一些 下载文件，从而提高爬取速度
        if "Content-Type" in res.headers :
            CT = res.headers["Content-Type"]
            if CT.startswith("application") or CT.startswith("image") or CT.startswith("video") or CT.startswith("audio"):
                return 0
        # 爬取本页url 
        threading.Thread(target=get_url_from_access_page,args=(url,findJsOrCss,)).start()
        res.close()

    else :
        res.close()
        print("\033[33m[-] "+ str(res.status_code) +" " + url + "\033[0m")


def main_start():
    while len(dir_list) != 0 :
        dir = dir_list.pop()
        if dir.startswith("/") == False : dir = "/" + dir
        try :
            page_connect(urlInfo["hostUrl"] + dir.replace("\n",""),findJsOrCss)
        except Exception as e:
            print("\033[31m[*] "+ str(e) +"\033[0m")
    time.sleep(3)
    global processend
    processend += 1

if __name__ == "__main__":
    timetest = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="字典 (不选则爬取页面url)", dest="file", type=str, default="")
    parser.add_argument("-u", "--url", help="扫描url",  dest="url",type=str, default="")
    parser.add_argument("-t", "--thread", help="扫描线程（可选）", dest="thread" ,type=int, default=1)
    parser.add_argument("-s", "--static", help="检索静态文件（可选）", dest="static" ,type=int, default=0)
    args = parser.parse_args()

    if args.url == "":
        exit()
    scanUrl = args.url
    # 导入字典
    if args.file != "":
        try:
            with open(args.file,"r") as f:
                dir_list = f.readlines()
        except:
            print("导入文件错误")
            exit()
    # 静态资源
    if args.static != 0:
        findJsOrCss = 1

    if args.thread != 1 and  args.thread >0:
        count = args.thread
    # 获取 url 基本信息
    parseurl = urllib.parse.urlparse(scanUrl)
    urlInfo.update({"host":parseurl.hostname})
    urlInfo.update({"scheme":parseurl.scheme})
    urlInfo.update({"hostUrl":parseurl.scheme + "://" + urlInfo["host"]})
    hostUrlAndPath = urlInfo["hostUrl"] + parseurl.path
    urlInfo.update({"hostUrlAndPath" :hostUrlAndPath})
    # 检测爬取的页面
    threading.Thread(target=check_accessPageTmp,args=(findJsOrCss,)).start()

    # 基于字典的扫描
    dir_list.append(parseurl.path)
    for x in range(count):
        threading.Thread(target=main_start,args=()).start()
    
   

    

    