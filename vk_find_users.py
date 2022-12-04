import requests
import time
import re
import random


class VkBotFunc:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.url_get = 'https://api.vk.com/method/users.get'
        self.user_fields = 'city, sex, bdate'

    def user_info(self):
        params = {'user_ids': self.id, 'fields': self.user_fields}
        response = requests.get(self.url_get, params={**self.params, **params})
        time.sleep(0.33)
        return response.json()

    def get_users(self):
        list_ids = []
        list_users_data = []
        for counter in range(0, 10000):
            random_count = 0
            random_count += random.randint(0, 10000000)
            list_ids.append(random_count)
        for user_id in list_ids:
            params = {'user_ids': user_id, 'fields': self.user_fields}
            res = requests.get(self.url_get, params={**self.params, **params}).json()
            list_users_data.append(res)
            time.sleep(0.33)
        return list_users_data

    def select_users(self, users_data, sex_main, home_town_to_search, bdate_to_search):
        list_users_selection = []
        bdate_to_search_from = bdate_to_search - 5
        bdate_to_search_to = bdate_to_search + 5
        if sex_main == 2:
            sex_to_search = 1
        else:
            sex_to_search = 2
        for user in users_data:
            key1 = 'city'
            key2 = 'bdate'
            if key1 in user['response'][0].keys() and key2 in user['response'][0].keys():
                bdate_check = user['response'][0]['bdate']
                if len(bdate_check) == 9 or len(bdate_check) == 10:
                    # bdate_check_year = int(re.sub(r'.', '', bdate_check, count = 5))
                    bdate_main = bdate_check.split('.')
                    bdate_check_year = int(bdate_main[2])
                    if bdate_check_year >= bdate_to_search_from and bdate_check_year <= bdate_to_search_to:
                        user_sex = user['response'][0]['sex']
                        user_home_town = user['response'][0]['city']['id']
                        if user_sex == sex_to_search and user_home_town == home_town_to_search:
                            list_users_selection.append(user)
        return list_users_selection

