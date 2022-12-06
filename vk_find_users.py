import requests
import time


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

    def get_users(self, sex_main, home_town_to_search):
        list_users_data = []
        params = {'count': 1000, 'fields': self.user_fields}
        res = requests.get(self.url_search, params={**self.params_search, **params}).json()
        list_users_data.append(res)
        time.sleep(0.33)
        return list_users_data

    def select_users(self, users_data_package, sex_main, home_town_to_search, bdate_to_search):
        list_users_selection = []
        bdate_to_search_from = bdate_to_search - 5
        bdate_to_search_to = bdate_to_search + 5
        if sex_main == 2:
            sex_to_search = 1
        else:
            sex_to_search = 2
        for users_data in users_data_package[0]['response']['items']:
            key1 = 'city'
            key2 = 'bdate'
            if key1 in users_data.keys() and key2 in users_data.keys():
                bdate_check = users_data['bdate']
                if len(bdate_check) == 9 or len(bdate_check) == 10:
                    bdate_main = bdate_check.split('.')
                    bdate_check_year = int(bdate_main[2])
                    if bdate_check_year >= bdate_to_search_from and bdate_check_year <= bdate_to_search_to:
                        user_sex = users_data['sex']
                        user_home_town = users_data['city']['id']
                        if user_sex == sex_to_search and user_home_town == home_town_to_search:
                            list_users_selection.append(users_data)
        return list_users_selection

    def get_photos(self, selected_data, offset=0):
        photos_data = []
        for user in selected_data:
            user_id = user['id']  # User id is to be taken from DB when DB is ready
            url = 'https://api.vk.com/method/photos.get'
            params = {'owner_id': user_id,
                      'album_id': 'profile',
                      'access_token': self.token_user,
                      'v': '5.131',
                      'extended': '1',
                      # 'count': count,
                      'offset': offset
                      }
            res = requests.get(url=url, params=params).json()
            photos_data.append(res)
        selected_photos = []
        for response in photos_data:
            try:
                if response['response']['count'] != 0:
                    temp_dict = {}
                    temp_list = []
                    user_id = response['response']['items'][0]['owner_id']
                    photo_url = response['response']['items'][0]['sizes'][0]['url']
                    # first photo in album as likes are available per album not per photo
                    photo_likes = response['response']['items'][0]['likes']['count']
                    # likes are available to get only at album level// selction of best photos to be done via select requests to DB
                    temp_list.append(photo_url)
                    temp_list.append(photo_likes)
                    temp_dict['user_id'] = user_id
                    temp_dict['user_photo_data'] = temp_list
                    selected_photos.append(temp_dict)
            except KeyError:
                pass
        return selected_photos  # to write response in DB when it is ready

