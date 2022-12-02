def main():

    import requests
    import re
    import random
    from token_bot_vk import bot_token

    token = bot_token
    class VkDownloader:

        def __init__(self, token):
            self.token = token

        def get_users(self):
            list_ids = []
            counter = 0
            for counter in range(0, 1000):
                Random = 0
                Random += random.randint(0, 10000000)
                list_ids.append(Random)
                counter += 1
            print(list_ids)
            list_users_data = []
            for user_id in list_ids:
                url = 'https://api.vk.com/method/users.get'
                params = {'user_ids': user_id,
                      'access_token': token,
                      'v': '5.131',
                      'fields': 'id, home_town, sex, bdate'
                      }
                res = requests.get(url=url, params=params).json()
                list_users_data.append(res)
            return(list_users_data)

    def select_users(users_data, sex_to_search, home_town_to_search, bdate_to_search_from, bdate_to_search_to):
        list_users_selection = []
        for user in users_data:
            key1 = 'home_town'
            key2 = 'bdate'
            if key1 in user['response'][0].keys() and key2 in user['response'][0].keys():
                bdate_check = user['response'][0]['bdate']
                if len(bdate_check) == 9:
                    bdate_check_year = int(re.sub(r'.', '', bdate_check, count = 5))
                    if bdate_check_year >= bdate_to_search_from and bdate_check_year <= bdate_to_search_to:
                        user_sex = user['response'][0]['sex']
                        user_home_town = user['response'][0]['home_town']
                        if user_sex == sex_to_search and user_home_town == home_town_to_search:
                            list_users_selection.append(user)
        return(list_users_selection)

    sex_to_search = 1
    home_town_to_search = 'Москва'
    bdate_to_search = 1999

    bdate_to_search_from = bdate_to_search - 5
    bdate_to_search_to = bdate_to_search + 5
    downloader = VkDownloader(token)
    users_data = downloader.get_users()
    users_selected = select_users(users_data, sex_to_search, home_town_to_search, bdate_to_search_from, bdate_to_search_to)
    # while len(users_selected) <= 4:
    #     users_data_ = downloader.get_users()
    #     users_selected_ = select_users(users_data, sex_to_search, home_town_to_search, bdate_to_search_from,
    #                                   bdate_to_search_to)
    #     users_selected.append(users_selected_)
    print(users_selected)

if __name__ == '__main__':
    main()