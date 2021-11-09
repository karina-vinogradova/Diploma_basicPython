from pprint import pprint
import requests
import json
import hashlib

class BackupOk():

    def __init__(self, access_token, application_key, session_secret_key, fid):
        self.access_token = access_token
        self.application_key = application_key
        self.session_secret_key = session_secret_key
        self.fid = fid

    def get_photo_ok(self):        

        sig_str  = f'application_key={self.application_key}fid={self.fid}format=jsonmethod=photos.getPhotos{self.session_secret_key}'
        sig = (hashlib.md5(bytes(sig_str, encoding='utf-8'))).hexdigest()

        url = f'https://api.ok.ru/fb.do?application_key={self.application_key}&fid={self.fid}&format=json&method=photos.getPhotos&sig={sig}&access_token={self.access_token}'

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
            sig_str = f'application_key={self.application_key}format=jsonmethod=photos.getPhotoInfophoto_id={photo_id}{self.session_secret_key}'
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

