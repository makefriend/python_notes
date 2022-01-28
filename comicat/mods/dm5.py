import re
from typing import List

import execjs
import requests
from lxml import etree
from parsel import SelectorList, Selector

from entity import *
from mods.website_interface import WebsiteInterface


class DM5Comicat(WebsiteInterface):

    def down_image(self, image_info) -> bytes:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/97.0.4692.99 Safari/537.36',
            'referer': 'https://www.dm5.com{}'.format(image_info['dm5Curl'])
        }
        response = requests.get(image_info.url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            return None

    def parse_image_list(self, chapter_info) -> List[ImageInfo]:
        image_list = []
        response = etree.HTML(requests.get(chapter_info.url).text)
        cid = re.findall('var DM5_CID=(.+?);', response.text)[0].strip()
        page_count = re.findall('var DM5_IMAGE_COUNT=(.+?);', response.text)[0].strip()
        mid = re.findall('var DM5_MID=(.+?);', response.text)[0].strip()
        dt = re.findall('var DM5_VIEWSIGN_DT="(.+?)";', response.text)[0].strip()
        sign = re.findall('var DM5_VIEWSIGN="(.*?)";', response.text)[0].strip()
        dm5Curl = re.findall('var DM5_CURL = "(.*?)";', response.text)[0].strip()
        for page in range(1, int(page_count) + 1):
            chapterfun_url = "{}/chapterfun.ashx?cid={}&page={}&key=&language=1&gtk=6&_cid={}&_mid={}&_dt={}&_sign={}" \
                .format(response.url, cid, page, cid, mid, dt, sign)
            response = requests.get(chapterfun_url)
            js = execjs.eval(response.text)
            info = ImageInfo()
            info.url = js[0]
            info['dm5Curl'] = dm5Curl
            image_list.append(info)
        return image_list

    def chapter_callback(self, comic_info: ComicInfo, callback):
        for chapter_info in comic_info.chapterList:
            callback(chapter_info)
        return comic_info.chapterList

    def __init__(self):
        self.webSiteName = "dm5"
        self.searchUrl = "https://www.dm5.com/search?title={}"
        self.domain = "https://www.dm5.com"

    def search_callback(self, key, callback) -> list[ComicInfo]:
        comic_info_list: List[ComicInfo] = []
        url = self.searchUrl.format(key)
        response = requests.get(url)
        if response.status_code != 200:
            print(url, response.status_code)
        else:
            tree = etree.HTML(response.text)
            info = self.dm5_info(self.domain + tree.xpath("//div[@class='info']/p[@class='title']/a/@href")[0])
            info.service = self
            callback(info)
            comic_info_list.append(info)
            for i in tree.xpath("/html/body/section[2]/div/ul/li/div/div[2]/div/a/@href"):
                info = self.dm5_info(self.domain + i)
                info.service = self
                callback(info)
                comic_info_list.append(info)
        return comic_info_list

    def dm5_info(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            print(url, response.status_code)
            return None
        else:
            info = ComicInfo()
            info.url = url
            info.domain = self.webSiteName
            tree = etree.HTML(response.text)
            info.title = tree.xpath("//div[@class='info']/p[@class='title']/text()")[0].strip()
            info.author = tree.xpath("//div[@class='info']/p[@class='subtitle']/a/text()")[0].strip()
            info.describe = tree.xpath("//div[@class='info']/p[@class='content']/text()")[0].strip()
            describe2 = tree.xpath("//div[@class='info']/p[@class='content']/span/text()")
            if describe2:
                info.describe += describe2[0].strip()
            info.status = tree.xpath("//div[@class='info']/p[@class='tip']/span/span/text()")[0].strip()
            info.coverUrl = tree.xpath("//div[@class='cover']/img/@src")[0].strip()
            info.tip = ",".join(tree.xpath("//div[@class='info']/p[@class='tip']/span/a/span/text()"))
            # info.cover = requests.get(info.coverUrl).content #TODO 本地测试

            # 这个网站直接爬章节, 放到comicinfo对象中,获取章节的时候,不用再请求一次
            alist: SelectorList = tree.xpath("//ul[@class='view-win-list detail-list-select']/li/a")
            for a in alist:
                a: Selector
                chapter_info = ChapterInfo()
                chapter_info.title = a.text
                chapter_info.url = self.domain + a.attrib.get("href")
                info.chapterList.append(chapter_info)
            return info


if __name__ == '__main__':
    s = DM5Comicat()


    def test(info):
        pass


    l = s.search_callback("龙珠", test)
    for c in l:
        c: ComicInfo
        print(c.title)
        print(c.url)
        print(c.author)
        print(c.describe)