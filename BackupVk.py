import requests
import json

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

