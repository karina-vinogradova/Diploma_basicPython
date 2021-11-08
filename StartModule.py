import BackupVk
import BackupOk
import YaUploader
import GoogleUploader
from pprint import pprint


class StartModule():

    def __init__(self, social):
        self.social = social

    def backup_vk(self, count, user_name):
            with open('token_vk.txt', 'r') as file_vk:
                token_vk = file_vk.readline()
            
            backuper = BackupVk.BackupVk(token_vk, user_name)
            response = BackupVk.BackupVk.get_photos(backuper, token_vk)
            photos = backuper.make_photos_dict(response, count)
            backuper.make_json_file(photos)

            return photos
        

    def backup_ok(self, count, user_name):
        with open('token_ok.txt', 'r') as file:
            access_token = file.readline()[:-1]
            application_key = file.readline()[:-1]
            session_secret_key = file.readline()[:-1]

        ok_loader = BackupOk.BackupOk(access_token, application_key, session_secret_key, user_name)
        response = ok_loader.get_photo_ok()
        id_dict = ok_loader.make_id_dict(response)
        photos = ok_loader.get_photos_name(id_dict, count)
        ok_loader.make_json_file(photos)
        
        return photos
       

    def upload_to_yandex_disk(self):
        
        # with open('token_ya.txt', 'r') as file_ya:
        #     token_ya = file_ya.readline()

        token_ya = input("Введите токен с Полигона Яндекс.Диска: ")
        uploader_ya = YaUploader.YaUploader(token_ya)
        uploader_ya.create_folder()

        if self.social == 'vk':
            count = int(input("Сколько фотографий вы хотите сохранить? "))
            user_name = input('Введите id или username пользователя: ')

            uploader_ya.upload(self.backup_vk(count, user_name))

        elif self.social == 'ok':
            count = int(input("Сколько фотографий вы хотите сохранить? "))
            user_name = input('Введите ID пользователя: ')

            uploader_ya.upload(self.backup_ok(count, user_name))

        else:
            pprint('Не знаю такой соц.сети')


    def upload_to_google_drive(self):

        # with open('token_google.txt', 'r') as file:
        #     read_token = file.readline().split('\n')[:-1]
        #     token_google = read_token[0]

        token_google = input("Введите токен для загрузки на Google Drive: ")
        uploader_google = GoogleUploader.GoogleUploader(token_google)
        files_list = uploader_google.get_auth()        
        
        if self.social == 'vk':
            count = int(input("Сколько фотографий вы хотите сохранить? "))
            user_name = input('Введите id или username пользователя: ')

            photos = self.backup_vk(count, user_name)
            folder_id = uploader_google.make_new_folder(files_list, self.social, user_name)
            uploader_google.upload(photos, folder_id)

        elif self.social == 'ok':
            count = int(input("Сколько фотографий вы хотите сохранить? "))
            user_name = input('Введите ID пользователя: ')

            photos = self.backup_ok(count, user_name)
            folder_id = uploader_google.make_new_folder(files_list, self.social, user_name)
            uploader_google.upload(photos, folder_id)

        else:
            pprint('Не знаю такой соц.сети')