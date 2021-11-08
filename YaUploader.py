import requests
import datetime
from tqdm import tqdm
import time
from pprint import pprint

class YaUploader():

    def __init__(self, token_ya):
        date = datetime.datetime.now().strftime("%d-%b-%Y %H-%M-%S")
        self.token_ya = token_ya
        self.path = f'Backup_{date}'

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def create_folder(self):
        URL = "https://cloud-api.yandex.net/v1/disk/resources"

        requests.put(f'{URL}?path={self.path}', headers=self.get_headers())

    def upload(self, photos):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"

        for key, value in photos.items():
            photo = f'{self.path}/{key}.jpg'
            if type(value) == list:
                path_to_file = f'{value[0]}'
            elif type(value) == str:
                path_to_file = f'{value}'

            params = {
                'path': photo,
                'url': path_to_file
            }

            response = requests.post(
                url=upload_url, params=params, headers=self.get_headers())
            response.raise_for_status()

            # if response.status_code == 202:
            #     pprint(f'Фотография с именем {key}.jpg загружается в папку {path_dir}')

        for i in tqdm(photo):
            time.sleep(0.05)
        pprint(f'Успешно загружено {len(photos)} файлов')
    