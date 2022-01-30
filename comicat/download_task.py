import os
import random
import time
import typing
import urllib

from entity import ComicInfo, ChapterInfo, ImageInfo
from mods.website_interface import WebsiteInterface


class DownloadTask(object):
    comicInfo: ComicInfo
    chapterInfo: ChapterInfo
    imageInfos: typing.List[ImageInfo]
    success = typing.List[str]
    error = typing.List[str]
    widget: object
    status: int = 0  # 0 等待开始 1 开始 2 暂停  -1 完成
    doneNum = 0

    def __init__(self):
        self.success = {}
        self.error = {}

    def download_image_thread(self):
        if self.status == 0 or self.status == 1:
            self.status = 1
            filePath = f"/Users/bo/my/tmp/comicat_down/{self.comicInfo.title}/{self.chapterInfo.title}/"
            if not os.path.exists(filePath):
                os.makedirs(filePath)
            for page in range(len(self.success) + len(self.error) + 1, len(self.imageInfos) + 1):
                if self.status != 1:
                    return
                web_service = self.comicInfo.service
                web_service: WebsiteInterface
                image_path = filePath + ("%0{}d".format(len(str(len(self.imageInfos)))) % page) + \
                             os.path.splitext(urllib.parse.urlparse(self.imageInfos[page - 1].url).path)[-1]
                self.success[image_path] = page
                # time.sleep(random.randint(0, 5))
                time.sleep(0.3)
                # web_service.down_image(task.imageInfos[page])
                self.doneNum += 1
                # 更新下载状态
                self.widget.update_task(self)
            self.status = -1
            print("下载完成")
            self.widget.update_task(self)
        elif self.status == -1:  # 重试error列表
            filePath = f"/Users/bo/my/tmp/comicat_down/{self.comicInfo.title}/{self.chapterInfo.title}/"
            if not os.path.exists(filePath):
                os.makedirs(filePath)
            for k, v in self.error:
                web_service = self.comicInfo.service
                web_service: WebsiteInterface
                image_path = filePath + ("%0{}d".format(len(str(len(self.imageInfos)))) % v) + \
                             os.path.splitext(urllib.parse.urlparse(k).path)[-1]
                self.success[image_path] = k
                time.sleep(random.randint(0, 5))
                # web_service.down_image(task.imageInfos[page])
                self.doneNum += 1
                # 更新下载状态
                self.widget.update_task(self)
                self.error.pop(k)
                self.widget.update_task(self)