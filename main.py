import os
import requests
from bs4 import BeautifulSoup
from time import sleep
import threading
from PIL import Image, ImageChops
import queue
import lxml

headers = {"User-Agent":"Mozilla/5.0"}


def make_dir(directory_name):
    if not os.path.isdir('dataset'):
        os.mkdir('dataset')
    if not os.path.exists(os.path.join('dataset', directory_name)):
        os.mkdir(os.path.join('dataset', directory_name))


def download_image(image_url, image_name, folder_name):
    response = requests.get(image_url, headers=headers).content

    file_name = open(os.path.join('dataset', folder_name, f"{image_name}.jpg"), 'wb')
    with file_name as handler:
        handler.write(response)


def get_image_url(flower_name):
    for page in range(1, 25):
        url = f'https://yandex.ru/images/search?p={page}&text={flower_name}'
        src = requests.get(url, headers=headers)
        soup = BeautifulSoup(src.text, "lxml")
        all_images = soup.find_all("a", class_="serp-item__link")
        for image in all_images:
            url_img = "https:" + image.find("img", class_="serp-item__thumb").get("src")
            yield url_img


class diff_image(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Получаем пару путей из очереди
            files = self.queue.get()
            self.difference_images(files.split(':')[0], files.split(':')[1])
            self.queue.task_done()

    def difference_images(self, img1, img2):
        image_1 = Image.open(img1)
        image_2 = Image.open(img2)

        size = [400, 300]
        image_1.thumbnail(size)
        image_2.thumbnail(size)

        result = ImageChops.difference(image_1, image_2).getbbox()
        if result == None:
            print(img1, img2, 'matches')
        return


def main_remove(path):
    imgs = os.listdir(path)
    queue = Queue()
    # Запускаем поток и очередь
    for i in range(4):
        t = diff_image(queue)
        t.setDaemon(True)
        t.start()
    check_file = 0
    current_file = 0

    while check_file < len(imgs):
        if current_file == check_file:
            current_file += 1
            continue
        queue.put(path + imgs[current_file] + ':' + path + imgs[check_file])
        current_file += 1
        if current_file == len(imgs):
            check_file += 1
            current_file = check_file
    queue.join()


def run(flower_name):
    count = 0
    make_dir(flower_name)
    for url in get_image_url(flower_name):
        download_image(url, str(count).zfill(4), flower_name)
        count += 1
        sleep(200)
        print(count, ' downloaded')


if __name__ == '__main__':
    run('rose')
    path_rose = 'dataset/rose'
    main_remove(path_rose)
    sleep(200)
    print('\n\n')
    run('tulip')
    path_tulip = 'dataset/tulip'
    main_remove(path_tulip)
    print('the end')