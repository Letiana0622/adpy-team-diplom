import requests
import time


class VkBotFunc:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def user_info(self):
        url = 'https://api.vk.com/method/users.get'
        main_user_fields = 'city, sex, bdate'
        params = {'user_ids': self.id, 'fields': main_user_fields}
        response = requests.get(url, params={**self.params, **params})
        time.sleep(0.33)
        return response.json()


