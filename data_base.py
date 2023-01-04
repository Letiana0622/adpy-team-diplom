import psycopg2
from settings import database, user, password


def create_db():
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        DROP TABLE vk_photo;
                        DROP TABLE vk_favorite;
                        DROP TABLE vk_selected;
                        """)

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
                        vk_user_main VARCHAR NOT NULL,
                        vk_user_id VARCHAR NOT NULL,
                        vk_photo_url VARCHAR NOT NULL
                        );
                        """)
            conn.commit()
    conn.close()


# по комментариям записываем в таблицу только 1 ИД/1й - необходимо доработать в основных модулях
def add_user(vk_user_id):
    with psycopg2.connect(database=database, user=user, password=password) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO vk_selected(vk_user_id) VALUES
                            (%s)
                            RETURNING user_id, vk_user_id;
                            """, (vk_user_id,))
                conn.commit()
    conn.close()

def add_photo(user_id, photo_url, photo_likes):
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO vk_photo(vk_user_id, photo_link, photo_likes) VALUES
                        (%s,%s,%s)
                        RETURNING photo_id, vk_user_id, photo_link, photo_likes;
                        """, (user_id, photo_url, photo_likes,))
            conn.commit()
    conn.close()


def add_favorite(user_main, favorite_id, photo_url):
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO vk_favorite(vk_user_main, vk_user_id, vk_photo_url) VALUES
                        (%s, %s, %s)
                        RETURNING favorite_id, vk_user_id;
                        """, (user_main, favorite_id, photo_url,))
            conn.commit()
    conn.close()

def select_photo(user_id):
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT photo_link FROM vk_photo
                        WHERE vk_user_id = %s;
                        """, (user_id,))
            photo_data = cur.fetchall()
    conn.close()
    return photo_data


def select_user(number_photo):
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT vk_user_id FROM vk_selected
                        WHERE user_id = %s;
                        """, (number_photo,))
            user_data = cur.fetchall()
    conn.close()
    return user_data


def select_user_count():
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT * FROM vk_photo;
                        """)
            user_data = cur.fetchall()
    conn.close()
    return user_data


def select_favorite_user(number_photo):
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT vk_user_id, vk_photo_url FROM vk_favorite
                        WHERE favorite_id = %s;
                        """, (number_photo,))
            user_data = cur.fetchall()
    conn.close()
    return user_data


def select_user_favorite_count():
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT * FROM vk_favorite;
                        """)
            user_data = cur.fetchall()
    conn.close()
    return user_data

def delete_favorite(number_id):
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        DELETE FROM vk_favorite WHERE favorite_id = %s; 
                        """, (number_id,))
    conn.close()
