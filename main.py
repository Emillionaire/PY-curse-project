import datetime
import time
import urllib.request
import requests
import io
from progress.bar import IncrementalBar
from pprint import pprint

METHODS = ['https://api.vk.com/method/users.get', 'https://api.vk.com/method/photos.get']
URL = 'https://cloud-api.yandex.net/v1/disk/resources'


def input_data():
    # Take input data
    data_list = ['TOKEN_VK', 'TOKEN_YD', 'target_user', 'quantity_files']
    data_dict = {}
    i = 0
    with open('input_data.txt') as data:
        for row in data:
            data_dict[data_list[i]] = row.split('=')[1].strip()
            i += 1
    return data_dict


def search_id(user, token_vk):
    # Search user id by unic name
    params = {
        'user_ids': user,
        'access_token': token_vk,
        'v': '5.131'
    }
    res = requests.get(METHODS[0], params=params)
    user_id = res.json()['response'][0]['id']
    return user_id


def get_largest_avatar_photo(name_or_id, token_vk):
    if not str(name_or_id).isdigit():
        user_id = search_id(name_or_id, token_vk)
    else:
        user_id = name_or_id
    params = {
        'owner_id': user_id,
        'access_token': token_vk,
        'v': '5.131',
        'album_id': 'profile',
        'extended': 1
    }
    res = requests.get(METHODS[1], params=params)
    data_list = []
    for i in range(res.json()['response']['count']):
        max_height = 0
        k = 0
        position_max_size_photo = 0
        for j in res.json()['response']['items'][i]['sizes']:
            if j['height'] > max_height:
                max_height = j['height']
                position_max_size_photo = k
            k += 1
        time = datetime.datetime.fromtimestamp(res.json()['response']['items'][i]['date'])
        photo_url = res.json()['response']['items'][i]['sizes'][position_max_size_photo]['url']
        photo_like = res.json()['response']['items'][i]['likes']['count']
        photo_upload_date = str(f'{time:%Y-%m-%d_%H-%M-%S}')
        push = [photo_url, photo_like, photo_upload_date]
        data_list.append(push)
    return data_list


def upload_photo_to_disk():
    # Take input data
    # TOKEN_VK, TOKEN_YD, target_user, quantity_files
    data_dict = input_data()
    # Create folder
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'OAuth {data_dict["TOKEN_YD"]}'
    }
    requests.put(f'{URL}?path={data_dict["target_user"]}', headers=headers)
    # Upload files
    data_list = get_largest_avatar_photo(data_dict["target_user"], data_dict['TOKEN_VK'])
    output_data = []
    j = 0
    bar = IncrementalBar('Файлов загружено', max=len(data_list))
    print(f'Вы хотите загрузить {data_dict["quantity_files"]} фотографий из {len(data_list)}.\n')
    for i in data_list:
        if j >= int(data_dict['quantity_files']):
            break
        else:
            bar.next()
            res = requests.get(f'{URL}/upload?path={data_dict["target_user"]}/L-{i[1]}, D-{i[2]}&overwrite=True', headers=headers).json()
            with urllib.request.urlopen(i[0]) as url:
                f = io.BytesIO(url.read())
                requests.put(res['href'], files={'file':f})
            output_data.append({'file_name': f'L-{i[1]}, D-{i[2]}'})
            j += 1
        time.sleep(1)
    bar.finish()
    print('\nЗагрузка окончена!')
    return pprint(output_data)


upload_photo_to_disk()
