from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import sqlite3
import os
import random
import json
from datetime import datetime

print("Starting the Flask application...")

app = Flask(__name__)
app.secret_key = 'secret_key'  # Change this to a random secret key!
ADMIN_PASSWORD = 'album_materials'    #admin password here
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TableOfFailures.db')

# --- Database helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form.get('failure')
        if content:
            db = get_db()
            db.execute('INSERT INTO submissions (content) VALUES (?)', (content,))
            db.commit()
            # If AJAX, return JSON, else redirect
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']:
                return jsonify(success=True)
            return redirect(url_for('index'))
        # If no content, return error for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']:
            return jsonify(success=False), 400
    return render_template('index.html')

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    db = get_db()
    cur = db.execute('SELECT id, content, timestamp FROM submissions ORDER BY timestamp DESC')
    submissions = cur.fetchall()
    return render_template('admin.html', submissions=submissions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Incorrect password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/world')
def world():
    cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'world_cache.json')
    today = datetime.now().strftime('%Y-%m-%d')
    submissions = None
    # Try to load cache
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            try:
                cache = json.load(f)
                if cache.get('date') == today:
                    submissions = cache.get('submissions')
            except Exception:
                pass
    # If no valid cache, pick new random submissions and cache them
    if not submissions:
        db = get_db()
        cur = db.execute('SELECT content, timestamp FROM submissions')
        all_submissions = cur.fetchall()
        if len(all_submissions) > 10:
            picked = random.sample(all_submissions, 10)
        else:
            picked = all_submissions
        # Convert to list of lists for JSON serialization
        submissions = [list(row) for row in picked]
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'date': today, 'submissions': submissions}, f, ensure_ascii=False)
    return render_template('world.html', submissions=submissions)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
