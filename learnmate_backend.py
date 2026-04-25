from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DATABASE = 'learnmate.db'

# Helper to connect DB
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB
def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            password TEXT,
            role TEXT CHECK(role IN ('student', 'faculty')),
            name TEXT,
            email TEXT,
            branch TEXT,
            year INTEGER
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS doubts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            doubt TEXT,
            answer TEXT,
            resolved_by TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            filename TEXT
        )''')
        db.commit()

@app.route('/')
def index():
    return jsonify({"msg": "LearnMate Backend Running"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get("user_id")
    password = data.get("password")

    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE user_id=? AND password=?", (user_id, password)).fetchone()
        
        if user:
            return jsonify({
                "status": "success",
                "role": user["role"],
                "name": user["name"],
                "branch": user["branch"],
                "year": user["year"]
            }), 200
        else:
            return jsonify({"status": "fail", "msg": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        with get_db() as db:
            db.execute("""
                INSERT INTO users (user_id, password, role, name, email, branch, year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data['user_id'],
                data['password'],
                data['role'],
                data['name'],
                data['email'],
                data['branch'],
                data['year']
            ))
            db.commit()
        return jsonify({"status": "success"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "fail", "msg": "User already exists"}), 409

@app.route('/ask_doubt', methods=['POST'])
def ask_doubt():
    data = request.json
    with get_db() as db:
        db.execute("INSERT INTO doubts (user_id, doubt, answer, resolved_by) VALUES (?, ?, '', '')", 
                   (data["user_id"], data["doubt"]))
        db.commit()
    return jsonify({"status": "submitted"}), 200

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    file = request.files["file"]
    title = request.form.get("title")
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        with get_db() as db:
            db.execute("INSERT INTO materials (title, filename) VALUES (?, ?)", (title, file.filename))
            db.commit()
        return jsonify({"status": "uploaded"}), 200
    return jsonify({"status": "failed"}), 400

@app.route('/get_materials', methods=['GET'])
def get_materials():
    with get_db() as db:
        rows = db.execute("SELECT * FROM materials").fetchall()
        materials = [{"title": row["title"], "filename": row["filename"]} for row in rows]
    return jsonify(materials), 200

@app.route('/download/<filename>')
def download_pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)