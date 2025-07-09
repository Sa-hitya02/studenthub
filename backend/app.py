from flask import Flask, render_template, request, redirect, url_for, session
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# App setup
app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")
CORS(app)

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI not set in .env file")

client = MongoClient(mongo_uri)
db = client["studenthub"]

# Collections
users = db["users"]
posts = db["posts"]
assignments = db["assignments"]
events = db["events"]

# ------------------ AUTH ------------------

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if users.find_one({"email": email}):
            return "User already exists!"
        
        users.insert_one({"email": email, "password": password})
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = users.find_one({"email": email, "password": password})
        if user:
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------ DASHBOARD ------------------

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))

    return render_template("dashboard.html",
        email=session['email'],
        posts=list(posts.find({}, {"_id": 0})),
        assignments=list(assignments.find({}, {"_id": 0})),
        events=list(events.find({}, {"_id": 0}))
    )

@app.route('/add-post', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']
    posts.insert_one({
        "title": title,
        "content": content,
        "created_by": session['email'],
        "created_at": datetime.utcnow().isoformat()
    })
    return redirect(url_for('dashboard'))

@app.route('/add-assignment', methods=['POST'])
def add_assignment():
    title = request.form['title']
    deadline = request.form['deadline']
    assignments.insert_one({
        "title": title,
        "deadline": deadline,
        "created_by": session['email'],
        "created_at": datetime.utcnow().isoformat()
    })
    return redirect(url_for('dashboard'))

@app.route('/add-event', methods=['POST'])
def add_event():
    title = request.form['title']
    date = request.form['date']
    description = request.form['description']
    events.insert_one({
        "title": title,
        "date": date,
        "description": description,
        "created_by": session['email'],
        "created_at": datetime.utcnow().isoformat()
    })
    return redirect(url_for('dashboard'))

# ------------------ PROFILE ------------------

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('login'))
    try:
        return render_template("profile.html",
            email=session['email'],
            posts=list(posts.find({"created_by": session['email']})),
            assignments=list(assignments.find({"created_by": session['email']})),
            events=list(events.find({"created_by": session['email']}))
        )
    except Exception as e:
        return f"Error loading profile: {str(e)}", 500

# ------------------ EVENTS PAGE ------------------

@app.route('/events')
def events_page():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template("events.html")

# ------------------ SERVER ------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
