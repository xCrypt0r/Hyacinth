import json
import requests
import threading
import os.path
from urllib import request
from pathlib import Path
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class DCSweeper:
    def __init__(self, gui, gallery_id, gallery_title):
        self._timer = None
        self.gui = gui
        self.is_minor = gallery_title.startswith('ⓜ')
        self.is_stopped = False
        self.list_url = 'https://gall.dcinside.com/board/lists/'
        self.post_url = 'https://gall.dcinside.com/board/view/'
        self.gallery_id = gallery_id
        self.gallery_title = gallery_title
        self.ua = UserAgent()
        self.post_sweeped = []

        with open('assets/json/config.json', encoding='utf8') as config_file:
            config = json.load(config_file)
            self.folder = os.path.join(
                config['archive_path'],
                self.gallery_title
            )
            self.sweeping_interval = config['sweeping_interval']

        if self.is_minor:
            self.list_url = self.list_url.replace('board', 'mgallery/board')
            self.post_url = self.post_url.replace('board', 'mgallery/board')

    def run(self):
        threading.Timer(0.1, self.start_sweeping).start()

    def start_sweeping(self):
        if self.is_stopped:
            self._timer.cancel()

            return

        self.sweep_images_from_post(self.get_target_post())

        self._timer = threading.Timer(
            self.sweeping_interval,
            self.start_sweeping
        )
        self._timer.daemon = True

        self._timer.start()

    def stop_sweeping(self):
        self._timer.cancel()

        self.is_stopped = True

    def get_target_post(self):
        req = requests.get(
            self.list_url,
            params={ 'id': self.gallery_id },
            headers={ 'User-Agent': self.ua.random }
        )
        soup = BeautifulSoup(req.content, 'html.parser')
        tbody = soup.find('tbody')

        if tbody is None:
            return

        target = tbody.find('tr', { 'data-type': 'icon_pic' })
        target_post = target['data-no']

        return target_post

    def sweep_images_from_post(self, target_post):
        if target_post in self.post_sweeped:
            return

        self.post_sweeped.append(target_post)

        try:
            req = requests.get(
                self.post_url,
                params={ 'id': self.gallery_id, 'no': target_post },
                headers={ 'User-Agent': self.ua.random },
                timeout=5
            )
        except:
            return

        soup = BeautifulSoup(req.content, 'html.parser')
        appending_file = soup.find('ul', class_='appending_file')

        if appending_file is None:
            return

        post_title = soup.find('span', class_='title_subject').text
        post_date = soup.find('span', class_='gall_date').text
        attachments = appending_file.find_all('li')
        delta_count = 0

        print(f'[{post_date[-8:]}] <{self.gallery_title}> {post_title}')

        for i, attachment in enumerate(attachments):
            attachment_url = attachment.find('a', href=True)['href']
            extension = os.path.splitext(attachment_url)[1]
            opener = request.build_opener()
            opener.addheaders = [
                ('User-agent', self.ua.random),
                ('Referer', req.url)
            ]

            Path(self.folder).mkdir(parents=True, exist_ok=True)
            request.install_opener(opener)
            request.urlretrieve(
                attachment_url,
                os.path.join(
                    self.folder,
                    f'{self.gallery_id}_{target_post}_{i + 1}{extension}'
                )
            )

            delta_count += 1

        self.gui.update_signal.emit(self.gallery_title, delta_count)