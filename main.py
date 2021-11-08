import StartModule

from pprint import pprint

if __name__ == '__main__':
    
    social = input("Из какой соц.сети будем бэкапить фотки - VK или OK: ").lower()
    disk = input("Куда загрузить файлы - на Yandex.Disk или на Google Drive - yd / gd? ").lower()
    
    start_prog = StartModule.StartModule(social)
    
    if disk == 'yd':
        StartModule.StartModule.upload_to_yandex_disk(start_prog)

    elif disk == 'gd':
        StartModule.StartModule.upload_to_google_drive(start_prog)

    else:
        pprint('Не знаю такого хранилища')

    
    