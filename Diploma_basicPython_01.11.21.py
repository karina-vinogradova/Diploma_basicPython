from pprint import pprint
import requests
from datetime import date
import json
from tqdm import tqdm
import time
import hashlib

class BackupVk():
    
    def __init__(self, token_vk, user_name):
        self.token_vk = token_vk
        self.user_name = user_name
        

    def make_photos_dict(self, response, count):
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

    def get_photos(self, token_vk):
        url = 'https://api.vk.com/method/users.get'
        params = {
            'user_ids': self.user_name,
            'access_token': token_vk,
            'v': '5.131'
        }
        user_id_conteiner = requests.get(url, params=params).json()
        for item in user_id_conteiner['response']:
            user_id = item['id']

        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': token_vk,
            'v': '5.131',
            'owner_id': '',
            'album_id': 'profile',
            'extended': '1'
        }

        params['owner_id'] = self.user_name
        if params['owner_id'].isdigit() == False:
            params['owner_id'] = user_id

        result = requests.get(url, params=params).json()
        return result


    def make_json_file(self, info_dict):
        name_size = []

        for file in info_dict:
            name_size.append({
                "file_name": f'{file}.jpg',
                "size": f'{info_dict[file][1]}'
            })
        with open(f'photo_info_vk_{self.user_name}.json', 'w') as info_file:
            json.dump(name_size, info_file, sort_keys=True, indent=0)


class BackupOk():
    def __init__(self, access_token, application_key, session_secret_key, fid):
        self.access_token = access_token
        self.application_key = application_key
        self.session_secret_key = session_secret_key
        self.fid = fid

    def get_photo_ok(self):        

        sig_str  = f'application_key={application_key}fid={self.fid}format=jsonmethod=photos.getPhotos{session_secret_key}'
        sig = (hashlib.md5(bytes(sig_str, encoding='utf-8'))).hexdigest()

        url = f'https://api.ok.ru/fb.do?application_key={application_key}&fid={self.fid}&format=json&method=photos.getPhotos&sig={sig}&access_token={access_token}'

        result = requests.get(url=url).json()
        return result


    def make_id_dict(self, photo_json):
        about = photo_json['photos']
        id_dict = {}
        for photo in about:
            id_dict[photo['id']] = photo['pic640x480']

        return id_dict


    def get_photos_name(self, id_dict, count):
        name_dict = {}
        for photo_id in id_dict.keys():
            sig_str = f'application_key={self.application_key}format=jsonmethod=photos.getPhotoInfophoto_id={photo_id}{session_secret_key}'
            sig = (hashlib.md5(bytes(sig_str, encoding='utf-8'))).hexdigest()
            url = f'https://api.ok.ru/fb.do?application_key={self.application_key}&format=json&method=photos.getPhotoInfo&photo_id={photo_id}&sig={sig}&access_token={self.access_token}'
        
            result = requests.get(url=url).json()

            find_likes = result['photo']
            for key, likes in find_likes.items():
                if key == 'like_count':
                    if count > 0:
                        if likes in name_dict.keys():
                            key_dict = f'{likes}_{photo_id}'
                            name_dict.setdefault(key_dict, id_dict[photo_id])
                        else:
                            name_dict.setdefault(likes, id_dict[photo_id])
                    count -= 1

        return name_dict

    def make_json_file(self, dict_for_upload):
        name_size = []

        for file in dict_for_upload:
            name_size.append({
                "file_name": f'{file}.jpg',
                "size": 'pic640x480'
            })
        with open(f'photo_info_ok_{self.fid}.json', 'w') as info_file:
            json.dump(name_size, info_file, sort_keys=True, indent=0)


class YaUploader():

    def __init__(self, token_ya):
        self.token_ya = token_ya
        self.path = f'Backup_{date.today()}'

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
            pprint(photo)
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
    


if __name__ == '__main__':
    with open('token_vk.txt', 'r') as file_vk:
        token_vk = file_vk.readline()

    # with open('token_ya.txt', 'r') as file_ya:
    #     token_ya = file_ya.readline()

    social = input("Из какой соц.сети будем бэкапить фотки - VK или OK: ").lower()
    

    if social == 'vk':
        token_ya = input("Введите токен с Полигона Яндекс.Диска: ")
        count = int(input("Сколько фотографий загрузить на Яндекс.Диск? "))
        user_name = input('Введите id или username пользователя: ')
        backuper = BackupVk(token_vk, user_name)
        response = BackupVk.get_photos(backuper, token_vk)
        photos = backuper.make_photos_dict(response, count)
        info_file = backuper.make_json_file(photos)
        uploader = YaUploader(token_ya)
        uploader.create_folder()
        result = uploader.upload(photos)

    elif social == 'ok':
        token_ya = input("Введите токен с Полигона Яндекс.Диска: ")
        count = int(input("Сколько фотографий загрузить на Яндекс.Диск? "))
        fid = input("Введите ID пользователя: ")

        with open('token_ok.txt', 'r') as file:
            access_token = file.readline()[:-1]
            application_key = file.readline()[:-1]
            session_secret_key = file.readline()[:-1]

        ok_loader = BackupOk(access_token, application_key, session_secret_key, fid)
        response = ok_loader.get_photo_ok()
        id_dict = ok_loader.make_id_dict(response)
        dict_for_upload = ok_loader.get_photos_name(id_dict, count)
        info_file = ok_loader.make_json_file(dict_for_upload)
        uploader = YaUploader(token_ya)
        uploader.create_folder()
        result = uploader.upload(dict_for_upload)

    else:
        pprint('Не знаю такой соц.сети')
    
    