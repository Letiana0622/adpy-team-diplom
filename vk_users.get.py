def main():
    import requests
    import re
    import random
    from token_bot_vk import bot_token, bot_token_v
    import psycopg2
    token = bot_token_v

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
            return (list_users_data)

        def get_photos(self, selected_data, offset=0):
            photos_data = []
            for user in selected_data:
                user_id = user['response'][0]['id']  # User id is to be taken from DB when DB is ready
                url = 'https://api.vk.com/method/photos.get'
                params = {'owner_id': user_id,
                          'album_id': 'profile',
                          'access_token': token,
                          'v': '5.131',
                          'extended': '1',
                          # 'count': count,
                          'offset': offset
                          }
                res = requests.get(url=url, params=params).json()
                photos_data.append(res)
            selected_photos = []
            for response in photos_data:
                temp_dict = {}
                temp_list = []
                user_id = response['response']['items'][0]['owner_id']
                photo_url = response['response']['items'][0]['sizes'][0]['url']
                # first photo in album as likes are available per album not per photo
                photo_likes = response['response']['items'][0]['likes']['count']
                # likes are available to get only at album level// selction of best photos to be done via select requests to DB
                with psycopg2.connect(database="vk_bot_db", user="postgres", password="postgres") as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO vk_photo(vk_user_id, photo_link, photo_likes) VALUES
                            (%s,%s,%s)
                            RETURNING photo_id, vk_user_id, photo_link, photo_likes;
                            """, (user_id, photo_url, photo_likes,))
                        conn.commit()
                conn.close()
                temp_list.append(photo_url)
                temp_list.append(photo_likes)
                temp_dict[user_id] = temp_list
                selected_photos.append(temp_dict)
            return selected_photos  # to write response in DB when it is ready

    def select_users(users_data, sex_to_search, home_town_to_search, bdate_to_search_from, bdate_to_search_to):
        list_users_selection = []
        for user in users_data:
            key1 = 'home_town'
            key2 = 'bdate'
            if key1 in user['response'][0].keys() and key2 in user['response'][0].keys():
                bdate_check = user['response'][0]['bdate']
                if len(bdate_check) == 9:
                    bdate_check_year = int(re.sub(r'.', '', bdate_check, count=5))
                    if bdate_check_year >= bdate_to_search_from and bdate_check_year <= bdate_to_search_to:
                        user_sex = user['response'][0]['sex']
                        user_home_town = user['response'][0]['home_town']
                        if user_sex == sex_to_search and user_home_town == home_town_to_search:
                            list_users_selection.append(user)
                            #cоздаем таблицы в БД
                            vk_user_id = user['response'][0]['id']
                            with psycopg2.connect(database="vk_bot_db", user="postgres", password="postgres") as conn:
                                with conn.cursor() as cur:
                                    # удаление таблиц| когда уже созданы
                                    cur.execute("""
                                    DROP TABLE vk_photo;
                                    DROP TABLE vk_favorite;
                                    DROP TABLE vk_selected;
                                    """)

                                    # создание таблиц
                                    cur.execute("""
                                    CREATE TABLE IF NOT EXISTS vk_selected(
                                        user_id SERIAL PRIMARY KEY,
                                        vk_user_id INTEGER NOT NULL UNIQUE
                                    );
                                    """)
                                    cur.execute("""
                                    CREATE TABLE IF NOT EXISTS vk_photo(
                                        photo_id SERIAL PRIMARY KEY,
                                        vk_user_id INTEGER NOT NULL REFERENCES vk_selected(vk_user_id),
                                        photo_link TEXT NOT NULL,
                                        photo_likes INTEGER NOT NULL
                                     );
                                    """)

                                    cur.execute("""
                                    CREATE TABLE IF NOT EXISTS vk_favorite(
                                        favorite_id SERIAL PRIMARY KEY,
                                        vk_user_id INTEGER NOT NULL REFERENCES vk_selected(vk_user_id)
                                     );
                                    """)
                                    conn.commit()  # фиксируем в БД
                                    cur.execute("""
                                        INSERT INTO vk_selected(vk_user_id) VALUES
                                        (%s)
                                        RETURNING user_id, vk_user_id;
                                        """, (vk_user_id,))
                                    conn.commit()
                            conn.close()
        return (list_users_selection)

    def favorite_to_db():
        user_id = 'favorite_id' #необходимо связать с кнопкой выбора пользователя -> по выбору фото опрелелить user_id и запустить функцию записи в базу
        with psycopg2.connect(database="vk_bot_db", user="postgres", password="postgres") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO vk_favorite(vk_user_id) VALUES
                    (%s)
                    RETURNING favorite_id, vk_user_id;
                    """, (user_id,))
                conn.commit()
        conn.close()

    def select_user(conn, user_id):
        cur.execute("""
            SELECT vk_user_id FROM vk_selected
            WHERE
            (user_id = %s);
            """, (user_id,))
        print(cur.fetchall())

    def select_photos(conn, user_id_show):
        cur.execute("""
                        SELECT vk_user_id, photo_link, photo_likes FROM vk_photo
                        WHERE
                              (vk_user_id = %s)
                        ORDER BY photo_likes DESC
                        LIMIT 3;
                        """, (user_id_show,))
        print(cur.fetchall())

    with psycopg2.connect(database="vk_bot_db", user="postgres", password="postgres") as conn:
        with conn.cursor() as cur:
            user_id = 1 # увеличивать порядок при нажатии кнопки next
            user_id_show = select_user(conn,user_id)
            photo_links_show = select_photos(user_id_show)
            print(photo_links_show) # photo_links_show необходимо передать боту
    conn.close()

    sex_to_search = 1
    home_town_to_search = 'Москва'
    bdate_to_search = 1999
    bdate_to_search_from = bdate_to_search - 5
    bdate_to_search_to = bdate_to_search + 5

    downloader = VkDownloader(token)

    users_data = downloader.get_users()

    users_selected = select_users(users_data, sex_to_search, home_town_to_search, bdate_to_search_from,
                                  bdate_to_search_to)
    print(users_selected)

    photos_data = downloader.get_photos(users_selected)
    print(photos_data)


if __name__ == '__main__':
    main()