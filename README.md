

单线程爬虫

多线程字典扫描

爬虫的结果会导入扫描器继续扫描

扫描结果为200的同时会交给爬虫处理 python

支持未认证的https



```
usage: index.py [-h] [-f FILE] [-u URL] [-t THREAD] [-s STATIC]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  字典 (不选则爬取页面url)
  -u URL, --url URL     扫描url
  -t THREAD, --thread THREAD
                        扫描线程（可选）
  -s STATIC, --static STATIC
                        检索静态文件（可选）
```



![image-20210320125857607](https://blog-1300884845.cos.ap-shanghai.myqcloud.com/wenzhang/image-20210320125857607.png)



![image-20210320125930060](https://blog-1300884845.cos.ap-shanghai.myqcloud.com/wenzhang/image-20210320125930060.png)

