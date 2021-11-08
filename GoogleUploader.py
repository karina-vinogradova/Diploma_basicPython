from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
from tqdm import tqdm
import time
import json
import requests
from pprint import pprint

class GoogleUploader():

    def __init__(self, token_google):
        self.token_google = token_google
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.SERVICE_ACCOUNT_FILE = 'project.json'

        self.credentials = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        self.service = build('drive', 'v3', credentials=self.credentials)


    def get_auth(self):
        result = self.service.files().list(
                pageSize=100,fields="files(id, name), nextPageToken").execute()

        return result


    def make_new_folder(self, files_list, social, owner_id):
        date = datetime.datetime.now().strftime("%d-%b-%Y %H-%M-%S")
        find_name = files_list['files']
        for i in find_name:
            if i['name'] == 'Backups':
                folder_id = i['id']

        file_metadata = {
            'parents': [folder_id],
            'name': f'Backup{social}_{owner_id}_{date}',
            'mimeType': 'application/vnd.google-apps.folder'
        }

        file = self.service.files().create(body=file_metadata, fields='id').execute()
        folder_id = file['id']

        return folder_id


    def upload(self, photos, folder_id):
         
        upload_url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart'

        for photo_name, photo_url in photos.items():
            if type(photo_url) == list:
                path_to_file = f'{photo_url[0]}'
            elif type(photo_url) == str:
                path_to_file = f'{photo_url}'

            get_url = requests.get(f'{path_to_file}').content

            headers = {'Authorization': 'Bearer ' + self.token_google}

            params = {
                'name': f'{photo_name}.jpg',
                "parents": [folder_id]
            }

            files = {
                'data': ('metadata', json.dumps(params), 'application/json; charset=UTF-8'),
                'file': ('application/jpg', get_url)
            }

            result = requests.post(url=upload_url, params=params, headers=headers, files=files)
        
        for i in tqdm(str(photo_name)):
            time.sleep(0.15)
        pprint(f'Успешно загружено {len(photos)} файлов')