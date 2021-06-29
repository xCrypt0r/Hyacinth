import requests
import threading
import os.path
import urllib3
from urllib import request
from pathlib import Path
from bs4 import BeautifulSoup

class DCSweeper:
    def __init__(self, target_gallery, gallery_title):
        self.list_url = 'https://gall.dcinside.com/board/lists/'
        self.post_url = 'https://gall.dcinside.com/board/view/'
        self.target_gallery = target_gallery
        self.gallery_title = gallery_title
        self.headers = { 'User-Agent': '' }
        self.post_sweeped = []

    def start_sweeping(self):
        self.sweep_images_from_post(self.get_target_post())
        threading.Timer(2, self.start_sweeping).start()

    def get_target_post(self):
        req = requests.get(self.list_url,
            params={ 'id': self.target_gallery },
            headers=self.headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        target = soup.find('tbody').find('tr', { 'data-type': 'icon_pic' })
        target_post = target['data-no']

        return target_post

    def sweep_images_from_post(self, target_post):
        if target_post in self.post_sweeped:
            return

        self.post_sweeped.append(target_post)

        try:
            req = requests.get(self.post_url,
                params={ 'id': self.target_gallery, 'no': target_post },
                headers=self.headers)
        except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError):
            return

        soup = BeautifulSoup(req.content, 'html.parser')
        appending_file = soup.find('ul', class_='appending_file')
        post_title = soup.find('span', class_='title_subject').text
        post_date = soup.find('span', class_='gall_date').text

        if appending_file is None:
            return

        print(f'[{post_date[-8:]}] <{self.gallery_title}> {post_title}')

        attachments = appending_file.find_all('li')

        for i, attachment in enumerate(attachments):
            attachment_url = attachment.find('a', href=True)['href']
            extension = os.path.splitext(attachment_url)[1]
            opener = request.build_opener()

            opener.addheaders = [('User-agent', ''), ('Referer', req.url)]

            Path(f'archive/{self.gallery_title}').mkdir(parents=True, exist_ok=True)
            request.install_opener(opener)
            request.urlretrieve(attachment_url,
                f'archive/{self.gallery_title}/{self.target_gallery}_{target_post}_{i + 1}{extension}')