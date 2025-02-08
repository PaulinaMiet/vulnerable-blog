import sqlite3
import argon2
from flask import Flask, render_template, make_response, request, redirect, url_for, flash, session, g, abort 

from config import DATABASE, SECRET_KEY, SQL_INJECTION, XSS_INJECTION, SECRET_ACCESS, UNSIGNED_COOKIES, PLAIN_PASSWORDS

app = Flask(__name__)
app.secret_key = SECRET_KEY

ph = argon2.PasswordHasher()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/error')
def error():
    raise Exception("Nastąpił błąd")

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    cursor = get_db().cursor()
    if SQL_INJECTION:
        cursor.execute(
            f'''
            SELECT posts.id, posts.title, posts.content, users.username 
            FROM posts JOIN users ON posts.user_id = users.id 
            WHERE title LIKE '%{search_query}%' OR content LIKE '%{search_query}%'
            ORDER BY posts.id DESC
            ''',
        )
    else:
        cursor.execute(
            '''
            SELECT posts.id, posts.title, posts.content, users.username 
            FROM posts JOIN users ON posts.user_id = users.id 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY posts.id DESC
            ''',
            (f"%{search_query}%", f"%{search_query}%")
        )
    posts = cursor.fetchall()
    return render_template('index.html', posts=posts, search_query=search_query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if PLAIN_PASSWORDS:
            hash = password
        else:
            hash = ph.hash(password)
        secret = request.form['secret']
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('INSERT INTO users (username, password, secret) VALUES (?, ?, ?)', (username, hash, secret))
            db.commit()
            flash('Rejestracja pomyślna. Zaloguj się.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Taki użytkownik już istnieje.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    def verify(hash, password):
        if PLAIN_PASSWORDS:
            return hash == password
        else:
            try:
                return ph.verify(hash, password)
            except:
                return False

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_db().cursor()
        cursor.execute('SELECT id, username, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and verify(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Pomyślnie zalogowano.')
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('user_id', str(user['id']))
            return resp
        else:
            flash('Niepoprawna nazwa użytkownika lub hasło.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Zostałeś wylogowany.')
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('user_id')
    return resp

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if UNSIGNED_COOKIES:
        user_id = int(request.cookies.get('user_id'))
    else:
        user_id = session.get('user_id')

    if user_id is None:
        flash('Musisz być zalogowany, żeby dodać posta.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)', (title, content, user_id))
        db.commit()
        flash('Post utworzony pomyślnie.')
        return redirect(url_for('index'))
    
    return render_template('create_post.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    if UNSIGNED_COOKIES:
        user_id = int(request.cookies.get('user_id'))
    else:
        user_id = session.get('user_id')

    cursor = get_db().cursor()
    cursor.execute(
        '''
        SELECT posts.id, posts.title, posts.content, users.username 
        FROM posts JOIN users ON posts.user_id = users.id WHERE posts.id = ?
        ''', 
        (post_id,)
    )
    post = cursor.fetchone()
    
    cursor.execute(
        '''
        SELECT comments.content, users.username 
        FROM comments JOIN users ON comments.user_id = users.id 
        WHERE comments.post_id = ?
        ORDER BY comments.id DESC
        ''', 
        (post_id,)
    )
    comments = cursor.fetchall()

    if request.method == 'POST':
        if user_id is None:
            flash('Musisz być zalogowany, żeby komentować.')
            return redirect(url_for('login'))
        
        comment_content = request.form['comment']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO comments (content, post_id, user_id) VALUES (?, ?, ?)', 
                        (comment_content, post_id, user_id))
        db.commit()
        flash('Pomyślnie zamieszczono komentarz.')
        return redirect(url_for('post_detail', post_id=post_id))

    return render_template('post_detail.html', post=post, comments=comments, injection=XSS_INJECTION)

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    if UNSIGNED_COOKIES:
        true_user_id = int(request.cookies.get('user_id'))
    else:
        true_user_id = session.get('user_id')

    if not SECRET_ACCESS:
        if true_user_id is None or true_user_id != user_id:
            abort(401)

    cursor = get_db().cursor()
    cursor.execute(
        '''
        SELECT username, secret FROM users 
        WHERE id = ?
        ''',
        (user_id,)
    )
    user = cursor.fetchone()
    cursor.execute(
        '''
        SELECT posts.id, posts.title, posts.content, 'post' AS type FROM posts 
        WHERE posts.user_id = ?
        UNION
        SELECT comments.post_id, posts.title, comments.content, 'comment' AS type FROM comments
        JOIN posts ON comments.post_id = posts.id
        WHERE comments.user_id = ?
        ORDER BY id DESC
        ''',
        (user_id, user_id)
    )
    user_activity = cursor.fetchall()
    return render_template(
        'user_profile.html',
        user=user,
        user_activity=user_activity,
    )