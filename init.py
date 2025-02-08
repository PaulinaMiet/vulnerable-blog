import sqlite3
from config import DATABASE

with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            secret   TEXT
        )
        '''
    )
    cursor.execute(
        '''
        INSERT INTO users (username, password, secret) VALUES
        ('ania', 'password_1', 'niebieski'),
        ('bartek', 'password_2', 'żółty'),
        ('czarek', 'password_3', 'czerwony');
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
    )
    cursor.execute(
        '''
        INSERT INTO posts (title, content, user_id) VALUES
        ('Mój pierwszy projekt we Flasku', 'Właśnie stworzyłem swoją pierwszą aplikację we Flasku i jest świetna!', 1),
        ('Zrozumieć złączenia SQL', 'Złączenia SQL mogą być trudne, ale oto prosty przewodnik...', 2),
        ('Dlaczego kocham Pythona', 'Python to mój ulubiony język programowania, ponieważ...', 3),
        ('Flask vs Django: Co wybrać?', 'Porównajmy Flaska i Django w kontekście tworzenia stron internetowych...', 1),
        ('SQLite dla początkujących', 'Oto dlaczego SQLite jest świetnym wyborem dla małych projektów...', 2);
        '''
    )
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
    )
    cursor.execute('''
        INSERT INTO comments (content, user_id, post_id) VALUES
        ('Świetna robota! Ja też zaczynałem od Flaska.', 2, 1),
        ('To naprawdę pomogło mi zrozumieć złączenia, dzięki!', 1, 2),
        ('Python jest niesamowity! Jaka jest Twoja ulubiona funkcja?', 2, 3),
        ('Django bardziej nadaje się do większych projektów.', 3, 4),
        ('Bardzo pomocny wpis! Dzięki za podzielenie się.', 1, 5),
        ('Uwielbiam SQLite za jego prostotę.', 3, 5);
        '''
    )
    conn.commit()