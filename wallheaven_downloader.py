import os
import requests
from lxml import etree
import time
from queue import Queue
import threading
import re


class Spider:

    def __init__(self, head, path, q, start_page=1, end_page=1, resolution="2560x1080", atleast="atleast"):
        self.head = head
        self.path = path
        self.q = q
        self.start_page = start_page
        self.end_page = end_page
        self.resolution = resolution
        self.atleast = atleast

    def get(self):
        for i in range(self.start_page, self.end_page + 1):
            url = f"https://wallhaven.cc/search?q=id%3A5&categories=110&purity=100&{self.atleast}={self.resolution}&sorting=favorites&order=desc&page={i} "
            _request = requests.get(url, headers=self.head).text
            html = etree.HTML(_request)
            tree = html.xpath('//*/a[@class="preview"]/@href')
            for links in tree:
                time.sleep(0.5)  # 本次采用多线程,访问过快会导致出错,所以暂停0.5秒再继续
                sub_request = requests.get(links, headers=self.head).text
                sub_html = etree.HTML(sub_request)
                sub_tree = sub_html.xpath('//*/div[@class="scrollbox"]/img/@src')
                self.q.put(sub_tree[0])

    def download(self):
        count = 0
        while True:
            time.sleep(1)
            names = self.q.get()
            pic_req = requests.get(names, headers=self.head).content
            nums = names.rfind("/")
            print(f"Downloading: [ {count + 1} ] {names[nums + 1::]}")
            count += 1
            try:
                with open(self.path + "/" + names[nums::], 'wb') as f:
                    f.write(pic_req)
                    if self.q.empty():
                        break
            except FileNotFoundError:
                os.mkdir(self.path)


def get_count(head, resolution="2560x1080", atleast="atleast"):
    url = f"https://wallhaven.cc/search?q=id%3A5&categories=110&purity=100&{atleast}={resolution}&sorting=favorites&order=desc&page=1"
    requests_ = requests.get(url, head).text
    html = etree.HTML(requests_)
    get_count__ = html.xpath('//*[@id="main"]//h1/text()')
    nums = re.findall('[0-9]', get_count__[0])
    final = int("".join(nums))
    print(f"Total pictures: {final}")
    if final < 24 or final > 24:
        total_pages = int(final / 24 + 1)
    else:
        total_pages = 1

    print(f"Total pages: {total_pages}")


def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/84.0.4147.89 Safari/537.36 "
    head = {"user-agent": user_agent}
    q = Queue()
    path = "./wallheaven_test"
    print("[ + ] Tip: This website needs VPN to get faster")
    print("[ + ] 注: 一页24张壁纸")
    print("[ 1 ] 从第一页开始下载 ")
    print("[ 2 ] 从您输入的页面位置开始下载 ")
    set_pages = int(input("请选择:"))
    if set_pages == 1:
        resolution = str(input("请输入图片分辨率(如果留空则使用默认分辨率2560x1080):"))
        print("[ 1 ] 图片分辨率大于等于输入的分辨率")
        print("[ 2 ] 图片分辨率等于输入的分辨率")
        atleast = str(input("请选择(如果留空则默认选择第一种):"))
        if resolution == "" and (atleast == "" or atleast == "1"):
            get_count(head, atleast="atleast")
        elif resolution == "" and atleast == "2":
            get_count(head, atleast="resolutions")
        elif resolution != "" and (atleast == "" or atleast == "1"):
            get_count(head, resolution)
        elif resolution != "" and atleast == "2":
            get_count(head, resolution, "resolutions")
        pages = int(input("请输入下载的页数:"))
        if resolution == "" and (atleast == "" or atleast == "1"):
            spider = Spider(head, path, q, end_page=pages)
            t1 = threading.Thread(target=spider.get)
            t1.start()
            t2 = threading.Thread(target=spider.download)
            t2.start()
        elif resolution == "" and atleast == "2":
            spider = Spider(head, path, q, end_page=pages, atleast="resolutions")
            t1 = threading.Thread(target=spider.get)
            t1.start()
            t2 = threading.Thread(target=spider.download)
            t2.start()
        elif resolution != "" and (atleast == "" or atleast == "1"):
            spider = Spider(head, path, q, end_page=pages, resolution=resolution)
            t1 = threading.Thread(target=spider.get)
            t1.start()
            t2 = threading.Thread(target=spider.download)
            t2.start()
        elif resolution != "" and atleast == "2":
            spider = Spider(head, path, q, end_page=pages, resolution=resolution, atleast="resolutions")
            t1 = threading.Thread(target=spider.get)
            t1.start()
            t2 = threading.Thread(target=spider.download)
            t2.start()
    elif set_pages == 2:
        resolution = str(input("请输入图片分辨率(如果留空则使用默认分辨率2560x1080):"))
        print("[ 1 ] 图片分辨率大于等于输入的分辨率")
        print("[ 2 ] 图片分辨率等于输入的分辨率")
        atleast = str(input("请选择(如果留空则默认选择第一种):"))
        if resolution == "" and (atleast == "" or atleast == "1"):
            get_count(head, atleast="atleast")
        elif resolution == "" and atleast == "2":
            get_count(head, atleast="resolutions")
        elif resolution != "" and (atleast == "" or atleast == "1"):
            get_count(head, resolution)
        elif resolution != "" and atleast == "2":
            get_count(head, resolution, "resolutions")
        print("[ + ] 注: 页数包括起始页和结束页")
        start_pages = int(input("请输入起始页:"))
        end_pages = int(input("请输入结束页:"))
        if resolution == "" and (atleast == "" or atleast == "1"):
            spider = Spider(head, path, q, start_pages, end_pages)
            t1 = threading.Thread(target=spider.get)
            t1.start()
            t2 = threading.Thread(target=spider.download)
            t2.start()
        elif resolution == "" and atleast == "2":
            spider = Spider(head, path, q, start_pages, end_pages, atleast="resolutions")
            t1 = threading.Thread(target=spider.get)
            t1.start()
            t2 = threading.Thread(target=spider.download)
            t2.start()
        elif resolution != "" and (atleast == "" or atleast == "1"):
            spider = Spider(head, path, q, start_pages, end_pages, resolution=resolution)
            t1 = threading.Thread(target=spider.get)
            t1.start()
            t2 = threading.Thread(target=spider.download)
            t2.start()
        elif resolution != "" and atleast == "2":
            spider = Spider(head, path, q, start_pages, end_pages, resolution=resolution, atleast="resolutions")
            t1 = threading.Thread(target=spider.get)
            t1.start()
            t2 = threading.Thread(target=spider.download)
            t2.start()


if __name__ == '__main__':
    main()
