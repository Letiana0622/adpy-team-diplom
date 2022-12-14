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
                        vk_user_id INTEGER NOT NULL REFERENCES vk_selected(vk_user_id)
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

def add_favorite(favorite_id):
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            user_id = favorite_id
            cur.execute("""
                        INSERT INTO vk_favorite(vk_user_id) VALUES
                        (%s)
                        RETURNING favorite_id, vk_user_id;
                        """, (user_id,))
            conn.commit()
    conn.close()
