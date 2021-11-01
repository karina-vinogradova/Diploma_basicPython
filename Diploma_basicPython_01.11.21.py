from pprint import pprint
import requests
from datetime import date
import json
from tqdm import tqdm
import time


class PhotoBackup():
    
    def __init__(self, token_vk, token_ya, owner_id):
        self.token_vk = token_vk
        self.token_ya = token_ya
        self.owner_id = owner_id
        self.path = f'Backup_{date.today()}'


    def make_photos_dict(self, response):
        # count = int(input("Сколько фотографий загрузить на Яндекс.Диск? "))
        count = 5
        type_max = 0
        info_dict = {}
        sizes_list = ['s', 'm', 'x', 'o', 'p', 'q', 'r', 'y', 'z', 'w']
        for i in response['response']['items']:
            likes = i['likes']['count']
            date = i['date']

            for item in i['sizes']:
                if item['type'] in sizes_list:
                    if sizes_list.index(item['type']) > type_max:
                        type_max = sizes_list.index(item['type'])
            if count > 0:
                if likes in info_dict.keys():
                    key_dict = f'{likes}_{date}'
                    info_dict.setdefault(key_dict, [item['url'], item['type']])
                else:
                    info_dict.setdefault(likes, [item['url'], item['type']])
            count -= 1
        # Будет возвращать и сохранять самые популярные фотки
        # sorted_tuple = sorted(info_dict.items(), key=lambda x: x[0], reverse=True)
        # info_sorted_dict = dict(sorted_tuple)

        # return info_sorted_dict
        return info_dict


    def make_json_file(self, info_dict):
        name_size = []

        for file in info_dict:
            name_size.append({
                "file_name": f'{file}.jpg',
                "size": f'{info_dict[file][1]}'
            })
        with open(f'photo_info_{self.owner_id}.json', 'w') as info_file:
            json.dump(name_size, info_file, sort_keys=True, indent=0)


    def get_photos(self, token_vk):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': token_vk,
            'v': '5.131',
            'owner_id': '',
            'album_id': 'profile',
            'extended': '1'
        }

        while True:
            params['owner_id'] = self.owner_id
            if params['owner_id'].isdigit() == False:
                pprint('Введите id пользователя в виде числа!')
            else:
                break

        result = requests.get(url, params=params).json()
        return result

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
            path_to_file = f'{value[0]}'

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


if __name__ == '__main__':
    with open('token_vk.txt', 'r') as file_vk:
        token_vk = file_vk.readline()

    # with open('token_ya.txt', 'r') as file_ya:
    #     token_ya = file_ya.readline()

    owner_id = input('Введите id пользователя: ')
    token_ya = input("Введите токен с Полигона Яндекс.Диска: ")

    backuper = PhotoBackup(token_vk, token_ya, owner_id)
    response = PhotoBackup.get_photos(backuper, token_vk)
    backuper.create_folder()
    photos = backuper.make_photos_dict(response)
    info_file = backuper.make_json_file(photos)
    result = backuper.upload(photos)
