import requests
import time
import datetime
from data_base import create_db, add_user, add_photo


class VkBotFunc:

    def __init__(self, access_token, access_token_user, user_id, version='5.131'):
        self.token = access_token
        self.token_user = access_token_user
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.params_search = {'access_token': self.token_user, 'v': self.version}
        self.url_get = 'https://api.vk.com/method/users.get'
        self.url_search = 'https://api.vk.com/method/users.search'
        self.user_fields = 'city, sex, bdate'

    def user_info(self):
        params = {'user_ids': self.id, 'fields': self.user_fields}
        response = requests.get(self.url_get, params={**self.params, **params})
        time.sleep(0.33)
        return response.json()

    def get_users(self, sex_main, home_town_to_search, bdate_to_search, offset=0):
        create_db()
        photos_data = []
        list_users_data = []
        list_users_selection = []
        if sex_main == 2:
            sex_to_search = 1
        else:
            sex_to_search = 2
        time_now = datetime.datetime.now()
        year_now = time_now.year
        age_search_from = year_now - bdate_to_search - 5
        age_search_to = year_now - bdate_to_search + 5
        params = {'count': 50,
                  'city': home_town_to_search,
                  'sex': sex_to_search,
                  'age_from': age_search_from,
                  'age_to': age_search_to,
                  'fields': self.user_fields}
        res = requests.get(self.url_search, params={**self.params_search, **params}).json()
        list_users_data.append(res)
        time.sleep(0.33)
        for users_data in list_users_data[0]['response']['items']:
            list_users_selection.append(users_data)
            vk_user_id = users_data['id']
            add_user(vk_user_id)
            user_id = users_data['id']  # User id is to be taken from DB when DB is ready
            url = 'https://api.vk.com/method/photos.get'
            params = {'owner_id': user_id,
                      'album_id': 'profile',
                      'access_token': self.token_user,
                      'v': '5.131',
                      'extended': '1',
                      'offset': offset
                      }
            res = requests.get(url=url, params=params).json()
            time.sleep(0.2)
            photos_data.append(res)
        for response in photos_data:
            try:
                if response['response']['count'] != 0:
                    user_id = response['response']['items'][0]['owner_id']
                    # first photo in album as likes are available per album not per photo
                    photo_likes = response['response']['items'][0]['likes']['count']
                    for correct_size in response['response']['items'][0]['sizes']:
                        if correct_size['type'] == 'x':
                            photo_url = correct_size['url']
                            add_photo(user_id, photo_url, photo_likes)
            except KeyError:
                pass
