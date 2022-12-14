import psycopg2

def create_db(conn):
    cur.execute("""
                DROP TABLE vk_photo;
                DROP TABLE vk_favorite;
                DROP TABLE vk_selected;
                """)
    conn.commit()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS vk_selected(
                user_id SERIAL PRIMARY KEY,
                vk_user_id INTEGER NOT NULL UNIQUE
                );
                """)
    conn.commit()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS vk_photo(
                photo_id SERIAL PRIMARY KEY,
                vk_user_id INTEGER NOT NULL REFERENCES vk_selected(vk_user_id),
                photo_link TEXT NOT NULL,
                photo_likes INTEGER NOT NULL
                );
                """)
    conn.commit()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS vk_favorite(
                favorite_id SERIAL PRIMARY KEY,
                vk_user_id INTEGER NOT NULL REFERENCES vk_selected(vk_user_id)
                );
                """)
    conn.commit()

# по комментариям записываем в таблицу только 1 ИД/1й - необходимо доработать в основных модулях
def add_user(conn, vk_user_id):
    cur.execute("""
                INSERT INTO vk_selected(vk_user_id) VALUES
                (%s)
                RETURNING user_id, vk_user_id;
                """, (vk_user_id,))
    conn.commit()

def add_photo(conn,user_id, photo_url, photo_likes):
    cur.execute("""
                INSERT INTO vk_photo(vk_user_id, photo_link, photo_likes) VALUES
                (%s,%s,%s)
                RETURNING photo_id, vk_user_id, photo_link, photo_likes;
                """, (user_id, photo_url, photo_likes,))
    conn.commit()

def add_favorite(conn,favorite_id):
    user_id = favorite_id
    cur.execute("""
                INSERT INTO vk_favorite(vk_user_id) VALUES
                (%s)
                RETURNING favorite_id, vk_user_id;
                """, (user_id,))
    conn.commit()

if __name__ == "__main__":
    with psycopg2.connect(database="vk_bot_db", user="postgres", password="postgres") as conn:
        with conn.cursor() as cur:
            create_db(conn)
            add_user(conn, vk_user_id)
            add_photo(conn, user_id, photo_url, photo_likes)
            add_favorite(conn, favorite_id)
    conn.close()